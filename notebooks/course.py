"""Fonctions partagées par les notebooks d'exercices.

Vous n'avez pas besoin de lire ce fichier pour faire les exercices.
"""
from functools import cache
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"


def pieces(encoding, text):
    """Un texte découpé en morceaux de tokens, séparés par |."""
    return "|" + "|".join(encoding.decode([token_id]) for token_id in encoding.encode(text)) + "|"


@cache
def distilgpt2():
    """Charge distilgpt2 une fois, en (tokenizer, model). Environ 350 Mo à télécharger la première fois."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2").eval()
    return tokenizer, model


def next_tokens(text, k=5):
    """Les k tokens suivants les plus probables après text, en (token, probabilité), avec distilgpt2."""
    import torch

    tokenizer, model = distilgpt2()
    with torch.no_grad():
        logits = model(**tokenizer(text, return_tensors="pt")).logits[0, -1]
    top = torch.topk(torch.softmax(logits, dim=-1), k)
    return [(tokenizer.decode(token_id), p) for p, token_id in zip(top.values.tolist(), top.indices.tolist())]


# ---------------------------------------------------------------- appels aux modèles

PROVIDERS = {
    "api": {"base_url": "https://api.groq.com/openai/v1", "key": "GROQ_API_KEY", "model": "openai/gpt-oss-20b"},
    "judge": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key": "GEMINI_API_KEY",
        "model": "gemini-3.5-flash-lite",
    },
    "local": {"base_url": "http://localhost:11434/v1", "key": None, "model": "llama3.2:3b"},
}


@cache
def client(provider):
    """Un client compatible OpenAI pour 'api' (Groq), 'judge' (Gemini) ou 'local' (Ollama)."""
    import os

    from dotenv import find_dotenv, load_dotenv
    from openai import OpenAI

    settings = PROVIDERS[provider]
    load_dotenv(find_dotenv(usecwd=True))
    if settings["key"] and not os.environ.get(settings["key"]):
        raise RuntimeError(f"{settings['key']} n'est pas défini. Ajoutez-le au fichier .env du dossier principal.")
    return OpenAI(
        base_url=settings["base_url"],
        api_key=os.environ.get(settings["key"]) if settings["key"] else "ollama",
        max_retries=5,  # attend et réessaie sur HTTP 429, "too many requests"
        timeout=120,
    )


def ask(prompt, provider="api", temperature=0.0):
    """Envoie un prompt ; renvoie (réponse, secondes)."""
    import time

    start = time.perf_counter()
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1000,  # une limite de sécurité : arrête une réponse qui ne finit pas
    )
    return (response.choices[0].message.content or "").strip(), time.perf_counter() - start


def normalise(answer):
    """Minuscules, sans espaces autour, sans point final : 'Nausea.' et 'nausea' comptent comme une seule réponse."""
    return answer.strip().lower().rstrip(".")


# ---------------------------------------------------------------- RAG

BOILERPLATE = __import__("re").compile(
    r"^(Official address|An agency of the European|Union$|Address for visits|Send us a question"
    r"|©|EMADOC-|EMEA/H/C/|EMA/\d+/\d{4})"
)


def load_pdf(path):
    """Le texte d'un PDF en une chaîne, sans les lignes répétées sur chaque page ni les en-têtes de l'EMA."""
    from collections import Counter

    from pypdf import PdfReader

    lines = [line.strip() for page in PdfReader(path).pages for line in (page.extract_text() or "").splitlines()]
    counts = Counter(line for line in lines if line)
    return " ".join(line for line in lines if line and BOILERPLATE.match(line) is None and counts[line] == 1)


@cache
def corpus():
    """Les documents du RAG : {name: text}, depuis data/rag/*.pdf."""
    return {path.stem: load_pdf(path) for path in sorted((DATA / "rag").glob("*.pdf"))}


def chunk(name, text, size=150, overlap=30):
    """Découpe un document en passages de `size` mots ; deux voisins partagent `overlap` mots."""
    words = text.split()
    passages = []
    for number, start in enumerate(range(0, len(words), size - overlap)):
        passages.append({"doc": name, "id": f"{name}#{number}", "text": " ".join(words[start:start + size])})
        if start + size >= len(words):
            break
    return passages


@cache
def embedder():
    """Le modèle d'embedding, chargé une fois : all-MiniLM-L6-v2, 384 nombres par texte, environ 90 Mo."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed(texts):
    """Des vecteurs de longueur 1 : un pour un texte, une matrice (une ligne par texte) pour une liste."""
    return embedder().encode(texts, normalize_embeddings=True)


def similarity(a, b):
    """La similarité cosinus de deux vecteurs de longueur 1 : 1 = même sens, 0 = aucun rapport."""
    return float(a @ b)


@cache
def rag_index(size=150):
    """Tous les passages du corpus et leurs vecteurs, pour une taille de passage en mots."""
    passages = [passage for name, text in corpus().items() for passage in chunk(name, text, size, size // 5)]
    return passages, embed([passage["text"] for passage in passages])


def ema_indications():
    """Les indications des 1 564 médicaments autorisés dans l'UE (EMA), depuis data/train/ema.txt : {nom: texte}."""
    entries = {}
    for block in (DATA / "train" / "ema.txt").read_text(encoding="utf-8").split("\n\n"):
        lines = block.strip().splitlines()
        if lines and lines[0].startswith("Medicine:"):
            name = lines[0].removeprefix("Medicine:").strip()
            entries[name] = " ".join(line.removeprefix("Indication:").strip() for line in lines[1:])
    return entries


@cache
def full_index(size=150):
    """Les passages des documents du RAG et des 1 564 indications de l'EMA, et leurs vecteurs."""
    documents = corpus() | {f"EMA {name}": text for name, text in ema_indications().items()}
    passages = [passage for name, text in documents.items() for passage in chunk(name, text, size, size // 5)]
    return passages, embed([passage["text"] for passage in passages])


def test_questions():
    """Les questions de test de data/rag/questions.json."""
    import json

    return json.loads((DATA / "rag" / "questions.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- extraction et évaluation

OUTPUT = DATA / "output"


def abstracts():
    """Les 20 résumés de data/abstracts.json : [{"id": ..., "text": ...}, ...]."""
    import json

    return json.loads((DATA / "abstracts.json").read_text(encoding="utf-8"))


def ask_json(system, user, provider="api"):
    """Envoie un message système et un message utilisateur en mode JSON ; renvoie (le texte JSON, secondes)."""
    import time

    start = time.perf_counter()
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"],
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0,
        max_tokens=1500,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "", time.perf_counter() - start


def read_csv(path):
    """Un fichier CSV en liste de dicts."""
    import csv

    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    """Écrit une liste de dicts dans un fichier CSV."""
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
