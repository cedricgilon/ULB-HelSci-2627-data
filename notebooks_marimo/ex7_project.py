import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 7: small project")

with app.setup(hide_code=True):
    import marimo as mo

    import checks
    from course import ask


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 7: small project


    A task from your field: start from your one-line idea of yesterday.

    1. The task and 5 examples
    2. The prompt, run on the 5 examples
    3. Check by hand, and three lines to present

    No personal data in the examples.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · The task and 5 examples

    > **The idea:** start small: a clear task, and a few examples where you know the answer (slide "La méthode, toujours la même")

    **Change the task and the examples.** Some ideas, all with no personal data:

    - the triage level of a fictional case (HELPMed: 10 cases written by doctors)
    - a plain-language summary of an EMA document (`data/rag/`)
    - a table from abstracts (exercise 5)
    - teaching vignettes, each fact checked by a person
    - a context-of-use sheet for an AI tool in pharma (EMA–FDA, 10 principles)
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
    ## 2 · The prompt

    > **The idea:** the instructions on one side, the data between tags on the other (slide "Data and messages")

    **Write one line**: the message for one example, the prompt first, then the example between `<input>` tags.
    With `make_message("Say yes or no.", "She felt dizzy.")`, the message must be:

    ```
    Say yes or no.

    <input>
    She felt dizzy.
    </input>
    ```

    An f-string puts a variable in a text: `f"Hello {name}"`. `\n` is a new line.
    """)
    return


@app.cell
def _():
    def make_message(prompt, example):
        """The prompt, then the example between <input> tags."""
        ...  # TODO
    return (make_message,)


@app.cell(hide_code=True)
def _(make_message):
    checks.ex7_message(make_message)
    return


@app.cell(hide_code=True)
def _(task):
    prompt = mo.ui.text_area(value=f"{task.value}\nAnswer with one word.", full_width=True, rows=5)
    run_all = mo.ui.run_button(label="Run on the 5 examples")
    mo.vstack([prompt, run_all])
    return prompt, run_all


@app.cell(hide_code=True)
def _(examples, make_message, prompt, run_all):
    mo.stop(not run_all.value, mo.md("Press **Run on the 5 examples**."))
    outputs = [ask(make_message(prompt.value, example), "api", temperature=0)[0] for example in examples]
    mo.ui.table([{"example": example, "answer": output} for example, output in zip(examples, outputs)], selection=None)
    return (outputs,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · Check by hand, then three lines

    > **The idea:** measure before you trust, then say what the tool does, its risk and how you measure it (slide "Trois lignes à présenter")

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


if __name__ == "__main__":
    app.run()
