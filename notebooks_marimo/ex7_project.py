import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 7: small project")

with app.setup(hide_code=True):
    import marimo as mo

    from course import PROVIDERS, client


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 7: small project


    A task from your field: start from your one-line idea of yesterday. No code to write.

    1. The prompt and 5 examples
    2. Run on the 5 examples
    3. Check by hand, and three lines to present

    No personal data in the examples. Option: run on the local model and compare.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · The prompt and 5 examples

    > **The idea:** start small: a clear task, and a few examples where you know the answer (slide "The method, always the same")

    **Change the prompt and the examples**, one example per line. Some ideas, all with no personal data:

    - the triage level of a fictional case (HELPMed: 10 cases written by doctors)
    - a plain-language summary of an EMA document (`data/rag/`)
    - a table from abstracts (exercise 5)
    - teaching vignettes, each fact checked by a person
    - a context-of-use sheet for an AI tool in pharma (EMA–FDA, 10 principles)
    """)
    return


@app.cell(hide_code=True)
def _():
    prompt = mo.ui.text_area(
        value="Say whether a sentence reports an adverse event: yes or no.\nAnswer with one word.",
        label="`prompt`",
        full_width=True,
        rows=3,
    )
    examples = mo.ui.text_area(
        value="\n".join([
            "After the second dose, the patient developed a rash on both arms.",
            "The patient took the tablets with breakfast, as advised.",
            "She reported dizziness two hours after the injection.",
            "The study enrolled 120 adults with type 2 diabetes.",
            "Three participants stopped treatment because of nausea.",
        ]),
        label="`examples`, one per line",
        full_width=True,
        rows=6,
    )
    mo.vstack([prompt, examples])
    return examples, prompt


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Run on the 5 examples

    > **The idea:** the instructions on one side, the data between tags on the other (slide "Data and messages")

    The notebook sends one message per example: your prompt first, then the example between `<input>` tags. **Read the two code cells** (no change needed), look at the message for your first example, then press **Run on the examples**.
    """)
    return


@app.cell
def _():
    def make_message(prompt, example):
        """The prompt, then the example between <input> tags."""
        return f"{prompt}\n\n<input>\n{example}\n</input>"
    return (make_message,)


@app.cell(hide_code=True)
def _(examples, make_message, prompt):
    example_list = [line.strip() for line in examples.value.splitlines() if line.strip()]
    mo.stop(not example_list, mo.md("Write at least one example, one per line."))
    mo.md(f"```\n{make_message(prompt.value, example_list[0])}\n```")
    return (example_list,)


@app.cell(hide_code=True)
def _():
    where = mo.ui.dropdown(["api", "local"], value="api", label="`where`")
    run_all = mo.ui.run_button(label="Run on the examples")
    mo.hstack([where, run_all], justify="start")
    return run_all, where


@app.cell
def _(example_list, make_message, prompt, run_all, where):
    mo.stop(not run_all.value, mo.md("Press **Run on the examples**."))
    outputs = []
    for example in example_list:
        response = client(where.value).chat.completions.create(
            model=PROVIDERS[where.value]["model"],
            messages=[{"role": "user", "content": make_message(prompt.value, example)}],
            temperature=0,
        )
        outputs.append(response.choices[0].message.content)
    return (outputs,)


@app.cell(hide_code=True)
def _(example_list, outputs):
    mo.ui.table([{"example": example, "answer": output} for example, output in zip(example_list, outputs)], selection=None)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Check by hand, then three lines

    > **The idea:** measure before you trust, then say what the tool does, its risk and how you measure it (slide "Three lines to present")

    **Tick each right answer.**
    """)
    return


@app.cell(hide_code=True)
def _(outputs):
    right = mo.ui.dictionary({f"example {number + 1}": mo.ui.checkbox(label="right") for number in range(len(outputs))})
    right
    return (right,)


@app.cell(hide_code=True)
def _(right):
    mo.md(f"**{sum(right.value.values())} / {len(right.value)} right**")
    return


@app.cell(hide_code=True)
def _():
    what = mo.ui.text_area(placeholder="What it does", full_width=True)
    risk = mo.ui.text_area(placeholder="The risk if it is wrong", full_width=True)
    measure = mo.ui.text_area(placeholder="How you measure it", full_width=True)
    mo.vstack([what, risk, measure])
    return measure, risk, what


@app.cell(hide_code=True)
def _(measure, risk, what):
    mo.md(f"**What it does**: {what.value}\n\n**Risk if it is wrong**: {risk.value}\n\n**How we measure it**: {measure.value}")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Option: the local model

    Set `where` to `local`, press **Run on the examples** again, and tick again. Does the small local model get the same score?
    """)
    return


if __name__ == "__main__":
    app.run()
