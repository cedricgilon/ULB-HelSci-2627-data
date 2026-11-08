import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercice 1 : tokens")

with app.setup(hide_code=True):
    import marimo as mo
    import tiktoken

    import checks
    from course import next_tokens, pieces

    o200k = tiktoken.get_encoding("o200k_base")  # modèles OpenAI récents, ~200 000 tokens
    gpt2 = tiktoken.get_encoding("gpt2")


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercice 1 : tokens

    Pas d'API : tout tourne sur votre portable.

    Un modèle ne lit pas des mots. Il lit des **tokens** : des morceaux de texte, chacun avec un numéro entier (id).

    1. Sur le web : voir les tokens
    2. Une phrase, cinq langues
    3. Des mots de votre domaine, et le coût

    Option, si vous finissez plus tôt : le token suivant, avec un petit modèle.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Sur le web

    > **L'idée :** un modèle ne lit pas des mots mais des tokens, chacun avec un numéro (slide "Un modèle lit des tokens, pas des mots")

    Ouvrez <https://tiktokenizer.vercel.app/> et choisissez `o200k_base`.

    - Tapez une phrase en anglais, puis la même phrase en français. Comptez les tokens.
    - Tapez un mot de votre domaine : une molécule, une maladie, une technique de labo.

    /// details | Question
    Quel mot est coupé en le plus de morceaux ? Pourquoi ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Une phrase, cinq langues

    > **L'idée :** le vocabulaire est appris surtout sur de l'anglais. À sens égal, une autre langue peut demander plus de tokens (slide "Un vocabulaire fixe")

    La même phrase en cinq langues. **Ajoutez votre langue** : une ligne de plus dans le dictionnaire.
    """)
    return


@app.cell
def _():
    sentences = {
        "English": "The patient was given a low dose of aspirin to reduce the risk of a heart attack.",
        "French": "On a donné au patient une faible dose d'aspirine pour réduire le risque de crise cardiaque.",
        "Dutch": "De patiënt kreeg een lage dosis aspirine om het risico op een hartaanval te verminderen.",
        "German": "Der Patient erhielt eine niedrige Dosis Aspirin, um das Risiko eines Herzinfarkts zu senken.",
        "Arabic": "أُعطي المريض جرعة منخفضة من الأسبرين لتقليل خطر الإصابة بنوبة قلبية.",
    }
    return (sentences,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    `encode` découpe un texte en tokens et donne leurs numéros :
    """)
    return


@app.cell
def _():
    o200k.encode("The patient was given aspirin")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Écrivez une ligne** : la fonction donne le nombre de tokens d'un texte. `encoding` est le tokenizer : `o200k` ou `gpt2`.
    """)
    return


@app.function
def count_tokens(encoding, text):
    """Le nombre de tokens de text."""
    ...  # TODO


@app.cell(hide_code=True)
def _():
    checks.ex1_count(count_tokens)
    return


@app.cell(hide_code=True)
def _():
    mo.accordion({"💡 Indice": mo.md("`len(une_liste)` donne le nombre d'éléments d'une liste.")})
    return


@app.cell(hide_code=True)
def _(sentences):
    english = count_tokens(o200k, sentences["English"])
    mo.ui.table(
        [
            {
                "langue": language,
                "o200k (2024)": count_tokens(o200k, text),
                "gpt2 (2019)": count_tokens(gpt2, text),
                "vs anglais": f"{count_tokens(o200k, text) / english - 1:+.0%}" if english else "",
            }
            for language, text in sentences.items()
        ],
        selection=None,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Même sens, nombre de tokens différent.
    - Le tokenizer plus ancien, `gpt2`, a été construit sur un texte surtout anglais.

    /// details | Question
    Les prix des API sont par token. Qu'est-ce que cela veut dire pour un prompt en français ou en arabe ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Des mots de votre domaine, et le coût

    > **L'idée :** un mot rare est découpé en plusieurs tokens, et l'API facture au token (slide "Les mots rares sont découpés")

    **Changez la liste** : trois mots de votre domaine.
    """)
    return


@app.cell
def _():
    my_terms = ["pharmacokinetics", "acetylsalicylic acid", "glomerular filtration rate"]
    return (my_terms,)


@app.cell(hide_code=True)
def _(my_terms):
    mo.md("\n".join(f"- `{term}` → `{pieces(o200k, term)}`" for term in my_terms))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Le modèle ne voit jamais les lettres d'un mot, seulement ses morceaux.

    **Trouvez le prix** de `openai/gpt-oss-20b` chez Groq : tokens en entrée, USD par million.
    Cherchez sur <https://console.groq.com/docs/models>
    """)
    return


@app.cell(hide_code=True)
def _():
    price = mo.ui.number(start=0, stop=100, step=0.005, value=0, label="USD par million de tokens en entrée")
    price
    return (price,)


@app.cell(hide_code=True)
def _(price):
    checks.ex1_price(price.value)
    return


@app.cell(hide_code=True)
def _(price, sentences):
    print(f"Price: {price.value}")
    mo.ui.table(
        [
            {
                "langue": language,
                "tokens": count_tokens(o200k, text),
                "USD pour un million de phrases": round((count_tokens(o200k, text) or 0) * price.value, 2),
            }
            for language, text in sentences.items()
        ],
        selection=None,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **À retenir**

    - Même sens, coût différent : une langue peu vue par le tokenizer coûte plus.
    - Les mots techniques sont coupés en beaucoup de morceaux.
    - La context window se compte aussi en tokens.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option · Le token suivant

    `distilgpt2` est un petit modèle : 82 millions de paramètres. Ce n'est pas un modèle de chat.
    Pour un texte, il donne une probabilité à chacun de ses 50 257 tokens d'être le suivant.

    La première fois que vous appuyez sur le bouton, le modèle est téléchargé : environ 350 Mo.
    """)
    return


@app.cell(hide_code=True)
def _():
    start = mo.ui.text(value="The patient was given a dose of", full_width=True)
    predict = mo.ui.run_button(label="Token suivant")
    mo.vstack([start, predict])
    return predict, start


@app.cell(hide_code=True)
def _(predict, start):
    mo.stop(not predict.value, mo.md("Appuyez sur **Token suivant**."))
    mo.ui.table(
        [{"token suivant": repr(token), "probabilité": f"{p:.1%}"} for token, p in next_tokens(start.value)],
        selection=None,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - **Faites le sampling vous-même** : copiez un des cinq tokens à la fin du texte, appuyez de nouveau sur le bouton. Faites-le cinq fois.
    - Le texte est une chaîne de choix locaux. Pas de plan, pas de vrai ou faux : seulement du probable.
    """)
    return


if __name__ == "__main__":
    app.run()
