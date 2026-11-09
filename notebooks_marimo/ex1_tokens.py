import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 1: tokens")

with app.setup(hide_code=True):
    import marimo as mo
    import tiktoken

    import checks
    from course import next_tokens, pieces

    o200k = tiktoken.get_encoding("o200k_base")  # recent OpenAI models, ~200,000 tokens
    gpt2 = tiktoken.get_encoding("gpt2")


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 1: tokens

    No API: everything runs on your laptop.

    A model does not read words. It reads **tokens**: pieces of text, each with an integer number (id).

    1. On the web: see the tokens
    2. One sentence, five languages
    3. Words from your field, and the cost

    Option, if you finish early: the next token, with a small model.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · On the web

    > **The idea:** a model reads tokens, not words, each with a number (slide "A model reads tokens, not words")

    Open <https://tiktokenizer.vercel.app/> and select `o200k_base`.

    - Type a sentence in English, then the same sentence in another language you know. Count the tokens.
    - Type a word from your field: a molecule, a disease, a lab technique.

    /// details | Question
    Which word is cut into the most pieces? Why?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · One sentence, five languages

    > **The idea:** the vocabulary is learned mostly from English text. For the same meaning, another language can need more tokens (slide "A fixed vocabulary")

    The same sentence in five languages. **Add your language**: one more line in the dictionary.
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
    `encode` cuts a text into tokens and gives their numbers:
    """)
    return


@app.cell
def _():
    o200k.encode("The patient was given aspirin")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Read the function**: `encode` cuts the text into token ids, `len` counts them. `encoding` is the tokenizer: `o200k` or `gpt2`.
    """)
    return


@app.function
def count_tokens(encoding, text):
    """The number of tokens in text."""
    return len(encoding.encode(text))


@app.cell(hide_code=True)
def _(sentences):
    english = count_tokens(o200k, sentences["English"])
    mo.ui.table(
        [
            {
                "language": language,
                "o200k (2024)": count_tokens(o200k, text),
                "gpt2 (2019)": count_tokens(gpt2, text),
                "vs English": f"{count_tokens(o200k, text) / english - 1:+.0%}" if english else "",
            }
            for language, text in sentences.items()
        ],
        selection=None,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Same meaning, different number of tokens.
    - The older tokenizer, `gpt2`, was built on mostly English text.

    /// details | Question
    API prices are per token. What does this mean for a prompt in French or in Arabic?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Words from your field, and the cost

    > **The idea:** a rare word is cut into several tokens, and the API charges per token (slide "Rare words are cut into pieces")

    **Change the list**: three words from your field.
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
    - The model does not see the letters of a word, only its pieces.

    **Find the price** of `openai/gpt-oss-20b` at Groq: input tokens, USD per million.
    Look at <https://console.groq.com/docs/models>
    """)
    return


@app.cell(hide_code=True)
def _():
    price = mo.ui.number(start=0, stop=100, step=0.005, value=0, label="USD per million input tokens")
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
                "language": language,
                "tokens": count_tokens(o200k, text),
                "USD for one million sentences": round((count_tokens(o200k, text) or 0) * price.value, 2),
            }
            for language, text in sentences.items()
        ],
        selection=None,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Key points**

    - Same meaning, different cost: a language the tokenizer saw less costs more.
    - Technical words are cut into many pieces.
    - The context window is also counted in tokens.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option · The next token

    `distilgpt2` is a small model: 82 million parameters. It is not a chat model.
    For a text, it gives each of its 50,257 tokens a probability to be the next one.

    The first time you press the button, the model is downloaded: about 350 MB.
    """)
    return


@app.cell(hide_code=True)
def _():
    start = mo.ui.text(value="The patient was given a dose of", full_width=True)
    predict = mo.ui.run_button(label="Next token")
    mo.vstack([start, predict])
    return predict, start


@app.cell(hide_code=True)
def _(predict, start):
    mo.stop(not predict.value, mo.md("Press **Next token**."))
    mo.ui.table(
        [{"next token": repr(token), "probability": f"{p:.1%}"} for token, p in next_tokens(start.value)],
        selection=None,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - **Do the sampling yourself**: copy one of the five tokens to the end of the text, then press the button again. Do it five times.
    - The text is a chain of local choices. No plan, no true or false: only what is probable.
    """)
    return


if __name__ == "__main__":
    app.run()
