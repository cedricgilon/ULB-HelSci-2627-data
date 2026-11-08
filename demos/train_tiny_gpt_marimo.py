import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Train a tiny GPT on medical text

    Block A · optional · 1–5 min of training on a laptop CPU · no API, no key.

    In the lecture you saw how a model is trained: predict the next token,
    compare with the real one, adjust the weights, repeat. Here you do it
    yourself, with a very small model, on medical text.

    The model code is nanoGPT's, by Andrej Karpathy (`nanogpt_model.py`,
    MIT licence). It is the same kind of model as GPT-2, only much smaller.

    Run the cells in order. The training cell prints its progress.
    """)
    return


@app.cell
def _():
    import math
    import re
    import time
    from pathlib import Path

    import matplotlib.pyplot as plt
    import torch

    from nanogpt_model import GPT, GPTConfig

    return GPT, GPTConfig, Path, math, plt, re, time, torch


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The text

    The indications of the 1 564 medicines authorised in the EU, from the
    European Medicines Agency: about 600 000 characters. Each entry starts
    with `Medicine:`.
    """)
    return


@app.cell
def _(Path):
    PROMPT = "Medicine: "
    text = (Path(__file__).resolve().parent.parent / "data" / "train" / "ema.txt").read_text()
    print(f"{len(text):,} characters")
    print(text[:600])
    return PROMPT, text


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Characters as tokens

    Exercise 1 used tiktoken: about 200 000 tokens, most of them word
    pieces. To keep the model tiny, here each **character** is a token.
    """)
    return


@app.cell
def _(text):
    characters = sorted(set(text))
    vocab_size = len(characters)
    char_to_id = {character: index for index, character in enumerate(characters)}
    id_to_char = {index: character for index, character in enumerate(characters)}


    def encode(string):
        return [char_to_id[character] for character in string]


    def decode(ids):
        return "".join(id_to_char[index] for index in ids)


    print(f"{vocab_size} distinct characters: {''.join(characters)!r}")
    print(encode("Medicine"))
    return decode, encode, vocab_size


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Training and validation text

    The model learns from the first 90%. The last 10% is held back to
    measure it on text it has not seen: the same idea as a test set in
    the Machine Learning module.
    """)
    return


@app.cell
def _(decode, encode, text, torch):
    torch.manual_seed(1337)
    data = torch.tensor(encode(text), dtype=torch.long)
    split = int(0.9 * len(data))
    train_data, val_data = data[:split], data[split:]

    BLOCK_SIZE = 64  # how many characters the model sees at once: its context window
    BATCH_SIZE = 12  # how many pieces of text per training step


    def get_batch(source):
        """Return BATCH_SIZE random pieces of text, and the same pieces shifted by one character."""
        starts = torch.randint(len(source) - BLOCK_SIZE, (BATCH_SIZE,))
        inputs = torch.stack([source[start:start + BLOCK_SIZE] for start in starts])
        # The targets: the same pieces, starting one character later.
        targets = torch.stack([source[start + 1:start + BLOCK_SIZE + 1] for start in starts])
        return inputs, targets


    inputs, targets = get_batch(train_data)
    print("input :", repr(decode(inputs[0].tolist())))
    print("target:", repr(decode(targets[0].tolist())))
    return BLOCK_SIZE, get_batch, inputs, targets, train_data, val_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The target is the input moved one character to the left. At every
    position, the model must predict the next character. That is all
    pretraining is.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The model

    Four layers, four attention heads, 128 numbers per token: the settings
    nanoGPT's README gives for a laptop without a GPU.
    """)
    return


@app.cell
def _(
    BLOCK_SIZE,
    GPT,
    GPTConfig,
    PROMPT,
    decode,
    encode,
    get_batch,
    torch,
    val_data,
    vocab_size,
):
    config = GPTConfig(block_size=BLOCK_SIZE, vocab_size=vocab_size,
                       n_layer=4, n_head=4, n_embd=128, dropout=0.0, bias=False)
    model = GPT(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, betas=(0.9, 0.99))
    print(f"{model.get_num_params():,} parameters (gpt-oss-20b, the model you call on Groq, has about 21 000 000 000)")


    def sample(length=300):
        """Generate text that starts with PROMPT."""
        model.eval()
        start = torch.tensor([encode(PROMPT)], dtype=torch.long)
        with torch.no_grad():
            generated = model.generate(start, max_new_tokens=length, temperature=0.8, top_k=200)
        model.train()
        return decode(generated[0].tolist())


    @torch.no_grad()
    def validation_loss(batches=20):
        model.eval()
        losses = [model(*get_batch(val_data))[1].item() for _ in range(batches)]
        model.train()
        return sum(losses) / len(losses)

    return model, optimizer, sample, validation_loss


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The loss of an untrained model

    The loss measures how surprised the model is by the real next
    character. **Sanity check:** an untrained model guesses uniformly
    among the `vocab_size` characters, so its loss should be close to
    ln(`vocab_size`). If it is far off, something is wrong before
    training even starts.
    """)
    return


