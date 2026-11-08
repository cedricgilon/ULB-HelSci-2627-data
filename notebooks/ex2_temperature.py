import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercice 2 : local vs API, température")

with app.setup(hide_code=True):
    import marimo as mo

    from course import ask, normalise


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercice 2 : local vs API, température


    1. Sur le web : la température dans Vittascience
    2. La même question, sur votre portable et sur l'API
    3. La même question, 5 fois, à une température que vous choisissez

    Option, si vous finissez plus tôt : demander des références, puis les vérifier.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Sur le web

    > **L'idée :** le modèle tire chaque token au hasard, selon les probabilités. Le même prompt peut donner une autre réponse (slide "Même prompt, même réponse ?")

    Ouvrez <https://fr.vittascience.com/ia/text>.

    - Écrivez un prompt. Lancez-le 3 fois avec un hasard bas, puis 3 fois avec un hasard élevé
    - Activez l'affichage des tokens et de leurs ids

    /// details | Question
    Où tourne ce modèle : sur votre portable ou sur un serveur ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Local ou API

    > **L'idée :** le même genre de modèle tourne sur votre portable ou chez un fournisseur. Le temps de réponse change, et l'endroit où vont vos données aussi

    **Choisissez** où tourne le modèle, puis appuyez sur le bouton. Posez la question une fois avec chacun.
    Le modèle local peut prendre 30 à 60 s sur un portable sans GPU.
    """)
    return


@app.cell(hide_code=True)
def _():
    prompt = mo.ui.text_area(
        value="What is the most common side effect of metformin? Answer in two words.", full_width=True
    )
    where = mo.ui.dropdown({"local (Ollama, llama3.2:3b)": "local", "API (Groq, gpt-oss-20b)": "api"}, value="local (Ollama, llama3.2:3b)")
    ask_once = mo.ui.run_button(label="Demander au modèle")
    mo.vstack([prompt, mo.hstack([where, ask_once], justify="start")])
    return ask_once, prompt, where


@app.cell(hide_code=True)
def _(ask_once, prompt, where):
    mo.stop(not ask_once.value, mo.md("Appuyez sur **Demander au modèle**."))
    answer, seconds = ask(prompt.value, where.value, temperature=0)
    mo.md(f"**{seconds:.1f} s** · {answer}")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Local : plus lent sans GPU ; le texte reste sur votre portable
    - API : rapide ; le texte part chez le fournisseur

    /// details | Question
    Vous travaillez avec des notes de patients. Lequel choisissez-vous, et pourquoi ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Température

    > **L'idée :** la température règle le hasard du tirage. Basse : presque toujours le token le plus probable. Haute : plus de variété (slide "Température")

    La même question, 5 fois, sur l'API. Combien de réponses **différentes** ?

    **Prédisez d'abord**, avant d'appuyer sur le bouton.
    """)
    return


@app.cell(hide_code=True)
def _():
    guess_low = mo.ui.number(start=1, stop=5, value=1, label="réponses différentes à la température 0")
    guess_high = mo.ui.number(start=1, stop=5, value=1, label="réponses différentes à la température 1,5")
    mo.vstack([guess_low, guess_high])
    return guess_high, guess_low


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Changez** la température, puis appuyez sur le bouton. Objectif : vérifier vos deux prédictions, puis trouver une température où les 5 réponses sont différentes.
    """)
    return


@app.cell(hide_code=True)
def _():
    temperature = mo.ui.slider(0, 1.5, step=0.1, value=0, label="température", show_value=True)
    ask_five = mo.ui.run_button(label="Demander 5 fois")
    mo.hstack([temperature, ask_five], justify="start")
    return ask_five, temperature


@app.cell(hide_code=True)
def _(ask_five, guess_high, guess_low, prompt, temperature):
    mo.stop(not ask_five.value, mo.md("Appuyez sur **Demander 5 fois**."))
    answers = [ask(prompt.value, "api", temperature.value)[0] for _ in range(5)]
    different = len({normalise(answer) for answer in answers})
    mo.vstack([
        mo.md(f"**{different} réponse(s) différente(s)** à la température {str(temperature.value).replace('.', ',')}. "
              f"Vos prédictions : {guess_low.value} à 0, {guess_high.value} à 1,5"),
        mo.ui.table([{"réponse": answer} for answer in answers], selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **À retenir**

    - La température change la variété des réponses, pas leur vérité
    - À température 0, une API peut encore donner une autre réponse : votre requête passe dans un lot avec d'autres
    - Température basse pour l'extraction et le code, plus haute pour les idées et les brouillons
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option · Des références inventées

    1. Dans la boîte de la partie 2, demandez : *"Give 3 peer-reviewed articles on (a narrow topic you know well), with authors, year, title, journal and DOI."* Demandez au modèle local et à l'API
    2. Demandez la même chose dans une application de chat avec la recherche web activée. A-t-elle cherché ?
    3. Vérifiez chaque référence :
        - ouvrez `https://doi.org/` + le DOI : même titre ? même premier auteur ? Un DOI qui s'ouvre n'est pas une preuve
        - sinon, cherchez le titre dans PubMed, puis dans Crossref
        - trouvé : lisez le résumé. Dit-il ce que le modèle a dit ?
    4. Donnez une étiquette à chacune : correcte / réelle avec des erreurs / réelle mais hors sujet / inventée

    /// details | Question
    Notre API et nos modèles locaux n'ont pas de recherche web. Qu'attendez-vous d'eux ?
    ///
    """)
    return


if __name__ == "__main__":
    app.run()
