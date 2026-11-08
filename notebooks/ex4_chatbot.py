"""Exercice 4, la suite : un chatbot sur toute la base.

La base : les 9 documents de l'exercice 4, plus les indications des 1 564 médicaments
autorisés dans l'UE (EMA). La même recherche et le même prompt que dans le notebook,
dans une boucle. Le modèle reçoit tout l'historique de la conversation à chaque question.

Lancer, depuis le dossier du cours :
    python notebooks/ex4_chatbot.py          # API (Groq)
    python notebooks/ex4_chatbot.py local    # modèle local (Ollama)
Une ligne vide pour quitter.

À essayer :
1. How often is Mounjaro injected?
2. Puis une question de suivi : And what are its most common side effects?
   Regardez les passages trouvés : la recherche voit-elle "Mounjaro" ?
3. Which medicines are indicated for Duchenne muscular dystrophy?
   La réponse vient des indications de l'EMA : quels passages ?
4. What does Narvelia cost?
"""
import sys

from openai import APIConnectionError

from course import PROVIDERS, client, embed, full_index, similarity

TOP_K = 3  # nombre de passages mis dans le prompt
INSTRUCTIONS = (
    "Answer only from the passages. Cite the passage id in brackets, like [mounjaro#1]. "
    "If the answer is not in the passages, say that it is not in the documents."
)


def search(question, passages, vectors):
    """1. Chercher : les TOP_K passages les plus proches de la question, avec leur score."""
    question_vector = embed(question)
    scores = [similarity(question_vector, vector) for vector in vectors]
    best = sorted(range(len(passages)), key=lambda index: scores[index], reverse=True)[:TOP_K]
    return [(passages[index], scores[index]) for index in best]


def make_message(question, found):
    """2. Le message : les passages entre balises, puis la question."""
    context = "\n\n".join(f"[{passage['id']}]\n{passage['text']}" for passage, _ in found)
    return {"role": "user", "content": f"<passages>\n{context}\n</passages>\n\nQuestion: {question}"}


def ask_model(messages, provider):
    """3. Envoyer toute la conversation au modèle, renvoyer sa réponse."""
    response = client(provider).chat.completions.create(
        model=PROVIDERS[provider]["model"], messages=messages, temperature=0, max_tokens=1000
    )
    return (response.choices[0].message.content or "").strip()


def main(provider):
    """Le chatbot : provider est 'api' (Groq) ou 'local' (Ollama)."""
    print("Préparation de la base : 10 à 60 secondes ...")
    passages, vectors = full_index(150)
    print(f"{len(passages)} passages prêts, modèle : {PROVIDERS[provider]['model']}. Ligne vide pour quitter.")

    messages = [{"role": "system", "content": INSTRUCTIONS}]
    while True:
        question = input("\nQuestion : ").strip()
        if not question:
            break
        found = search(question, passages, vectors)
        print("Passages : " + ", ".join(f"[{passage['id']}] {score:.2f}" for passage, score in found))
        messages.append(make_message(question, found))
        answer = ask_model(messages, provider)
        messages.append({"role": "assistant", "content": answer})  # l'historique grandit à chaque tour
        print(f"Réponse : {answer}")


if __name__ == "__main__":
    provider = sys.argv[1] if len(sys.argv) > 1 else "api"
    try:
        main(provider)
    except APIConnectionError:
        sys.exit(f"Pas de connexion à {PROVIDERS[provider]['base_url']}. Local : Ollama est-il lancé ? API : êtes-vous en ligne ?")
