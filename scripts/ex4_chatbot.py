"""Exercise 4, next step: a chatbot on the full base.

The base: the 9 documents of exercise 4, plus the indications of the 1 564 medicines
authorised in the EU (EMA). The same search and the same prompt as in the notebook,
in a loop. The model receives the full conversation history with each question.

Run it from the course folder:
    uv run python scripts/ex4_chatbot.py          # API (Groq)
    uv run python scripts/ex4_chatbot.py local    # local model (Ollama)
An empty line to quit.

To try:
1. How often is Mounjaro injected?
2. Then a follow-up question: And what are its most common side effects?
   Look at the passages found: does the search see "Mounjaro"?
3. Which medicines are indicated for Duchenne muscular dystrophy?
   The answer comes from the EMA indications: which passages?
4. What does Narvelia cost?
"""
import sys
from pathlib import Path

from openai import APIConnectionError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "notebooks"))  # to find course.py
from course import PROVIDERS, client, embed, full_index, similarity

TOP_K = 3  # number of passages put in the prompt
INSTRUCTIONS = (
    "Answer only from the passages. Cite the passage id in brackets, like [mounjaro#1]. "
    "If the answer is not in the passages, say that it is not in the documents."
)


def search(question, passages, vectors):
    """1. Search: the TOP_K passages closest to the question, with their score."""
    question_vector = embed(question)
    scores = [similarity(question_vector, vector) for vector in vectors]
    best = sorted(range(len(passages)), key=lambda index: scores[index], reverse=True)[:TOP_K]
    return [(passages[index], scores[index]) for index in best]


def make_message(question, found):
    """2. The message: the passages between tags, then the question."""
    context = "\n\n".join(f"[{passage['id']}]\n{passage['text']}" for passage, _ in found)
    return {"role": "user", "content": f"<passages>\n{context}\n</passages>\n\nQuestion: {question}"}


def ask_model(messages, provider):
    """3. Send the full conversation to the model, return its answer."""
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"], messages=messages, temperature=0, max_tokens=1000
    )
    return (response.choices[0].message.content or "").strip()


def main(provider):
    """The chatbot: provider is 'api' (Groq) or 'local' (Ollama)."""
    print("Preparing the base: 10 to 60 seconds ...")
    passages, vectors = full_index(150)
    print(f"{len(passages)} passages ready, model: {PROVIDERS[provider]['model']}. Empty line to quit.")

    messages = [{"role": "system", "content": INSTRUCTIONS}]
    while True:
        question = input("\nQuestion: ").strip()
        if not question:
            break
        found = search(question, passages, vectors)
        print("Passages: " + ", ".join(f"[{passage['id']}] {score:.2f}" for passage, score in found))
        messages.append(make_message(question, found))
        answer = ask_model(messages, provider)
        messages.append({"role": "assistant", "content": answer})  # the history grows with each turn
        print(f"Answer: {answer}")


if __name__ == "__main__":
    provider = sys.argv[1] if len(sys.argv) > 1 else "api"
    try:
        main(provider)
    except APIConnectionError:
        sys.exit(f"No connection to {PROVIDERS[provider]['base_url']}. Local: is Ollama running? API: are you online?")
