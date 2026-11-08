import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercice 6 : évaluer")

with app.setup(hide_code=True):
    from collections import Counter

    import marimo as mo

    import checks
    from course import DATA, OUTPUT, ask, read_csv


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercice 6 : évaluer


    D'abord lire les erreurs et les nommer, ensuite mesurer.

    1. Lire les lignes fausses, nommer chaque échec
    2. Compter les types d'échec, puis l'accuracy par champ
    3. Un second modèle comme juge, contrôlé avec vos propres étiquettes
    """)
    return


@app.cell(hide_code=True)
def _():
    sources = {"un petit modèle (llama3.2:3b)": DATA / "extraction_reference.csv"}
    if (OUTPUT / "extraction.csv").exists():
        sources["votre extraction (exercice 5)"] = OUTPUT / "extraction.csv"
    source = mo.ui.dropdown(sources, value="un petit modèle (llama3.2:3b)", label="extraction à évaluer")
    source
    return (source,)


@app.cell(hide_code=True)
def _(source):
    extracted = {row["id"]: row for row in read_csv(source.value)}
    truth = {row["id"]: row for row in read_csv(DATA / "ground_truth.csv")}
    mo.md(f"Vérité de référence : {len(truth)} résumés, écrite par une personne. Un grand modèle n'a fait aucune erreur sur ceux-ci dans notre test : commencez par le petit modèle")
    return extracted, truth


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Lire et nommer

    > **L'idée :** avant de mesurer, lire les erreurs et leur donner un nom (slide "Lire les erreurs, comme pour MNIST")

    Les lignes où un champ exact est faux. La `note` de la vérité de référence donne la raison.
    """)
    return


@app.cell(hide_code=True)
def _(extracted, truth):
    EXACT = ["sample_size", "study_design", "effect_found"]
    wrong = [
        {"id": item_id, "field": field, "extracted": extracted[item_id].get(field, ""), "right": truth[item_id][field], "note": truth[item_id]["note"]}
        for item_id in truth if item_id in extracted
        for field in EXACT if str(extracted[item_id].get(field, "")).strip().lower() != truth[item_id][field].strip().lower()
    ]
    mo.ui.table(wrong[:5], selection=None)
    return EXACT, wrong


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Donnez un nom court à chaque ligne fausse** : quel type d'échec est-ce ? Par exemple "clusters comptés au lieu des personnes".
    """)
    return


@app.cell(hide_code=True)
def _(wrong):
    failure = mo.ui.dictionary({f"{row['id']} {row['field']}": mo.ui.text(placeholder="type d'échec", full_width=True) for row in wrong[:5]})
    failure
    return (failure,)


@app.cell(hide_code=True)
def _(failure):
    checks.ex6_names(failure.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    /// details | Question
    Quelles lignes ont le même problème ?
    ///

    ## 2 · Compter, puis mesurer

    > **L'idée :** l'accuracy dit combien d'erreurs, les types d'échec disent quoi corriger (slide "Que mesurer ?")
    """)
    return


@app.cell(hide_code=True)
def _(failure):
    counts = Counter(failure.value.values())
    mo.ui.table([{"type d'échec": name, "lignes": count} for name, count in counts.most_common() if name], selection=None)
    return


@app.cell(hide_code=True)
def _(EXACT):
    field = mo.ui.dropdown(EXACT, value="sample_size", label="champ")
    field
    return (field,)


@app.cell(hide_code=True)
def _(extracted, field, truth):
    right = sum(str(extracted[item_id].get(field.value, "")).strip().lower() == truth[item_id][field.value].strip().lower() for item_id in truth if item_id in extracted)
    mo.md(f"**{field.value} : {right} / {len(truth)} justes**")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - L'accuracy dit *combien de fois* ; la liste des échecs dit *quoi corriger*
    - Ces 10 lignes sont un dev set : on les regarde et on change le prompt. Un vrai test set reste fermé jusqu'à la fin, comme dans le module ML

    /// details | Question
    Laquelle vous dit comment changer le prompt ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Un juge pour un type d'échec

    > **L'idée :** un LLM juge est un classifieur. Vérifiez qu'il est d'accord avec vous avant de lui faire confiance (slide "Le juge est un classifieur : testez-le")

    Le champ `main_result` est du texte libre : un programme ne peut pas le comparer mot à mot. Un second modèle (Gemini) le juge.

    **D'abord, étiquetez 5 lignes vous-même** : cochez une ligne quand le résultat extrait est bon.
    """)
    return


@app.cell(hide_code=True)
def _(extracted, truth):
    sample = [item_id for item_id in truth if item_id in extracted][:5]
    mo.ui.table([{"id": item_id, "extrait": extracted[item_id].get("main_result", ""), "vérité de référence": truth[item_id]["main_result"]} for item_id in sample], selection=None)
    return (sample,)


@app.cell(hide_code=True)
def _(sample):
    my_label = mo.ui.dictionary({item_id: mo.ui.checkbox(label="bon") for item_id in sample})
    my_label
    return (my_label,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Changez une ligne de la grille**, puis appuyez sur le bouton. Objectif : un juge d'accord avec vous.
    """)
    return


@app.cell(hide_code=True)
def _():
    rubric = mo.ui.text_area(
        value="""Does the extracted result state the primary outcome and its direction, as the ground truth does?
Give your reason in one sentence first. Then, on the last line, write only PASS or FAIL.""",
        full_width=True,
    )
    judge_now = mo.ui.run_button(label="Demander au juge")
    mo.vstack([rubric, judge_now])
    return judge_now, rubric


@app.cell(hide_code=True)
def _(extracted, judge_now, my_label, rubric, sample, truth):
    mo.stop(not judge_now.value, mo.md("Appuyez sur **Demander au juge**."))
    verdicts = {}
    for item_id in sample:
        reply, _ = ask(f"{rubric.value}\n\nGround truth: {truth[item_id]['main_result']}\nExtracted: {extracted[item_id].get('main_result', '')}", "judge", temperature=0)
        verdicts[item_id] = reply.strip().splitlines()[-1].strip().upper().startswith("PASS")
    failures = [item_id for item_id in sample if not my_label.value[item_id]]
    good = [item_id for item_id in sample if my_label.value[item_id]]
    mo.vstack([
        mo.md(f"**Le juge a détecté {sum(not verdicts[i] for i in failures)} échec(s) sur {len(failures)}, validé {sum(verdicts[i] for i in good)} bonne(s) réponse(s) sur {len(good)}**"),
        mo.ui.table([{"id": i, "vous": "bon" if my_label.value[i] else "échec", "juge": "PASS" if verdicts[i] else "FAIL"} for i in sample], selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **À retenir**

    - Lire, nommer, compter : ensuite mesurer
    - Un juge est un test que vous devez tester
    - 10 lignes, c'est peu : une vraie analyse d'erreurs en lit environ 100

    /// details | Question
    Trouvez une ligne où le juge et vous n'êtes pas d'accord. Qui a raison ?
    ///

    ---
    ## Option

    La recherche de l'exercice 4 : ouvrez son option et comparez hit@3 pour k = 1, 3, 5 passages.
    """)
    return


if __name__ == "__main__":
    app.run()
