"""Contrôles automatiques des notebooks d'exercices.

Un contrôle dit si une réponse est juste. Il ne montre jamais la réponse.
Chaque contrôle renvoie un callout marimo : ⏳ à faire, ✅ juste, ❌ pas encore.
"""
import marimo as mo
import tiktoken


def _status(result, label, hint=""):
    """Un callout pour un contrôle. result vaut True, False, ou None tant que le TODO est ouvert."""
    if result is None:
        return mo.callout(mo.md(f"⏳ {label}"), kind="neutral")
    if result:
        return mo.callout(mo.md(f"✅ {label}"), kind="success")
    return mo.callout(mo.md(f"❌ {label}. {hint}"), kind="warn")


def _run(test, label, hint):
    """Exécute une fonction de test ; une erreur dans le code de l'apprenant devient un ❌ avec son message."""
    try:
        result = test()
    except Exception as error:
        return _status(False, label, f"Erreur : `{type(error).__name__}: {str(error)[:120]}`")
    return _status(result, label, hint)


# ---------------------------------------------------------------- exercice 1

def ex1_count(count_tokens):
    """count_tokens(encoding, text) donne le nombre de tokens."""
    o200k = tiktoken.get_encoding("o200k_base")

    def test():
        n_tokens = count_tokens(o200k, "The patient was given a dose of aspirin.")
        return None if n_tokens is None else n_tokens == 9

    return _run(test, "`count_tokens` donne le nombre de tokens", "Indice : comptez les ids des tokens, pas les mots ni les lettres.")


def ex1_price(price):
    """L'apprenant a saisi un prix par million de tokens."""
    return _status(None if not price else 0 < price < 100, "le prix est saisi", "Indice : donnez des USD par million de tokens en entrée.")


# ---------------------------------------------------------------- exercice 4

def ex4_score(score, question, sentence):
    """score est la similarité entre la question et la phrase."""

    def test():
        if score is None or score is ...:
            return None
        from course import embed, similarity

        return abs(float(score) - similarity(embed(question), embed(sentence))) < 1e-4

    return _run(test, "`score` est la similarité entre la question et la phrase", "Indice : `embed` pour chaque texte, puis `similarity` des deux vecteurs.")


def ex4_instructions(instructions):
    """La ligne d'instructions demande d'utiliser seulement les passages, de les citer, et de dire quand la réponse manque.
    Accepte des instructions en anglais ou en français."""
    text = instructions.lower()
    parts = [
        "only" in text or "seulement" in text or "uniquement" in text,
        "cite" in text or "source" in text or "[" in text,
        "not in" in text or "don't know" in text or "do not know" in text
        or "pas dans" in text or "ne sais pas" in text or "ne figure pas" in text,
    ]
    return _status(None if not any(parts) else all(parts), "les instructions demandent : seulement les passages, les citer, sinon dire \"je ne sais pas\"", "Indice : trois règles, une pour chaque point.")


# ---------------------------------------------------------------- exercice 5

EX5_FIELDS = ["population", "intervention", "sample_size", "study_design", "effect_found", "main_result"]


def ex5_fields(fields_text):
    """Le prompt nomme les six champs."""
    missing = [name for name in EX5_FIELDS if name not in fields_text]
    return _status(None if missing else True, "le prompt nomme les 6 champs")


def ex5_model(model_class):
    """Le modèle pydantic a les six champs, avec sample_size en entier."""

    def test():
        fields = model_class.model_fields
        if "sample_size" not in fields:
            return None
        return set(fields) == set(EX5_FIELDS) and fields["sample_size"].annotation is int

    return _run(test, "`Extraction` a les 6 champs, `sample_size` est un entier", "Indice : une ligne, un nom et un type.")


# ---------------------------------------------------------------- exercice 6

def ex6_names(failure):
    """Chaque ligne fausse a un nom d'échec."""
    if not failure:
        return _status(None, "chaque ligne fausse a un nom d'échec")
    return _status(None if any(not name.strip() for name in failure.values()) else True, "chaque ligne fausse a un nom d'échec")


# ---------------------------------------------------------------- exercice 7

def ex7_message(make_message):
    """make_message(prompt, example) met le prompt d'abord, puis l'exemple entre balises."""

    def test():
        message = make_message("PROMPT", "EXAMPLE")
        if message is None:
            return None
        return message.index("PROMPT") < message.index("EXAMPLE") and "<input>" in message

    return _run(test, "`make_message` met le prompt d'abord, puis l'exemple entre balises `<input>`", "Indice : une f-string avec le prompt, puis l'exemple entre les balises.")
