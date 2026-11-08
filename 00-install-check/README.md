# Install check

Run this at home, before 9 November. It takes about ten minutes on a
home connection, most of it downloads. A laptop that ends on **READY**
is ready for the module.

## Why at home

The module needs about 4 GB per laptop: Python packages, two small
models and one local LLM. Fifteen laptops downloading that in the room
at the same time will stop the wifi. This check starts every download,
so after one green run nothing is left to fetch.

## Before you run it

1. Install the packages, as described in the mail of 17 September:

   ```sh
   uv venv
   uv pip install -r requirements.txt
   ```

2. Create two free API keys. Neither needs a payment card.

   - **Groq** at <https://console.groq.com>: Groq with a **q**. Grok
     with a k is a different product from a different company.
   - **Google AI Studio** at <https://aistudio.google.com>

3. Create a file named `.env` in the **main folder** of the module
   (the folder that holds `requirements.txt`, one level above this
   check), with your two keys. The check and every exercise look for
   it there:

   ```
   GROQ_API_KEY=gsk_...
   GEMINI_API_KEY=...
   ```

   Never share this file, never put it in a notebook, never commit it.

4. Optional: the local model. Install Ollama from <https://ollama.com>,
   then:

   ```sh
   ollama pull llama3.2:3b
   ```

   Skip this if your laptop has less than 8 GB of memory. You will use
   the Groq API for everything.

## Run it

Open `install_check.py` in VS Code and click **Run All**, or in a
terminal:

```sh
uv run python install_check.py
```

## Read the result

Each line is one check:

| Mark | Meaning |
|---|---|
| `OK` | works |
| `WARN` | optional part missing: you can follow the module without it |
| `FAIL` | required part missing: fix it before 9 November |

The last line says **READY** or lists what to fix.

## Common failures

| Line | Fix |
|---|---|
| `Python version` | install Python 3.11 to 3.14 with `uv python install 3.12` |
| a package `FAIL` | run the `uv pip install` command again, in the same folder |
| `.env file` | the file must be named `.env` exactly, with the dot, and sit next to `install_check.py` |
| `Groq call` with `401` | the key is wrong or incomplete: create a new one |
| `Groq call` with `429` | too many calls in a short time: wait one minute, run again |
| `Gemini call` with `429` | same as above |
| `Ollama` | start the Ollama application, then run again |

If a line stays red, send the full output to the trainer before
9 November.
