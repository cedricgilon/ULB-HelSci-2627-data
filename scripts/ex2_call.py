"""Exercise 2, next step: call the model, with a temperature.

The same prompt, 5 times, at the temperature you choose.

Run, from the course folder:
    uv run python scripts/ex2_call.py 0          # API (Groq), temperature 0
    uv run python scripts/ex2_call.py 1.5        # API (Groq), temperature 1.5
    uv run python scripts/ex2_call.py 1.5 local  # local model (Ollama)

Try:
1. The prompt below, at 0 then at 1.5: does a short, factual answer change?
2. Change PROMPT: "Give one name for a new medicine against migraine. Answer with the name only."
   At 0, then at 1.5: how many different answers?
"""
import sys
from pathlib import Path

from openai import APIConnectionError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "notebooks"))  # to find course.py
from course import PROVIDERS, client, normalise

PROMPT = "What is the most common side effect of metformin? Answer in two words."
RUNS = 5


def call_model(prompt, temperature, provider):
    """One call to the model: one message, one temperature, one answer."""
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1000,  # a safety limit: stops an answer that does not end
    )
    return (response.choices[0].message.content or "").strip()


def main(temperature, provider):
    """The same prompt RUNS times, then the number of different answers."""
    print(f"{PROVIDERS[provider]['model']}, temperature {temperature}\n")
    answers = [call_model(PROMPT, temperature, provider) for _ in range(RUNS)]
    for number, answer in enumerate(answers, start=1):
        print(f"{number}. {answer}")
    different = len({normalise(answer) for answer in answers})
    print(f"\n{different} different answer(s) out of {RUNS}")


if __name__ == "__main__":
    provider = sys.argv[2] if len(sys.argv) > 2 else "api"
    try:
        main(float(sys.argv[1]) if len(sys.argv) > 1 else 0.0, provider)
    except APIConnectionError:
        sys.exit(f"No connection to {PROVIDERS[provider]['base_url']}. Local: is Ollama running? API: are you online?")
