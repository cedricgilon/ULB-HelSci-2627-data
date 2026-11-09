"""Automatic checks of the exercise notebooks.

A check says if an answer is right. It never shows the answer.
Each check returns ⏳ to do, ✅ right, ❌ not yet: a marimo callout in
marimo, Markdown in Jupyter. notebooks_jupyter/checks.py links to this file.
"""
import marimo as mo


def _status(result, label, hint=""):
    """A callout for a check. result is True, False, or None while the answer is still to write."""
    if result is None:
        return _callout(f"⏳ {label}", "neutral")
    if result:
        return _callout(f"✅ {label}", "success")
    return _callout(f"❌ {label}. {hint}", "warn")


def _callout(text, kind):
    """A marimo callout in marimo, Markdown in Jupyter."""
    if mo.running_in_notebook():
        return mo.callout(mo.md(text), kind=kind)
    from IPython.display import Markdown

    return Markdown(text)


# ---------------------------------------------------------------- exercise 1


def ex1_price(price):
    """The learner typed a price per million tokens."""
    return _status(None if not price else 0 < price < 100, "the price is typed", "Hint: give USD per million input tokens.")


# ---------------------------------------------------------------- exercise 4


def ex4_instructions(instructions):
    """The instructions line asks to use only the passages, to cite them, and to say when the answer is missing.
    Accepts instructions in English or in French."""
    text = instructions.lower()
    parts = [
        "only" in text or "seulement" in text or "uniquement" in text,
        "cite" in text or "source" in text or "[" in text,
        "not in" in text or "don't know" in text or "do not know" in text
        or "pas dans" in text or "ne sais pas" in text or "ne figure pas" in text,
    ]
    return _status(None if not any(parts) else all(parts), "the instructions ask: only the passages, cite them, else say \"I don't know\"", "Hint: three rules, one for each point.")


# ---------------------------------------------------------------- exercise 5

EX5_FIELDS = ["population", "intervention", "sample_size", "study_design", "effect_found", "main_result"]


def ex5_fields(fields_text):
    """The prompt names the six fields."""
    missing = [name for name in EX5_FIELDS if name not in fields_text]
    return _status(None if missing else True, "the prompt names the 6 fields")


# ---------------------------------------------------------------- exercise 6

def ex6_names(failure):
    """Each wrong row has a failure name."""
    if not failure:
        return _status(None, "each wrong row has a failure name")
    return _status(None if any(not name.strip() for name in failure.values()) else True, "each wrong row has a failure name")
