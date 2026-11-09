import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 2: local vs API, temperature")

with app.setup(hide_code=True):
    import os
    import time

    import marimo as mo
    from dotenv import find_dotenv, load_dotenv
    from openai import OpenAI

    from course import ask, normalise

    load_dotenv(find_dotenv(usecwd=True))  # puts the keys of the .env file in os.environ


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

    Below: the full call, twice. **Read the two cells**: what changes between the local model and the API? Then press the two buttons.
    The local model can take 30 to 60 s on a laptop with no GPU.
    """)
    return


@app.cell(hide_code=True)
def _():
    prompt = mo.ui.text_area(
        value="What is the most common side effect of metformin? Answer in two words.", label="`prompt`", full_width=True
    )
    ask_local = mo.ui.run_button(label="Ask the local model")
    ask_api = mo.ui.run_button(label="Ask the API")
    mo.vstack([prompt, mo.hstack([ask_local, ask_api], justify="start")])
    return ask_api, ask_local, prompt


@app.cell
def _(ask_local, prompt):
    mo.stop(not ask_local.value, mo.md("Press **Ask the local model**."))
    local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # Ollama, on your laptop
    local_start = time.perf_counter()
    local_response = local.chat.completions.create(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt.value}],
        temperature=0,
    )
    local_seconds = time.perf_counter() - local_start
    return local_response, local_seconds


@app.cell(hide_code=True)
def _(local_response, local_seconds):
    mo.vstack([
        mo.md(f"**Local, {local_seconds:.1f} s** · {local_response.choices[0].message.content}"),
        mo.accordion({"The full response": mo.json(local_response.model_dump())}),
    ])
    return


@app.cell
def _(ask_api, prompt):
    mo.stop(not ask_api.value, mo.md("Press **Ask the API**."))
    api = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])  # Groq: the text goes to a provider's server
    api_start = time.perf_counter()
    api_response = api.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt.value}],
        temperature=0,
    )
    api_seconds = time.perf_counter() - api_start
    return api_response, api_seconds


@app.cell(hide_code=True)
def _(api_response, api_seconds):
    mo.vstack([
        mo.md(f"**API, {api_seconds:.1f} s** · {api_response.choices[0].message.content}"),
        mo.accordion({"The full response": mo.json(api_response.model_dump())}),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - The same code: only the address (`base_url`), the key and the model name change
    - Local: slower with no GPU, the text stays on your laptop
    - API: fast, the text goes to the provider
    - In "The full response": `usage` gives the tokens in and out, `finish_reason` why the answer stopped

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

    **Change** the temperature, then press the button. Target: press once at 0, then find a temperature where the 5 answers are all different.
    """)
    return


@app.cell(hide_code=True)
def _():
    temperature = mo.ui.slider(0, 1.5, step=0.1, value=0, label="temperature", show_value=True)
    ask_five = mo.ui.run_button(label="Ask 5 times")
    mo.hstack([temperature, ask_five], justify="start")
    return ask_five, temperature


@app.cell(hide_code=True)
def _(ask_five, prompt, temperature):
    mo.stop(not ask_five.value, mo.md("Press **Ask 5 times**."))
    answers = [ask(prompt.value, "api", temperature.value)[0] for _ in range(5)]
    different = len({normalise(answer) for answer in answers})
    mo.vstack([
        mo.md(f"**{different} different answer(s)** at temperature {temperature.value}"),
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
