import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Exercise 5: structured extraction")

with app.setup(hide_code=True):
    import json
    from typing import Literal

    import marimo as mo
    from pydantic import BaseModel, ValidationError

    import checks
    from course import OUTPUT, abstracts, ask_json, write_csv


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Exercise 5: structured extraction


    20 abstracts of clinical studies. The goal: a table that a program can use.

    1. One abstract: a prompt, JSON mode, a dict
    2. Check the fields and their types with `pydantic`
    3. The 20 abstracts: a table and a CSV file

    Option, if you finish early: a strict schema, or a `confidence` field.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1 · One abstract

    > **The idea:** a program needs fixed fields, not sentences, so we ask for JSON (slide "Un programme lit des champs, pas des phrases")

    **Complete the prompt**: one field of the list is missing. Use the allowed values below.
    """)
    return


@app.cell(hide_code=True)
def _():
    DESIGNS = ["randomised controlled trial", "cluster randomised trial", "crossover trial", "secondary analysis of a trial", "cross-sectional study"]
    EFFECTS = ["yes", "no", "mixed", "not applicable"]
    mo.md(f"`study_design`: {', '.join(DESIGNS)} · `effect_found`: {', '.join(EFFECTS)}")
    return DESIGNS, EFFECTS


@app.cell(hide_code=True)
def _():
    fields = mo.ui.text_area(
        value="""Extract these fields from the abstract, as a JSON object:
- population: who was studied (text)
- intervention: what was tested, and against what (text)
- sample_size: number of participants (integer)
- effect_found: a significant benefit on the primary outcome? one of: yes, no, mixed, not applicable
- main_result: the main result, in one sentence (text)""",
        full_width=True,
        rows=8,
    )
    fields
    return (fields,)


@app.cell(hide_code=True)
def _(fields):
    checks.ex5_fields(fields.value)
    return


@app.cell(hide_code=True)
def _():
    corpus = {item["id"]: item["text"] for item in abstracts()}
    abstract_id = mo.ui.dropdown(list(corpus), value="A01", label="abstract")
    extract_one = mo.ui.run_button(label="Extract")
    mo.hstack([abstract_id, extract_one], justify="start")
    return abstract_id, corpus, extract_one


@app.cell(hide_code=True)
def _(abstract_id, corpus, extract_one, fields):
    mo.stop(not extract_one.value, mo.md("Press **Extract**."))
    raw, seconds = ask_json("You extract structured data from abstracts of clinical studies.", f"{fields.value}\n\n<abstract>\n{corpus[abstract_id.value]}\n</abstract>")
    mo.vstack([mo.md(f"*{seconds:.1f} s*"), mo.json(json.loads(raw))])
    return (raw,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - JSON mode: the API returns valid JSON
    - It does not promise your fields, or the right values

    /// details | Question
    Compare with the abstract. Is each value correct?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2 · Check with pydantic

    > **The idea:** valid JSON can hold a value of the wrong type. A pydantic schema rejects it (slide "`pydantic` : un formulaire avec des champs typés")

    **Write one line**: the field `sample_size`, an integer.
    """)
    return


@app.cell
def _():
    class Extraction(BaseModel):
        population: str
        intervention: str
        ...  # TODO
        study_design: Literal["randomised controlled trial", "cluster randomised trial", "crossover trial", "secondary analysis of a trial", "cross-sectional study"]
        effect_found: Literal["yes", "no", "mixed", "not applicable"]
        main_result: str
    return (Extraction,)


@app.cell(hide_code=True)
def _(Extraction):
    checks.ex5_model(Extraction)
    return


@app.cell(hide_code=True)
def _(Extraction):
    bad = '{"population": "adults", "intervention": "metformin", "sample_size": "about 250", "study_design": "trial", "effect_found": "yes", "main_result": "..."}'
    try:
        Extraction.model_validate_json(bad)
        verdict = "accepted"
    except ValidationError as error:
        verdict = f"rejected:\n\n```\n{error}\n```"
    mo.md(f"A bad answer is {verdict}")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - The check rejects a wrong type or a value not in the list, and gives the reason
    - Valid JSON with the wrong number is still wrong: "87,449 women" can become 87

    /// details | Question
    Does your extraction from part 1 pass the check? Try `Extraction.model_validate_json(raw)`.
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3 · The 20 abstracts

    > **The idea:** the check finds badly formed answers, not wrong values (slide "JSON valide, valeur fausse")

    20 calls, one after the other. The free tier allows 8,000 tokens per minute, so some calls wait and try again (HTTP 429). This takes about 2 minutes.
    """)
    return


@app.cell(hide_code=True)
def _():
    extract_all = mo.ui.run_button(label="Extract all 20")
    extract_all
    return (extract_all,)


@app.cell(hide_code=True)
def _(Extraction, corpus, extract_all, fields):
    mo.stop(not extract_all.value, mo.md("Press **Extract all 20**."))
    rows = []
    for item_id, text in mo.status.progress_bar(list(corpus.items()), title="Extracting"):
        answer, _ = ask_json("You extract structured data from abstracts of clinical studies.", f"{fields.value}\n\n<abstract>\n{text}\n</abstract>")
        try:
            rows.append({"id": item_id, **Extraction.model_validate_json(answer).model_dump(), "error": ""})
        except ValidationError as error:
            rows.append({"id": item_id, "error": str(error).splitlines()[0]})
    write_csv(OUTPUT / "extraction.csv", rows)
    mo.vstack([mo.md(f"Saved to `data/output/extraction.csv`: {len(rows)} rows"), mo.ui.table(rows, selection=None)])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Key points**

    - A table that a program can use, in 2 minutes
    - Ask in the prompt < JSON mode < validation
    - Some values are wrong: how do you find them without reading all 20? That is exercise 6

    /// details | Question
    Look at `sample_size`. Which values look wrong?
    ///
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    ## Option

    - **Strict schema**: Groq accepts `response_format={"type": "json_schema", ...}` with the schema from `Extraction.model_json_schema()`. The API then returns your fields
    - **Confidence**: add a `confidence` field (0 to 1) to the prompt and to `Extraction`, then run again. In exercise 6, does the confidence predict the errors?
    """)
    return


if __name__ == "__main__":
    app.run()
