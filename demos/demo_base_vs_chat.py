# %% [markdown]
# # Demo: base model vs chat model
#
# Block A · trainer demo, 10 min. Learners can run it too: no API, no
# key. Downloads two models of about 700 MB each on first run.
#
# Two models of the **same size**: 360 million parameters, same
# tokenizer, same pretraining. The only difference: the second one was
# post-trained to behave as an assistant. So what you see is the effect
# of post-training alone.
#
# Models: SmolLM2-360M and SmolLM2-360M-Instruct, by Hugging Face,
# Apache 2.0 licence. Idea from Yann-Aël Le Borgne's SustAIn.Brussels
# course (April 2026), notebook "Chat templates". Qwen2.5-0.5B was tried
# first: its base model already answers and stops, so it hides the
# difference.

# %%
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "HuggingFaceTB/SmolLM2-360M"
CHAT = "HuggingFaceTB/SmolLM2-360M-Instruct"
PROMPT = "What is the capital of Belgium?"

# %% [markdown]
# ## Part 1: What the chat model really reads
#
# You send a list of messages. The model reads one text. The *chat
# template* turns the list into that text, with special tokens that
# mark who speaks.

# %%
tokenizer = AutoTokenizer.from_pretrained(CHAT)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": PROMPT},
]
chat_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
print(chat_text)

# %% [markdown]
# **What to point out.** `<|im_start|>` and `<|im_end|>` are single
# tokens. The text ends with `<|im_start|>assistant`: the model's job is
# still to predict the next token, and the most likely continuation
# after that marker is an assistant's answer. The API you call in the
# exercises builds this text for you.

# %%
def generate(model, text, max_new_tokens=60):
    """Continue text greedily and return only the new part."""
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs, do_sample=False, max_new_tokens=max_new_tokens,
                                pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


base_model = AutoModelForCausalLM.from_pretrained(BASE)
chat_model = AutoModelForCausalLM.from_pretrained(CHAT)
print(f"base: {base_model.num_parameters():,} parameters   chat: {chat_model.num_parameters():,} parameters")

# %% [markdown]
# ## Part 2: The same question, raw text, to both

# %%
print(f"--- base model ---\n{PROMPT}{generate(base_model, PROMPT)}\n")
print(f"--- chat model, same raw text ---\n{PROMPT}{generate(chat_model, PROMPT)}\n")

# %% [markdown]
# ## Part 3: The chat model with its template

# %%
print(f"--- chat model, with the chat template ---\n{generate(chat_model, chat_text)}")

# %% [markdown]
# **What to point out.** The base model gives the answer (its training
# text holds many question-and-answer pages), but it does not stop: it
# continues the *document*, repeating question and answer like a FAQ
# page. The chat model, given raw text, stops at once; given its
# template, it answers and stops. Same size, same knowledge: the habit
# of answering, and of stopping, comes from post-training.
