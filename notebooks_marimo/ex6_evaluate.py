import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 6: evaluate")

with app.setup(hide_code=True):
    from collections import Counter

    import marimo as mo

    import checks
    from course import DATA, OUTPUT, PROVIDERS, client, read_csv


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 6: evaluate


    First read the errors and name them, then measure.

    1. Read the wrong rows, name each failure
    2. Count the failure types, then the accuracy per field
    3. A second model as a judge, checked against your own labels
    """)
    return


@app.cell(hide_code=True)
def _():
    sources = {"a small model (llama3.2:3b)": DATA / "extraction_reference.csv"}
    if (OUTPUT / "extraction.csv").exists():
        sources["your extraction (exercise 5)"] = OUTPUT / "extraction.csv"
    source = mo.ui.dropdown(sources, value="a small model (llama3.2:3b)", label="extraction to evaluate")
    source
    return (source,)


@app.cell(hide_code=True)
def _(source):
    extracted = {row["id"]: row for row in read_csv(source.value)}
    truth = {row["id"]: row for row in read_csv(DATA / "ground_truth.csv")}
    mo.md(f"Ground truth: {len(truth)} abstracts, written by a person. A large model made no error on these in our test, so start with the small model")
    return extracted, truth


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · Read and name

    > **The idea:** before you measure, read the errors and give them a name (slide "Read the errors, as for MNIST")

    The rows where an exact field is wrong. The `note` of the ground truth gives the reason.
    """)
    return


@app.cell(hide_code=True)
def _(extracted, truth):
    EXACT = ["sample_size", "study_design", "effect_found"]
    wrong = [
        {"id": item_id, "field": field, "extracted": extracted[item_id].get(field, ""), "right": truth[item_id][field], "note": truth[item_id]["note"]}
        for item_id in truth if item_id in extracted
        for field in EXACT if str(extracted[item_id].get(field, "")).strip().lower() != truth[item_id][field].strip().lower()
    ]
    mo.ui.table(wrong[:5], selection=None)
    return EXACT, wrong


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Give a short name to each wrong row**: what type of failure is it? For example "clusters counted instead of people".
    """)
    return


@app.cell(hide_code=True)
def _(wrong):
    failure = mo.ui.dictionary({f"{row['id']} {row['field']}": mo.ui.text(placeholder="failure type", full_width=True) for row in wrong[:5]})
    failure
    return (failure,)


@app.cell(hide_code=True)
def _(failure):
    checks.ex6_names(failure.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    /// details | Question
    Which rows have the same problem?
    ///

    ## 2 · Count, then measure

    > **The idea:** accuracy says how many errors, the failure types say what to fix (slide "What to measure?")
    """)
    return


@app.cell(hide_code=True)
def _(failure):
    counts = Counter(failure.value.values())
    mo.ui.table([{"failure type": name, "rows": count} for name, count in counts.most_common() if name], selection=None)
    return


@app.cell(hide_code=True)
def _(EXACT):
    field = mo.ui.dropdown(EXACT, value="sample_size", label="field")
    field
    return (field,)


@app.cell(hide_code=True)
def _(extracted, field, truth):
    right = sum(str(extracted[item_id].get(field.value, "")).strip().lower() == truth[item_id][field.value].strip().lower() for item_id in truth if item_id in extracted)
    mo.md(f"**{field.value}: {right} / {len(truth)} correct**")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - Accuracy says *how often*. The list of failures says *what to fix*
    - These 10 rows are a dev set: you look at them and change the prompt. A real test set stays closed until the end, as in the ML module

    /// details | Question
    Which one tells you how to change the prompt?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · A judge for one failure type

    > **The idea:** an LLM judge is a classifier. Check that it agrees with you before you trust it (slide "The judge is a classifier: test it")

    The field `main_result` is free text: a program cannot compare it word by word. A second model (Gemini) judges it.

    **First, label 5 rows yourself**: tick a row when the extracted result is good.
    """)
    return


@app.cell(hide_code=True)
def _(extracted, truth):
    sample = [item_id for item_id in truth if item_id in extracted][:5]
    mo.ui.table([{"id": item_id, "extracted": extracted[item_id].get("main_result", ""), "ground truth": truth[item_id]["main_result"]} for item_id in sample], selection=None)
    return (sample,)


@app.cell(hide_code=True)
def _(sample):
    my_label = mo.ui.dictionary({item_id: mo.ui.checkbox(label="good") for item_id in sample})
    my_label
    return (my_label,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Change one line of the rubric**, then press the button. Target: a judge that agrees with you. **Read the judge cell**: the judge is one more call, with your rubric in the message.
    """)
    return


@app.cell(hide_code=True)
def _():
    rubric = mo.ui.text_area(
        value="""Does the extracted result state the primary outcome and its direction, as the ground truth does?
Give your reason in one sentence first. Then, on the last line, write only PASS or FAIL.""",
        full_width=True,
    )
    judge_now = mo.ui.run_button(label="Ask the judge")
    mo.vstack([rubric, judge_now])
    return judge_now, rubric


@app.cell
def _(extracted, judge_now, rubric, sample, truth):
    mo.stop(not judge_now.value, mo.md("Press **Ask the judge**."))
    verdicts = {}
    for item_id in sample:
        message = f"{rubric.value}\n\nGround truth: {truth[item_id]['main_result']}\nExtracted: {extracted[item_id].get('main_result', '')}"
        response = client("judge").chat.completions.create(
            model=PROVIDERS["judge"]["model"],  # Gemini, a second model
            messages=[{"role": "user", "content": message}],
            temperature=0,
        )
        last_line = (response.choices[0].message.content or "").strip().splitlines()[-1]
        verdicts[item_id] = last_line.strip().upper().startswith("PASS")  # True = PASS
    return (verdicts,)


@app.cell(hide_code=True)
def _(my_label, sample, verdicts):
    failures = [item_id for item_id in sample if not my_label.value[item_id]]
    good = [item_id for item_id in sample if my_label.value[item_id]]
    mo.vstack([
        mo.md(f"**The judge found {sum(not verdicts[i] for i in failures)} of {len(failures)} failure(s), and passed {sum(verdicts[i] for i in good)} of {len(good)} good answer(s)**"),
        mo.ui.table([{"id": i, "you": "good" if my_label.value[i] else "failure", "judge": "PASS" if verdicts[i] else "FAIL"} for i in sample], selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Key points**

    - Read, name, count: then measure
    - A judge is a test that you must test
    - 10 rows is few: a real error analysis reads about 100

    /// details | Question
    Find a row where you and the judge disagree. Who is right?
    ///

    ---
    ## Option

    The search of exercise 4: open its option and compare hit@3 for k = 1, 3, 5 passages.
    """)
    return


if __name__ == "__main__":
    app.run()
