import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercice 5 : extraction structurée")

with app.setup(hide_code=True):
    import json
    from typing import Literal

    import marimo as mo
    from pydantic import BaseModel, ValidationError

    import checks
    from course import OUTPUT, abstracts, ask_json, write_csv


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercice 5 : extraction structurée


    20 résumés d'études cliniques. L'objectif : un tableau qu'un programme peut utiliser.

    1. Un résumé : un prompt, le mode JSON, un dict
    2. Contrôler les champs et leurs types avec `pydantic`
    3. Les 20 résumés : un tableau et un fichier CSV

    Option, si vous finissez plus tôt : un schéma strict, ou un champ `confidence`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Un résumé

    > **L'idée :** un programme a besoin de champs fixes, pas de phrases : on demande un JSON (slide "Un programme lit des champs, pas des phrases")

    **Complétez le prompt** : un champ de la liste manque. Utilisez les valeurs permises ci-dessous.
    """)
    return


@app.cell(hide_code=True)
def _():
    DESIGNS = ["randomised controlled trial", "cluster randomised trial", "crossover trial", "secondary analysis of a trial", "cross-sectional study"]
    EFFECTS = ["yes", "no", "mixed", "not applicable"]
    mo.md(f"`study_design`: {', '.join(DESIGNS)} · `effect_found`: {', '.join(EFFECTS)}")
    return DESIGNS, EFFECTS


@app.cell(hide_code=True)
def _():
    fields = mo.ui.text_area(
        value="""Extract these fields from the abstract, as a JSON object:
- population: who was studied (text)
- intervention: what was tested, and against what (text)
- sample_size: number of participants (integer)
- effect_found: a significant benefit on the primary outcome? one of: yes, no, mixed, not applicable
- main_result: the main result, in one sentence (text)""",
        full_width=True,
        rows=8,
    )
    fields
    return (fields,)


@app.cell(hide_code=True)
def _(fields):
    checks.ex5_fields(fields.value)
    return


@app.cell(hide_code=True)
def _():
    corpus = {item["id"]: item["text"] for item in abstracts()}
    abstract_id = mo.ui.dropdown(list(corpus), value="A01", label="résumé")
    extract_one = mo.ui.run_button(label="Extraire")
    mo.hstack([abstract_id, extract_one], justify="start")
    return abstract_id, corpus, extract_one


@app.cell(hide_code=True)
def _(abstract_id, corpus, extract_one, fields):
    mo.stop(not extract_one.value, mo.md("Appuyez sur **Extraire**."))
    raw, seconds = ask_json("You extract structured data from abstracts of clinical studies.", f"{fields.value}\n\n<abstract>\n{corpus[abstract_id.value]}\n</abstract>")
    mo.vstack([mo.md(f"*{seconds:.1f} s*"), mo.json(json.loads(raw))])
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Mode JSON : l'API renvoie un JSON valide
    - Il ne promet ni vos champs, ni les bonnes valeurs

    /// details | Question
    Comparez avec le résumé. Chaque valeur est-elle juste ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Contrôler avec pydantic

    > **L'idée :** un JSON valide peut contenir une valeur du mauvais type. Un schéma pydantic la rejette (slide "`pydantic` : un formulaire avec des champs typés")

    **Écrivez une ligne** : le champ `sample_size`, un entier.
    """)
    return


@app.cell
def _():
    class Extraction(BaseModel):
        population: str
        intervention: str
        ...  # TODO
        study_design: Literal["randomised controlled trial", "cluster randomised trial", "crossover trial", "secondary analysis of a trial", "cross-sectional study"]
        effect_found: Literal["yes", "no", "mixed", "not applicable"]
        main_result: str
    return (Extraction,)


@app.cell(hide_code=True)
def _(Extraction):
    checks.ex5_model(Extraction)
    return


@app.cell(hide_code=True)
def _(Extraction):
    bad = '{"population": "adults", "intervention": "metformin", "sample_size": "about 250", "study_design": "trial", "effect_found": "yes", "main_result": "..."}'
    try:
        Extraction.model_validate_json(bad)
        verdict = "acceptée"
    except ValidationError as error:
        verdict = f"rejetée :\n\n```\n{error}\n```"
    mo.md(f"Une mauvaise réponse est {verdict}")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Le contrôle rejette un mauvais type ou une valeur hors de la liste, avec la raison
    - Un JSON valide avec le mauvais nombre reste faux : "87,449 women" peut devenir 87

    /// details | Question
    Votre extraction de la partie 1 passe-t-elle le contrôle ? Essayez `Extraction.model_validate_json(raw)`.
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Les 20 résumés

    > **L'idée :** le contrôle trouve les réponses mal formées, pas les valeurs fausses (slide "JSON valide, valeur fausse")

    20 appels, l'un après l'autre. L'offre gratuite permet 8 000 tokens par minute : certains appels attendent et réessaient (HTTP 429). Cela prend environ 2 minutes.
    """)
    return


@app.cell(hide_code=True)
def _():
    extract_all = mo.ui.run_button(label="Extraire les 20")
    extract_all
    return (extract_all,)


@app.cell(hide_code=True)
def _(Extraction, corpus, extract_all, fields):
    mo.stop(not extract_all.value, mo.md("Appuyez sur **Extraire les 20**."))
    rows = []
    for item_id, text in mo.status.progress_bar(list(corpus.items()), title="Extraction en cours"):
        answer, _ = ask_json("You extract structured data from abstracts of clinical studies.", f"{fields.value}\n\n<abstract>\n{text}\n</abstract>")
        try:
            rows.append({"id": item_id, **Extraction.model_validate_json(answer).model_dump(), "error": ""})
        except ValidationError as error:
            rows.append({"id": item_id, "error": str(error).splitlines()[0]})
    write_csv(OUTPUT / "extraction.csv", rows)
    mo.vstack([mo.md(f"Enregistré dans `data/output/extraction.csv` : {len(rows)} lignes"), mo.ui.table(rows, selection=None)])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **À retenir**

    - Un tableau qu'un programme peut utiliser, en 2 minutes
    - Demander dans le prompt < mode JSON < validation
    - Certaines valeurs sont fausses : comment les trouver sans lire les 20 ? C'est l'exercice 6

    /// details | Question
    Regardez `sample_size`. Quelles valeurs semblent fausses ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option

    - **Schéma strict** : Groq accepte `response_format={"type": "json_schema", ...}` avec le schéma de `Extraction.model_json_schema()` : l'API renvoie alors vos champs
    - **Confiance** : ajoutez un champ `confidence` (0 à 1) au prompt et à `Extraction`, relancez. Dans l'exercice 6, la confiance prédit-elle les erreurs ?
    """)
    return


if __name__ == "__main__":
    app.run()
