# %% [markdown]
# # Install check — Introduction to LLM
#
# Run every cell, top to bottom (**Run All**), or in a terminal:
# `uv run python install_check.py`.
#
# Each check prints one line: `OK`, `WARN` (optional, you can follow the
# module without it) or `FAIL` (fix it before 9 November). The last cell
# prints **READY** or the list of what to fix.
#
# The first run downloads about 450 MB of model files. Run it at home.

# %%
import importlib
from importlib import metadata
import os
import sys
import time

results = []


def record(status, name, detail=""):
    """Store one check result and print it at once."""
    results.append((status, name, detail))
    print(f"{status:<5} {name:<28} {detail}")


# %% [markdown]
# ## 1. Python and packages

# %%
version = sys.version_info
if (3, 11) <= (version.major, version.minor) <= (3, 14):
    record("OK", "Python version", f"{version.major}.{version.minor}.{version.micro}")
else:
    record("FAIL", "Python version", f"{version.major}.{version.minor} — need 3.11 to 3.14")

PACKAGES = [
    ("jupyter", "jupyter"),
    ("marimo", "marimo"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("scikit-learn", "sklearn"),
    ("matplotlib", "matplotlib"),
    ("tiktoken", "tiktoken"),
    ("transformers", "transformers"),
    ("torch", "torch"),
    ("openai", "openai"),
    ("google-genai", "google.genai"),
    ("python-dotenv", "dotenv"),
    ("pydantic", "pydantic"),
    ("sentence-transformers", "sentence_transformers"),
    ("pypdf", "pypdf"),
    ("ollama", "ollama"),
]

for package, module_name in PACKAGES:
    try:
        importlib.import_module(module_name)
        record("OK", package, metadata.version(package))
    except Exception as error:
        record("FAIL", package, f"{type(error).__name__}: {error}")

# %% [markdown]
# ## 2. Model files
#
# These download on first use. After one successful run they are stored
# on your laptop and nothing is downloaded again.

# %%
try:
    import tiktoken

    encoding = tiktoken.get_encoding("o200k_base")
    record("OK", "tiktoken o200k_base", f"{len(encoding.encode('Hello, world'))} tokens")
except Exception as error:
    record("FAIL", "tiktoken o200k_base", f"{type(error).__name__}: {error}")

# %%
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2")
    inputs = tokenizer("The patient was given", return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    next_token = tokenizer.decode(logits[0, -1].argmax())
    record("OK", "distilgpt2 (353 MB)", f"next token: {next_token!r}")
except Exception as error:
    record("FAIL", "distilgpt2 (353 MB)", f"{type(error).__name__}: {error}")

# %%
try:
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vector = embedder.encode("The patient was given metformin.")
    record("OK", "all-MiniLM-L6-v2 (91 MB)", f"vector of {len(vector)} numbers")
except Exception as error:
    record("FAIL", "all-MiniLM-L6-v2 (91 MB)", f"{type(error).__name__}: {error}")

# %% [markdown]
# ## 3. API keys
#
# The keys are read from a file named `.env` in the main folder of the
# module, one level above this file. The exercises look for it there
# too. The keys are never printed in full.

# %%
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(env_path)
    record("OK", ".env file", env_path)
else:
    record("FAIL", ".env file", f"not found in {os.getcwd()} or any folder above it")

KEYS = [
    ("GROQ_API_KEY", "gsk_", "https://console.groq.com — Groq with a q"),
    ("GEMINI_API_KEY", "", "https://aistudio.google.com"),
]

for variable, prefix, where in KEYS:
    value = os.environ.get(variable, "")
    if not value:
        record("FAIL", variable, f"missing — create one at {where}")
    elif not value.startswith(prefix):
        record("FAIL", variable, f"should start with {prefix!r} — check you copied it whole")
    else:
        record("OK", variable, f"{value[:6]}…")


# %%
def check_chat(name, base_url, api_key, model, failure="FAIL"):
    """Send one tiny prompt and record the answer and the time it took."""
    try:
        client = OpenAI(base_url=base_url, api_key=api_key, timeout=120, max_retries=0)
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with the single word: ready"}],
        )
        elapsed = time.time() - start
        answer = (response.choices[0].message.content or "").strip()
        record("OK", name, f"{model} answered {answer[:20]!r} in {elapsed:.1f} s")
    except Exception as error:
        record(failure, name, f"{type(error).__name__}: {str(error)[:120]}")


if os.environ.get("GROQ_API_KEY"):
    check_chat(
        "Groq call",
        "https://api.groq.com/openai/v1",
        os.environ["GROQ_API_KEY"],
        "openai/gpt-oss-20b",
    )
else:
    record("FAIL", "Groq call", "skipped — no GROQ_API_KEY")

if os.environ.get("GEMINI_API_KEY"):
    check_chat(
        "Gemini call",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
        os.environ["GEMINI_API_KEY"],
        "gemini-3.5-flash-lite",
    )
else:
    record("FAIL", "Gemini call", "skipped — no GEMINI_API_KEY")

# %% [markdown]
# ## 4. Local model — optional
#
# Needs the Ollama application running and `ollama pull llama3.2:3b`.
# Skip it if your laptop has less than 8 GB of memory: a `WARN` here is
# fine, you will use the Groq API instead.

# %%
check_chat(
    "Ollama llama3.2:3b",
    "http://localhost:11434/v1",
    "ollama",
    "llama3.2:3b",
    failure="WARN",
)

# %% [markdown]
# ## Result

# %%
failures = [name for status, name, _ in results if status == "FAIL"]
warnings = [name for status, name, _ in results if status == "WARN"]

print()
if failures:
    print("NOT READY — fix these before 9 November:")
    for name in failures:
        print(f"  - {name}")
    print("Help: see README.md in this folder, or send this output to the trainer.")
else:
    print("READY")
    if warnings:
        print(f"Optional parts missing: {', '.join(warnings)}. You can follow the module without them.")
