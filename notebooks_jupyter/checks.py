"""Automatic checks of the exercise notebooks.

A check says if an answer is right. It never shows the answer.
Each check returns ⏳ to do, ✅ right, ❌ not yet: a marimo callout in
marimo, Markdown in Jupyter. notebooks_jupyter/checks.py links to this file.
"""
import marimo as mo
import tiktoken


def _status(result, label, hint=""):
    """A callout for a check. result is True, False, or None while the TODO is open."""
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


def _run(test, label, hint):
    """Run a test function. An error in the learner's code becomes a ❌ with its message."""
    try:
        result = test()
    except Exception as error:
        return _status(False, label, f"Error: `{type(error).__name__}: {str(error)[:120]}`")
    return _status(result, label, hint)


# ---------------------------------------------------------------- exercise 1

def ex1_count(count_tokens):
    """count_tokens(encoding, text) gives the number of tokens."""
    o200k = tiktoken.get_encoding("o200k_base")

    def test():
        n_tokens = count_tokens(o200k, "The patient was given a dose of aspirin.")
        return None if n_tokens is None else n_tokens == 9

    return _run(test, "`count_tokens` gives the number of tokens", "Hint: count the token ids, not the words or the letters.")


def ex1_price(price):
    """The learner typed a price per million tokens."""
    return _status(None if not price else 0 < price < 100, "the price is typed", "Hint: give USD per million input tokens.")


# ---------------------------------------------------------------- exercise 4

def ex4_score(score, question, sentence):
    """score is the similarity between the question and the sentence."""

    def test():
        if score is None or score is ...:
            return None
        from course import embed, similarity

        return abs(float(score) - similarity(embed(question), embed(sentence))) < 1e-4

    return _run(test, "`score` is the similarity between the question and the sentence", "Hint: `embed` for each text, then `similarity` of the two vectors.")


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


def ex5_model(model_class):
    """The pydantic model has the six fields, with sample_size as an integer."""

    def test():
        fields = model_class.model_fields
        if "sample_size" not in fields:
            return None
        return set(fields) == set(EX5_FIELDS) and fields["sample_size"].annotation is int

    return _run(test, "`Extraction` has the 6 fields, `sample_size` is an integer", "Hint: one line, a name and a type.")


# ---------------------------------------------------------------- exercise 6

def ex6_names(failure):
    """Each wrong row has a failure name."""
    if not failure:
        return _status(None, "each wrong row has a failure name")
    return _status(None if any(not name.strip() for name in failure.values()) else True, "each wrong row has a failure name")


# ---------------------------------------------------------------- exercise 7

def ex7_message(make_message):
    """make_message(prompt, example) puts the prompt first, then the example between tags."""

    def test():
        message = make_message("PROMPT", "EXAMPLE")
        if message is None:
            return None
        return message.index("PROMPT") < message.index("EXAMPLE") and "<input>" in message

    return _run(test, "`make_message` puts the prompt first, then the example between `<input>` tags", "Hint: an f-string with the prompt, then the example between the tags.")
