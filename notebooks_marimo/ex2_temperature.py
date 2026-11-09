import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 2: local vs API, temperature")

with app.setup(hide_code=True):
    import marimo as mo

    from course import ask, normalise


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 2: local vs API, temperature


    1. On the web: the temperature in Vittascience
    2. The same question, on your laptop and on the API
    3. The same question, 5 times, at a temperature you choose

    Option, if you finish early: ask for references, then check them.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · On the web

    > **The idea:** the model draws each token at random, from the probabilities. The same prompt can give a different answer (slide "Same prompt, same answer?")

    Open <https://fr.vittascience.com/ia/text>.

    - Write a prompt. Run it 3 times with low randomness, then 3 times with high randomness
    - Turn on the display of the tokens and their ids

    /// details | Question
    Where does this model run: on your laptop or on a server?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Local or API

    > **The idea:** the same kind of model runs on your laptop or at a provider. The response time changes, and so does the place where your data goes

    **Choose** where the model runs, then press the button. Ask the question once with each.
    The local model can take 30 to 60 s on a laptop with no GPU.
    """)
    return


@app.cell(hide_code=True)
def _():
    prompt = mo.ui.text_area(
        value="What is the most common side effect of metformin? Answer in two words.", full_width=True
    )
    where = mo.ui.dropdown({"local (Ollama, llama3.2:3b)": "local", "API (Groq, gpt-oss-20b)": "api"}, value="local (Ollama, llama3.2:3b)")
    ask_once = mo.ui.run_button(label="Ask the model")
    mo.vstack([prompt, mo.hstack([where, ask_once], justify="start")])
    return ask_once, prompt, where


@app.cell(hide_code=True)
def _(ask_once, prompt, where):
    mo.stop(not ask_once.value, mo.md("Press **Ask the model**."))
    answer, seconds = ask(prompt.value, where.value, temperature=0)
    mo.md(f"**{seconds:.1f} s** · {answer}")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Local: slower with no GPU, the text stays on your laptop
    - API: fast, the text goes to the provider

    /// details | Question
    You work with patient notes. Which one do you choose, and why?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Temperature

    > **The idea:** the temperature sets how random the draw is. Low: nearly always the most probable token. High: more variety (slide "Temperature")

    The same question, 5 times, on the API. How many **different** answers?

    **Predict first**, before you press the button.
    """)
    return


@app.cell(hide_code=True)
def _():
    guess_low = mo.ui.number(start=1, stop=5, value=1, label="different answers at temperature 0")
    guess_high = mo.ui.number(start=1, stop=5, value=1, label="different answers at temperature 1.5")
    mo.vstack([guess_low, guess_high])
    return guess_high, guess_low


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Change** the temperature, then press the button. Target: check your two predictions, then find a temperature where the 5 answers are all different.
    """)
    return


@app.cell(hide_code=True)
def _():
    temperature = mo.ui.slider(0, 1.5, step=0.1, value=0, label="temperature", show_value=True)
    ask_five = mo.ui.run_button(label="Ask 5 times")
    mo.hstack([temperature, ask_five], justify="start")
    return ask_five, temperature


@app.cell(hide_code=True)
def _(ask_five, guess_high, guess_low, prompt, temperature):
    mo.stop(not ask_five.value, mo.md("Press **Ask 5 times**."))
    answers = [ask(prompt.value, "api", temperature.value)[0] for _ in range(5)]
    different = len({normalise(answer) for answer in answers})
    mo.vstack([
        mo.md(f"**{different} different answer(s)** at temperature {temperature.value}. "
              f"Your predictions: {guess_low.value} at 0, {guess_high.value} at 1.5"),
        mo.ui.table([{"answer": answer} for answer in answers], selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Key points**

    - The temperature changes the variety of the answers, not their truth
    - At temperature 0, an API can still give a different answer: your request runs in a batch with other requests
    - Low temperature for extraction and code, higher for ideas and drafts
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option · Invented references

    1. In the box of part 2, ask: *"Give 3 peer-reviewed articles on (a narrow topic you know well), with authors, year, title, journal and DOI."* Ask the local model and the API
    2. Ask the same in a chat app with web search turned on. Did it search?
    3. Check each reference:
        - open `https://doi.org/` + the DOI: same title? same first author? A DOI that opens is not a proof
        - else, search the title in PubMed, then in Crossref
        - found: read the abstract. Does it say what the model said?
    4. Give each one a label: correct / real with errors / real but off-topic / invented

    /// details | Question
    Our API and our local models have no web search. What do you expect from them?
    ///
    """)
    return


if __name__ == "__main__":
    app.run()
