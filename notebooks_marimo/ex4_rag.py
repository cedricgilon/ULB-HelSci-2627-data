import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 4: RAG by hand")

with app.setup(hide_code=True):
    import marimo as mo

    import checks
    from course import ask, embed, rag_index, similarity, test_questions


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 4: RAG by hand


    The documents: 8 EMA medicine summaries, and Narvelia, a medicine that does not exist.

    1. Search: find the passages closest to a question
    2. Answer: put the passages in the prompt
    3. A question the documents do not answer

    Option, if you finish early: does the passage size matter?
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Search

    > **The idea:** the search compares the meaning of the question with the meaning of each passage, with embeddings (slide "Cosine similarity")

    The documents are cut into passages of 150 words, and each passage becomes a vector of 384 numbers.
    This cell runs once, on your laptop: nothing is sent.
    """)
    return


@app.cell(hide_code=True)
def _():
    chunks, vectors = rag_index(150)
    mo.md(f"{len(chunks)} passages · matrix of {vectors.shape[0]} × {vectors.shape[1]} numbers")
    return chunks, vectors


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Two texts to compare: a question and a sentence.
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
    `question.value` is the text in the `question` box. `embed` turns it into a vector of 384 numbers. The first 5:
    """)
    return


@app.cell
def _(question):
    embed(question.value)[:5]
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Write one line**: the similarity between `question.value` and `sentence.value`. `similarity(a, b)` compares two vectors.
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
    mo.accordion({"💡 Hint": mo.md("`similarity` takes two vectors: `embed(...)` for each text.")})
    return


@app.cell(hide_code=True)
def _(score):
    mo.stop(score is ..., mo.md("First write the line above."))
    mo.md(f"""
    **Score: {score:.2f}.** 1: the same meaning. 0: no relation.

    **Change the sentence.** Target: a score near 0 (another topic), then a high score with different words (same meaning).
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The search does the same with each passage, then keeps the 3 best scores.
    """)
    return


@app.cell(hide_code=True)
def _(chunks, question, score, vectors):
    mo.stop(score is ..., mo.md("First write the line above."))
    question_vector = embed(question.value)
    scores = [similarity(question_vector, vector) for vector in vectors]
    best = sorted(range(len(chunks)), key=lambda index: scores[index], reverse=True)[:3]
    mo.ui.table(
        [{"score": round(float(scores[index]), 2), "passage": chunks[index]["id"], "text": chunks[index]["text"][:200] + " …"} for index in best],
        selection=None,
    )
    return (best,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - The search runs on your laptop, in less than one second
    - The passage closest to the question is not always the one that contains the answer

    **Change the question.** Target: find a question where the best passage comes from the wrong medicine.
    Try "Which medicines treat chronic kidney disease?": two documents contain the answer.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Answer

    > **The idea:** the model does not know your documents. The program puts the best passages in the prompt (slide "The answer prompt")

    **Complete the instructions**: three rules. Use only the passages. Cite the passage id. If the answer is not there, say so.
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
    ask_model = mo.ui.run_button(label="Ask the model")
    mo.vstack([mo.accordion({"The prompt sent to the model": mo.md(f"```\n{prompt}\n```")}), ask_model])
    return ask_model, prompt


@app.cell(hide_code=True)
def _(ask_model, prompt):
    mo.stop(not ask_model.value, mo.md("Press **Ask the model**."))
    answer, seconds = ask(prompt, "api", temperature=0)
    mo.md(f"{answer}\n\n*{seconds:.1f} s, Groq*")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - The model reads only the 3 passages: the search decides what it can know
    - With the ids, you can check each fact in the document

    /// details | Question
    The answer is wrong. Where do you look first: the model or the passages?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · A question the documents do not answer

    > **The idea:** with no useful passage, a good prompt makes the model say that it does not know, instead of making up an answer (slide "Against hallucination")

    **Change the question** in part 1, then press the button again. For example: "How much does Wegovy cost in Belgium?", or a medicine that is not in the documents.

    /// details | Question
    Does the model say that the answer is not in the documents? Remove your third rule and try again.
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option · Does the passage size matter?

    For each test question, the expected document is known. *hit@3*: the share of questions where it is in the 3 best passages.
    **Change the size**. Target: find a size where hit@3 goes down.
    """)
    return


@app.cell(hide_code=True)
def _():
    size = mo.ui.slider(50, 500, step=50, value=150, label="words per passage", show_value=True)
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
    mo.md(f"**hit@3 = {hits} / {len(expected)}** with {len(sized_chunks)} passages of {size.value} words")
    return


if __name__ == "__main__":
    app.run()
