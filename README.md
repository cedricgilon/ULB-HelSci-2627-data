# Introduction aux LLM: learner files

HeLSci · Formation @data · 9–10 November 2026 · Brachet AW1.203

Keep the folder structure as it is: the notebooks read their data from `../data/`.

## Get the files

```sh
git clone https://github.com/cedricgilon/ULB-HelSci-2627-data.git
cd ULB-HelSci-2627-data
```

Without git: on the GitHub page, **Code → Download ZIP**, then unzip.

## Before the module

Follow `00-install-check/README.md`: install the packages, create your two free API keys, put them in a file named `.env` in **this** folder, and run the check until it prints **READY**.

## What is inside

| Folder | Content |
|---|---|
| `00-install-check/` | the install check: run it at home |
| `notebooks/` | the exercises, one marimo notebook each (`ex1_tokens.py` … `ex7_project.py`), with `course.py` and `checks.py` |
| `demos/` | the base-vs-chat demo and an optional tiny-GPT training notebook |
| `slides/` | the slides of both days, PDF |
| `data/` | the abstracts, the medicine documents, the training text: sources and licences in `data/README.md` |

## Open an exercise

In a terminal, in this folder:

```sh
source .venv/bin/activate        # Windows: .venv\Scripts\activate
marimo edit notebooks/ex1_tokens.py
```

marimo does not run a notebook when it opens it: press **Run all** once (bottom right).

## In an exercise

- Change the data: a text box, a slider, a list
- Write the one line marked `# TODO`; a hint is in the closed box below it
- After each part, a check shows ✅ right, ⏳ still to do, or ❌ not yet, with a hint
- A model is called only when you press its ▶ button
- Finished early? An option at the end of each notebook
- Solutions are shared after the session

## Rules

- Never put your API keys in a notebook. They stay in `.env`
- The exercises send text to Groq and Google. Use only the data given here, or public data. **No personal or confidential data**
