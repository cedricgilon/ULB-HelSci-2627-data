# Introduction aux LLM

HeLSci · Formation @data · 9–10 November 2026 · Brachet AW1.203

## 1. Get the files

```sh
git clone https://github.com/cedricgilon/ULB-HelSci-2627-data.git
cd ULB-HelSci-2627-data
```

Without git: on the GitHub page, **Code → Download ZIP**, then unzip.

## 2. Install check

Follow `00-install-check/README.md`: install the packages, create your two free API keys, put them in a file named `.env` in **this** folder, and run the check until it prints **READY**.

## 3. What is inside

| Folder | Content |
|---|---|
| `00-install-check/` | the install check: run it first |
| `notebooks/` | the exercises, one marimo notebook each (`ex1_tokens.py` … `ex7_project.py`), with `course.py` and `checks.py` |
| `scripts/` | two Python scripts to run in the terminal: `ex2_call.py` (one model call, with a temperature) and `ex4_chatbot.py` (a chatbot on the medicine documents) |
| `demos/` | the base-vs-chat demo and an optional tiny-GPT training notebook |
| `slides/` | the slides of both days, PDF |
| `data/` | the abstracts, the medicine documents, the training text: sources and licences in `data/README.md` |

Note: keep the folder structure as it is: the notebooks read their data from `../data/`.

## 4. Open an exercise

In a terminal, in this folder:

Mac or Linux

```sh
source .venv/bin/activate
marimo edit notebooks/ex1_tokens.py
```

Windows

```sh
.venv\Scripts\activate
marimo edit notebooks/ex1_tokens.py
```

marimo does not run a notebook when it opens it: press **Run all** once (bottom right).

### In an exercise

- Change the data: a text box, a slider, a list
- Write the one line marked `# TODO`; a hint is in the closed box below it
- After each part, a check shows ✅ right, ⏳ still to do, or ❌ not yet, with a hint
- A model is called only when you press its ▶ button
- Finished early? An option at the end of each notebook
- Solutions are shared after the session

### Confidentiality note

- Never put your API keys in a notebook. They stay in `.env`
- The exercises send text to Groq and Google. Use only the data given here, or public data. **No personal or confidential data**
