# Data

## `abstracts.json`: extraction corpus, exercises 5 and 6

Twenty abstracts of clinical studies, 183 to 314 words each. Each entry
has an `id` (A01 to A20), the abstract `text`, and its `source`.

### Licence

Every abstract is published under **CC BY 4.0**, except A11 under
**CC BY 3.0 Unported**. Checked on 1 November 2026 against the licence
statement in each article's full-text XML from Europe PMC, not only the
search metadata. A19 states "Creative Commons Attribution License" in
words, without a version link.

CC BY allows reuse, including in teaching, with attribution. The
`source` field of each entry carries the attribution: authors, title,
journal, year, DOI, licence. Changes made: HTML tags removed and
whitespace normalised. No word changed.

### Why these sources

The texts are sent to third-party APIs by fifteen learners, and
Google's free tier may use submitted data to improve its products. So
the corpus must be free to redistribute and must hold no personal
data. These abstracts report aggregate results only. Author names
appear in `source`, which is public bibliographic information and is
not sent to any API by the exercises.

### Selection

From 800 CC BY randomised-trial abstracts on Europe PMC (2021–2025),
chosen for length and for variety of field and design. A11 was replaced
on 1 November 2026: the previous abstract called itself both a secondary
analysis and a randomised controlled trial, so no answer key was
defensible. Several hold a
deliberate difficulty for extraction:

| id | Difficulty |
|---|---|
| A01 | 40 randomised, but 60 people studied in total |
| A02 | sample size given only as 100 + 40 |
| A04, A18 | three or four arms: one arm's n is not the total |
| A05, A20 | secondary analysis of a trial |
| A10 | title says case-control; the study is randomised |
| A12 | cluster trial: 320 areas, 87 449 women |
| A13, A17 | number randomised differs from number completed |
| A14 | cross-sectional, but part of a randomised trial project |
| A11, A19 | crossover: each participant gets both treatments (A11: 26, one withdrew; A19: 10) |

## `ground_truth.csv`: reference answers, exercise 6

Ten of the twenty abstracts, annotated by hand: A01, A04, A05, A07,
A10, A11, A12, A13, A14, A16.

| Column | Rule |
|---|---|
| `sample_size` | participants randomised, or included if not randomised, in the study the abstract reports. People, not clusters. |
| `study_design` | one of: `randomised controlled trial`, `cluster randomised trial`, `crossover trial`, `secondary analysis of a trial`, `cross-sectional study` |
| `effect_found` | did the intervention show a significant benefit on the primary outcome: `yes`, `no`, `mixed`, `not applicable` |
| `population`, `intervention`, `main_result` | short reference text, for comparison by a person or by an LLM judge |
| `note` | why the answer is what it is, where it could be argued |

`sample_size`, `study_design` and `effect_found` are compared exactly.
The three text columns cannot be, which is the point of the
LLM-as-judge step.

## `extraction_reference.csv`: the small-model extraction, exercise 6

The output of exercise 4 for all twenty abstracts, made in advance with
`llama3.2:3b` through Ollama on 1 November 2026 (A11 row redone after
the abstract was replaced), prompt v1 as in
`ex4_extraction_solution.py`. For a learner whose own extraction
failed. Against the ground truth: sample size 9/10 (A12: 87 instead of
87 449), study design 8/10 (A11's crossover and A12's cluster trial
called plain randomised trials),
effect found 9/10 (A14: "yes" for a study with no intervention).

## `output/`: learner results

Written by the exercises. Not committed.

## `rag/`: document corpus, exercise 4

Eight plain-language medicine overviews published by the European
Medicines Agency (EMA), downloaded on 1 November 2026 from
`ema.europa.eu/en/documents/overview/<name>-epar-medicine-overview_en.pdf`
(Jardiance: `jardiance-epar-summary-public_en.pdf`).

| File | Medicine | Pages | Last updated |
|---|---|---|---|
| `comirnaty.pdf` | COVID-19 vaccine | 5 | 08-2025 |
| `dupixent.pdf` | dupilumab | 6 | 03-2026 |
| `forxiga.pdf` | dapagliflozin | 3 | 01-2023 |
| `jardiance.pdf` | empagliflozin | 4 | 12-2023 |
| `keytruda.pdf` | pembrolizumab | 10 | 10-2026 |
| `mounjaro.pdf` | tirzepatide | 3 | 02-2026 |
| `wegovy.pdf` | semaglutide | 3 | 06-2026 |
| `xarelto.pdf` | rivaroxaban | 4 | 12-2020 |

Plus `narvelia.pdf`: a **fictional** one-page overview in the same
section structure, written for the course and compiled by `build.py`
from `rag/source/narvelia.typ`. It says on the page that it is
fictional and not an EMA document. Narvelia and orbistatide were
checked on 1 November 2026 against EMA's medicines list and openFDA:
neither exists. Purpose: a document no model can have seen in training.

### Licence

© European Medicines Agency. EMA's legal notice, read on 1 November
2026: documents on its website "may be reproduced and / or
distributed, totally or in part … for non-commercial and commercial
purposes, provided that EMA is always acknowledged as the source of the
material. Such acknowledgement must be included in each copy." Each PDF
also carries the line "Reproduction is authorised provided the source
is acknowledged." The PDFs are unchanged. The acknowledgement is in this
file and at the top of exercise 5.

No personal data: the overviews describe medicines and aggregate trial
results.

### `questions.json`

Fifteen test questions with verified answers, written from the
documents: twelve answerable (one needs two documents, one is a
synonym, one has two parts, one is about the fictional medicine), three
not answerable from the corpus (one a trap: Narvelia's price is
mentioned but not given). Q12–Q15 carry a `type` field. `evidence` is a phrase copied from the
document that holds the answer, used to measure retrieval without an
LLM.

## `train/ema.txt`: training text, tiny-GPT demo (`demos/`)

Built on 1 November 2026 by `train/build_corpus.py` from EMA's medicines
data (JSON, `ema.europa.eu/en/documents/report/medicines-output-medicines_json-report_en.json`):
the field `therapeutic_indication` of every authorised human medicine,
1 564 entries, 605 000 characters. Each indication is cut at about 600
characters, at a sentence end. Cleaning: HTML tags and entities
removed, whitespace collapsed, rare symbols dropped so the character
vocabulary stays at 100. The raw download stays in `train/raw/`, not
committed.

### Licence

Same legal notice as `rag/` above: reuse allowed provided EMA is
acknowledged as the source. © European Medicines Agency.

### Model code

`block-a/nanogpt_model.py` is copied unchanged from nanoGPT by Andrej
Karpathy, commit `3adf61e`, MIT licence; the notice is at the top of
the file.
