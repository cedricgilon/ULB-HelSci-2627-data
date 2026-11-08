import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercice 4 : RAG à la main")

with app.setup(hide_code=True):
    import marimo as mo

    import checks
    from course import ask, embed, rag_index, similarity, test_questions


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercice 4 : RAG à la main


    Les documents : 8 résumés de médicaments de l'EMA, et Narvelia, un médicament qui n'existe pas.

    1. Chercher : trouver les passages les plus proches d'une question
    2. Répondre : mettre les passages dans le prompt
    3. Une question à laquelle les documents ne répondent pas

    Option, si vous finissez plus tôt : la taille des passages compte-t-elle ?
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Chercher

    > **L'idée :** la recherche compare le sens de la question avec le sens de chaque passage, grâce aux embeddings (slide "Similarité cosinus")

    Les documents sont découpés en passages de 150 mots, et chaque passage devient un vecteur de 384 nombres.
    Cette cellule tourne une fois, sur votre portable : rien n'est envoyé.
    """)
    return


@app.cell(hide_code=True)
def _():
    chunks, vectors = rag_index(150)
    mo.md(f"{len(chunks)} passages · matrice de {vectors.shape[0]} × {vectors.shape[1]} nombres")
    return chunks, vectors


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Deux textes à comparer : une question et une phrase.
    """)
    return


@app.cell(hide_code=True)
def _():
    question = mo.ui.text_area(value="How often is Mounjaro injected?", label="`question`", full_width=True)
    sentence = mo.ui.text_area(value="Mounjaro is injected once a week.", label="`sentence`", full_width=True)
    mo.vstack([question, sentence])
    return question, sentence


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    `question.value` est le texte de la boîte `question`. `embed` le transforme en vecteur de 384 nombres. Les 5 premiers :
    """)
    return


@app.cell
def _(question):
    embed(question.value)[:5]
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Écrivez une ligne** : la similarité entre `question.value` et `sentence.value`. `similarity(a, b)` compare deux vecteurs.
    """)
    return


@app.cell
def _(question, sentence):
    score = ...  # TODO
    return (score,)


@app.cell(hide_code=True)
def _(question, score, sentence):
    checks.ex4_score(score, question.value, sentence.value)
    return


@app.cell(hide_code=True)
def _():
    mo.accordion({"💡 Indice": mo.md("`similarity` prend deux vecteurs : `embed(...)` pour chaque texte.")})
    return


@app.cell(hide_code=True)
def _(score):
    mo.stop(score is ..., mo.md("Écrivez d'abord la ligne ci-dessus."))
    mo.md(f"""
    **Score : {score:.2f}.** 1 : le même sens. 0 : aucun rapport.

    **Changez la phrase.** Objectif : un score proche de 0 (un autre sujet), puis un score élevé avec d'autres mots (même sens).
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    La recherche fait la même chose avec chaque passage, puis garde les 3 meilleurs scores.
    """)
    return


@app.cell(hide_code=True)
def _(chunks, question, score, vectors):
    mo.stop(score is ..., mo.md("Écrivez d'abord la ligne ci-dessus."))
    question_vector = embed(question.value)
    scores = [similarity(question_vector, vector) for vector in vectors]
    best = sorted(range(len(chunks)), key=lambda index: scores[index], reverse=True)[:3]
    mo.ui.table(
        [{"score": round(float(scores[index]), 2), "passage": chunks[index]["id"], "texte": chunks[index]["text"][:200] + " …"} for index in best],
        selection=None,
    )
    return (best,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - La recherche tourne sur votre portable, en moins d'une seconde
    - Le passage le plus proche de la question n'est pas toujours celui qui contient la réponse

    **Changez la question.** Objectif : trouver une question où le meilleur passage vient du mauvais médicament.
    Essayez "Which medicines treat chronic kidney disease?" : deux documents contiennent la réponse.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Répondre

    > **L'idée :** le modèle ne connaît pas vos documents. Le programme met les meilleurs passages dans le prompt (slide "Le prompt de réponse")

    **Complétez les instructions** : trois règles. Utiliser seulement les passages. Citer l'id du passage. Si la réponse n'y est pas, le dire.
    """)
    return


@app.cell(hide_code=True)
def _():
    instructions = mo.ui.text_area(value="Answer the question.", full_width=True)
    instructions
    return (instructions,)


@app.cell(hide_code=True)
def _(instructions):
    checks.ex4_instructions(instructions.value)
    return


@app.cell(hide_code=True)
def _(best, chunks, instructions, question):
    context = "\n\n".join(f"[{chunks[index]['id']}]\n{chunks[index]['text']}" for index in best)
    prompt = f"{instructions.value}\n\n<passages>\n{context}\n</passages>\n\nQuestion: {question.value}"
    ask_model = mo.ui.run_button(label="Demander au modèle")
    mo.vstack([mo.accordion({"Le prompt envoyé au modèle": mo.md(f"```\n{prompt}\n```")}), ask_model])
    return ask_model, prompt


@app.cell(hide_code=True)
def _(ask_model, prompt):
    mo.stop(not ask_model.value, mo.md("Appuyez sur **Demander au modèle**."))
    answer, seconds = ask(prompt, "api", temperature=0)
    mo.md(f"{answer}\n\n*{seconds:.1f} s, Groq*")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Le modèle lit seulement les 3 passages : la recherche décide de ce qu'il peut savoir
    - Les ids vous permettent de vérifier chaque fait dans le document

    /// details | Question
    La réponse est fausse. Où regardez-vous d'abord : le modèle ou les passages ?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Une question à laquelle les documents ne répondent pas

    > **L'idée :** sans passage utile, un bon prompt fait dire au modèle qu'il ne sait pas, au lieu d'inventer (slide "Contre l'hallucination")

    **Changez la question** de la partie 1, puis appuyez de nouveau sur le bouton. Par exemple : "How much does Wegovy cost in Belgium?", ou un médicament absent des documents.

    /// details | Question
    Le modèle dit-il que la réponse n'est pas dans les documents ? Retirez votre troisième règle et réessayez.
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option · La taille des passages compte-t-elle ?

    Pour chaque question de test, le document attendu est connu. *hit@3* : la part des questions où il est dans les 3 meilleurs passages.
    **Changez la taille**. Objectif : trouver une taille où hit@3 baisse.
    """)
    return


@app.cell(hide_code=True)
def _():
    size = mo.ui.slider(50, 500, step=50, value=150, label="mots par passage", show_value=True)
    size
    return (size,)


@app.cell(hide_code=True)
def _(size):
    sized_chunks, sized_vectors = rag_index(size.value)
    expected = [item for item in test_questions() if item["in_corpus"]]
    hits = sum(
        any(sized_chunks[int(index)]["doc"] in item["sources"] for index in (sized_vectors @ embed(item["question"])).argsort()[::-1][:3])
        for item in expected
    )
    mo.md(f"**hit@3 = {hits} / {len(expected)}** avec {len(sized_chunks)} passages de {size.value} mots")
    return


if __name__ == "__main__":
    app.run()