@app.cell
def _(inputs, math, model, targets, vocab_size):
    # The loss of the untrained model on the batch above, and ln(vocab_size).
    _, untrained_loss = model(inputs, targets)
    expected_loss = math.log(vocab_size)
    print(f"untrained loss: {untrained_loss.item():.2f}   ln({vocab_size}) = {expected_loss:.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Before any training, the weights are random. What does it write?
    """)
    return


@app.cell
def _(sample):
    print(sample(200))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Train

    2 000 steps. Each step: predict, measure the error (the *loss*), adjust
    every weight a little. The cell keeps a sample at steps 1, 100, 500 and
    2 000. About one minute on a recent laptop, a few minutes on an older one.
    """)
    return


@app.cell
def _(get_batch, model, optimizer, sample, time, train_data, validation_loss):
    MAX_STEPS = 2000
    SAMPLE_AT = [1, 100, 500, 2000]

    samples = {}
    history = []
    started = time.time()
    for step in range(1, MAX_STEPS + 1):
        batch_inputs, batch_targets = get_batch(train_data)
        _, loss = model(batch_inputs, batch_targets)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if step in SAMPLE_AT or step % 250 == 0:
            history.append((step, validation_loss()))
            print(f"step {step:>5}   validation loss {history[-1][1]:.2f}   {time.time() - started:.0f} s")
        if step in SAMPLE_AT:
            samples[step] = sample()
    return MAX_STEPS, history, samples


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What it learned, step by step
    """)
    return


@app.cell
def _(samples):
    for sample_step, generated in samples.items():
        print(f"=== after {sample_step} steps\n{generated}\n")
    return


@app.cell
def _(history, plt):
    steps, losses = zip(*history)
    plt.plot(steps, losses, marker="o")
    plt.xlabel("training step")
    plt.ylabel("validation loss")
    plt.title("Tiny GPT on ema.txt")
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Questions.**
    1. In what order does the structure appear: characters, words, the
       entry layout, medical vocabulary?
    2. Does the last sample read like a real entry? Is it true?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Is it real?

    The model writes medicine names with confidence. Check each one
    against the corpus it was trained on.
    """)
    return


@app.cell
def _(MAX_STEPS, re, sample, samples, text):
    for name in re.findall(r"Medicine: (\w+)", samples[MAX_STEPS] + sample(600)):
        status = "in the corpus" if name in text else "INVENTED"
        print(f"{status:<14} {name}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Questions.**
    1. The model has never seen an invented name. Why does it write one
       with the same confidence as a real one?
    2. A large model has read far more, so it invents less often. Does
       that make an invented answer easier or harder to notice?

    This is a *hallucination*: not a bug, but what next-token prediction
    does when it continues a pattern beyond what it learned.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Generate text, by hand

    `sample()` used nanoGPT's `generate`. Here is the same loop, written out. At each
    step the model gives one score per character for the next position;
    divide by the temperature, turn the scores into probabilities with a
    softmax, draw one character, append it, repeat.
    """)
    return


@app.cell
def _(BLOCK_SIZE, PROMPT, decode, encode, model, torch):
    def generate_text(prompt, length=200, temperature=0.8):
        """Continue prompt by drawing one character at a time."""
        ids = torch.tensor([encode(prompt)], dtype=torch.long)
        model.eval()
        with torch.no_grad():
            for _ in range(length):
                logits, _ = model(ids[:, -BLOCK_SIZE:])
                scores = logits[0, -1]  # one score per character, for the next position
                # Divide the scores by the temperature, apply a softmax, then draw one id.
                probabilities = torch.softmax(scores / temperature, dim=-1)
                next_id = torch.multinomial(probabilities, num_samples=1)
                ids = torch.cat([ids, next_id.view(1, 1)], dim=1)
        model.train()
        return decode(ids[0].tolist())


    for temperature in [0.2, 0.8, 1.5]:
        print(f"=== temperature {temperature}\n{generate_text(PROMPT, temperature=temperature)}\n")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Question.** As in exercise 2 of the course: what happens to the text
    at a low temperature, and at a high one?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Extension

    - Set `MAX_STEPS = 5000`. Does the validation loss keep going down?
    - Set `PROMPT = "Medicine: Keytruda"`. Does it continue with the real
      indication, or invent one?

    Source and licence of the text: `../data/README.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
