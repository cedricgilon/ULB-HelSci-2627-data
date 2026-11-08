"""Exercice 2, la suite : appeler le modèle, avec une température.

Le même prompt, 5 fois, à la température que vous choisissez.

Lancer, depuis le dossier du cours :
    uv run python scripts/ex2_call.py 0          # API (Groq), température 0
    uv run python scripts/ex2_call.py 1.5        # API (Groq), température 1,5
    uv run python scripts/ex2_call.py 1.5 local  # modèle local (Ollama)

À essayer :
1. Le prompt ci-dessous, à 0 puis à 1,5 : une réponse courte et factuelle change-t-elle ?
2. Changez PROMPT : "Give one name for a new medicine against migraine. Answer with the name only."
   À 0, puis à 1,5 : combien de réponses différentes ?
"""
import sys
from pathlib import Path

from openai import APIConnectionError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "notebooks"))  # pour trouver course.py
from course import PROVIDERS, client, normalise

PROMPT = "What is the most common side effect of metformin? Answer in two words."
RUNS = 5


def call_model(prompt, temperature, provider):
    """Un appel au modèle : un message, une température, une réponse."""
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1000,  # une limite de sécurité : arrête une réponse qui ne finit pas
    )
    return (response.choices[0].message.content or "").strip()


def main(temperature, provider):
    """Le même prompt RUNS fois, puis le nombre de réponses différentes."""
    print(f"{PROVIDERS[provider]['model']}, température {temperature}\n")
    answers = [call_model(PROMPT, temperature, provider) for _ in range(RUNS)]
    for number, answer in enumerate(answers, start=1):
        print(f"{number}. {answer}")
    different = len({normalise(answer) for answer in answers})
    print(f"\n{different} réponse(s) différente(s) sur {RUNS}")


if __name__ == "__main__":
    provider = sys.argv[2] if len(sys.argv) > 2 else "api"
    try:
        main(float(sys.argv[1]) if len(sys.argv) > 1 else 0.0, provider)
    except APIConnectionError:
        sys.exit(f"Pas de connexion à {PROVIDERS[provider]['base_url']}. Local : Ollama est-il lancé ? API : êtes-vous en ligne ?")
