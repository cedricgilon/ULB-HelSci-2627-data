"""Functions shared by the exercise notebooks.

You do not need to read this file to do the exercises.
"""
from functools import cache
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"


def pieces(encoding, text):
    """A text cut into token pieces, separated by |."""
    return "|" + "|".join(encoding.decode([token_id]) for token_id in encoding.encode(text)) + "|"


@cache
def distilgpt2():
    """Load distilgpt2 once, as (tokenizer, model). About 350 MB to download the first time."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2").eval()
    return tokenizer, model


def next_tokens(text, k=5):
    """The k most probable next tokens after text, as (token, probability), with distilgpt2."""
    import torch

    tokenizer, model = distilgpt2()
    with torch.no_grad():
        logits = model(**tokenizer(text, return_tensors="pt")).logits[0, -1]
    top = torch.topk(torch.softmax(logits, dim=-1), k)
    return [(tokenizer.decode(token_id), p) for p, token_id in zip(top.values.tolist(), top.indices.tolist())]


# ---------------------------------------------------------------- model calls

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
    """An OpenAI-compatible client for 'api' (Groq), 'judge' (Gemini) or 'local' (Ollama)."""
    import os

    from dotenv import find_dotenv, load_dotenv
    from openai import OpenAI

    settings = PROVIDERS[provider]
    load_dotenv(find_dotenv(usecwd=True))
    if settings["key"] and not os.environ.get(settings["key"]):
        raise RuntimeError(f"{settings['key']} is not set. Add it to the .env file in the main folder.")
    return OpenAI(
        base_url=settings["base_url"],
        api_key=os.environ.get(settings["key"]) if settings["key"] else "ollama",
        max_retries=5,  # waits and tries again on HTTP 429, "too many requests"
        timeout=120,
    )


def ask(prompt, provider="api", temperature=0.0):
    """Send a prompt. Return (answer, seconds)."""
    import time

    start = time.perf_counter()
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1000,  # a safety limit: stops an answer that does not end
    )
    return (response.choices[0].message.content or "").strip(), time.perf_counter() - start


def normalise(answer):
    """Lower case, no spaces around, no final full stop: 'Nausea.' and 'nausea' count as one answer."""
    return answer.strip().lower().rstrip(".")


# ---------------------------------------------------------------- RAG

BOILERPLATE = __import__("re").compile(
    r"^(Official address|An agency of the European|Union$|Address for visits|Send us a question"
    r"|©|EMADOC-|EMEA/H/C/|EMA/\d+/\d{4})"
)


def load_pdf(path):
    """The text of a PDF as one string, without the lines repeated on each page and without the EMA headers."""
    from collections import Counter

    from pypdf import PdfReader

    lines = [line.strip() for page in PdfReader(path).pages for line in (page.extract_text() or "").splitlines()]
    counts = Counter(line for line in lines if line)
    return " ".join(line for line in lines if line and BOILERPLATE.match(line) is None and counts[line] == 1)


@cache
def corpus():
    """The RAG documents: {name: text}, from data/rag/*.pdf."""
    return {path.stem: load_pdf(path) for path in sorted((DATA / "rag").glob("*.pdf"))}


def chunk(name, text, size=150, overlap=30):
    """Cut a document into passages of `size` words. Two neighbours share `overlap` words."""
    words = text.split()
    passages = []
    for number, start in enumerate(range(0, len(words), size - overlap)):
        passages.append({"doc": name, "id": f"{name}#{number}", "text": " ".join(words[start:start + size])})
        if start + size >= len(words):
            break
    return passages


@cache
def embedder():
    """The embedding model, loaded once: all-MiniLM-L6-v2, 384 numbers per text, about 90 MB."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed(texts):
    """Vectors of length 1: one for a text, a matrix (one row per text) for a list."""
    return embedder().encode(texts, normalize_embeddings=True)


def similarity(a, b):
    """The cosine similarity of two vectors of length 1: 1 = same meaning, 0 = not related."""
    return float(a @ b)


@cache
def rag_index(size=150):
    """All the passages of the corpus and their vectors, for a passage size in words."""
    passages = [passage for name, text in corpus().items() for passage in chunk(name, text, size, size // 5)]
    return passages, embed([passage["text"] for passage in passages])


def ema_indications():
    """The indications of the 1,564 medicines authorised in the EU (EMA), from data/train/ema.txt: {name: text}."""
    entries = {}
    for block in (DATA / "train" / "ema.txt").read_text(encoding="utf-8").split("\n\n"):
        lines = block.strip().splitlines()
        if lines and lines[0].startswith("Medicine:"):
            name = lines[0].removeprefix("Medicine:").strip()
            entries[name] = " ".join(line.removeprefix("Indication:").strip() for line in lines[1:])
    return entries


@cache
def full_index(size=150):
    """The passages of the RAG documents and of the 1,564 EMA indications, and their vectors."""
    documents = corpus() | {f"EMA {name}": text for name, text in ema_indications().items()}
    passages = [passage for name, text in documents.items() for passage in chunk(name, text, size, size // 5)]
    return passages, embed([passage["text"] for passage in passages])


def test_questions():
    """The test questions of data/rag/questions.json."""
    import json

    return json.loads((DATA / "rag" / "questions.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- extraction and evaluation

OUTPUT = DATA / "output"


def abstracts():
    """The 20 abstracts of data/abstracts.json: [{"id": ..., "text": ...}, ...]."""
    import json

    return json.loads((DATA / "abstracts.json").read_text(encoding="utf-8"))


def ask_json(system, user, provider="api"):
    """Send a system message and a user message in JSON mode. Return (the JSON text, seconds)."""
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
    """A CSV file as a list of dicts."""
    import csv

    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    """Write a list of dicts to a CSV file."""
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
