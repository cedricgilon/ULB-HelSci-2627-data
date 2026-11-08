import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercice 7 : petit projet")

with app.setup(hide_code=True):
    import marimo as mo

    import checks
    from course import ask


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercice 7 : petit projet


    Une tâche de votre domaine : partez de l'idée en une ligne d'hier.

    1. La tâche et 5 exemples
    2. Le prompt, lancé sur les 5 exemples
    3. Vérifier à la main, et trois lignes à présenter

    Pas de données personnelles dans les exemples.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · La tâche et 5 exemples

    > **L'idée :** commencer petit : une tâche claire, et quelques exemples dont vous connaissez la réponse (slide "La méthode, toujours la même")

    **Changez la tâche et les exemples.** Des idées, avec des données sans données personnelles :

    - le niveau de triage d'un cas fictif (HELPMed : 10 cas écrits par des médecins)
    - un résumé en langage simple d'un document de l'EMA (`data/rag/`)
    - un tableau à partir de résumés (exercice 5)
    - des vignettes pédagogiques, chaque fait vérifié par une personne
    - une fiche de contexte d'usage pour un outil d'IA en pharma (EMA–FDA, 10 principes)
    """)
    return


@app.cell(hide_code=True)
def _():
    task = mo.ui.text_area(value="Say whether a sentence reports an adverse event: yes or no.", full_width=True)
    task
    return (task,)


@app.cell
def _():
    examples = [
        "After the second dose, the patient developed a rash on both arms.",
        "The patient took the tablets with breakfast, as advised.",
        "She reported dizziness two hours after the injection.",
        "The study enrolled 120 adults with type 2 diabetes.",
        "Three participants stopped treatment because of nausea.",
    ]
    return (examples,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Le prompt

    > **L'idée :** les instructions d'un côté, les données entre balises de l'autre (slide "Données et messages")

    **Écrivez une ligne** : le message pour un exemple, le prompt d'abord, puis l'exemple entre balises `<input>`.
    Avec `make_message("Say yes or no.", "She felt dizzy.")`, le message doit être :

    ```
    Say yes or no.

    <input>
    She felt dizzy.
    </input>
    ```

    Une f-string met une variable dans un texte : `f"Bonjour {name}"`. `\n` est un retour à la ligne.
    """)
    return


@app.cell
def _():
    def make_message(prompt, example):
        """Le prompt, puis l'exemple entre balises <input>."""
        ...  # TODO
    return (make_message,)


@app.cell(hide_code=True)
def _(make_message):
    checks.ex7_message(make_message)
    return


@app.cell(hide_code=True)
def _(task):
    prompt = mo.ui.text_area(value=f"{task.value}\nAnswer with one word.", full_width=True, rows=5)
    run_all = mo.ui.run_button(label="Lancer sur les 5 exemples")
    mo.vstack([prompt, run_all])
    return prompt, run_all


@app.cell(hide_code=True)
def _(examples, make_message, prompt, run_all):
    mo.stop(not run_all.value, mo.md("Appuyez sur **Lancer sur les 5 exemples**."))
    outputs = [ask(make_message(prompt.value, example), "api", temperature=0)[0] for example in examples]
    mo.ui.table([{"exemple": example, "réponse": output} for example, output in zip(examples, outputs)], selection=None)
    return (outputs,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Vérifier à la main, puis trois lignes

    > **L'idée :** mesurer avant de faire confiance, puis dire ce que fait l'outil, son risque et sa mesure (slide "Trois lignes à présenter")

    **Cochez chaque réponse juste.**
    """)
    return


@app.cell(hide_code=True)
def _(outputs):
    right = mo.ui.dictionary({f"exemple {number + 1}": mo.ui.checkbox(label="juste") for number in range(len(outputs))})
    right
    return (right,)


@app.cell(hide_code=True)
def _(right):
    mo.md(f"**{sum(right.value.values())} / {len(right.value)} justes**")
    return


@app.cell(hide_code=True)
def _():
    what = mo.ui.text_area(placeholder="Ce que cela fait", full_width=True)
    risk = mo.ui.text_area(placeholder="Le risque si c'est faux", full_width=True)
    measure = mo.ui.text_area(placeholder="Comment vous le mesurez", full_width=True)
    mo.vstack([what, risk, measure])
    return measure, risk, what


@app.cell(hide_code=True)
def _(measure, risk, what):
    mo.md(f"**Ce que cela fait** : {what.value}\n\n**Risque si c'est faux** : {risk.value}\n\n**Comment nous le mesurons** : {measure.value}")
    return


if __name__ == "__main__":
    app.run()
