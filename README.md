# Introduction to LLMs

HeLSci · @data training · 9–10 November 2026 · Brachet AW1.203

## 1. Get the files

```sh
git clone https://github.com/cedricgilon/ULB-HelSci-2627-data.git
cd ULB-HelSci-2627-data
```

Without git: on the GitHub page, **Code → Download ZIP**, then unzip it.

## 2. Install

Run all commands in a terminal, in this folder.

1. Install uv, if you do not have it yet: <https://docs.astral.sh/uv/getting-started/installation/>
2. Install the packages (about 10 minutes, mostly downloads):

   ```sh
   uv venv
   uv pip install -r requirements.txt
   ```

3. Make two free API keys, with no payment card:
   - **Groq** at <https://console.groq.com> (Groq with a **q**: Grok with a k is a different product)
   - **Google AI Studio** at <https://aistudio.google.com>
4. Make a file named `.env` in **this** folder (the one with `requirements.txt`), with your two keys:

   ```
   GROQ_API_KEY=gsk_...
   GEMINI_API_KEY=...
   ```

5. Run the check, until you see **READY**:

   ```sh
   uv run python 00-install-check/install_check.py
   ```

A `FAIL` line? The fixes are in `00-install-check/README.md`. If that does not help, show the output to the trainer.

Optional, the local model: install Ollama (<https://ollama.com>), then `ollama pull llama3.2:3b`. Not recommended with less than 8 GB of memory: Groq is enough for everything.

## 3. Contents

| Folder | Contents |
|---|---|
| `00-install-check/` | the install check |
| `notebooks/` | the exercises, one marimo notebook each (`ex1_tokens.py` … `ex7_project.py`), with `course.py` and `checks.py` |
| `scripts/` | two Python scripts to run in the terminal: `ex2_call.py` (one call to the model, with a temperature) and `ex4_chatbot.py` (a chatbot on the medicine documents) |
| `demos/` | the base model vs chat model demo, and an optional notebook to train a mini-GPT |
| `slides/` | the slides of the two days, as PDF |
| `data/` | the abstracts, the medicine documents, the training text: sources and licences in `data/README.md` |

Keep the folder structure as it is: the notebooks read their data from `../data/`.

## 4. Open an exercise

```sh
uv run marimo edit notebooks/ex1_tokens.py
```

marimo does not run a notebook when it opens: click **Run all** once (bottom right).

### In an exercise

- Change the data: a text box, a slider, a list
- Write the line marked `# TODO`. A hint is in the closed box below it
- After each part, a check shows ✅ right, ⏳ still to do, or ❌ not yet, with a hint
- The model is called only when you click its ▶ button
- Finished early? There is an option at the end of each notebook
- The solutions are shared after the session

## 5. Run a script

```sh
uv run python scripts/ex2_call.py 0            # Groq, temperature 0
uv run python scripts/ex2_call.py 1.5 local    # Ollama, temperature 1.5
uv run python scripts/ex4_chatbot.py           # the chatbot, with Groq
uv run python scripts/ex4_chatbot.py local     # the chatbot, with Ollama
```

What to try is written at the top of each script.

## Privacy

- Never put your API keys in a notebook. They stay in `.env`
- The exercises send text to Groq and to Google. Use only the data given here, or public data. **No personal or confidential data**
