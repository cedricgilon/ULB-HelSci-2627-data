# Introduction aux LLM

HeLSci · Formation @data · 9–10 novembre 2026 · Brachet AW1.203

## 1. Récupérer les fichiers

```sh
git clone https://github.com/cedricgilon/ULB-HelSci-2627-data.git
cd ULB-HelSci-2627-data
```

Sans git : sur la page GitHub, **Code → Download ZIP**, puis décompressez.

## 2. Installer

Toutes les commandes se lancent dans un terminal, dans ce dossier.

1. Installez uv, si ce n'est pas déjà fait : <https://docs.astral.sh/uv/getting-started/installation/>
2. Installez les paquets (environ 10 minutes, surtout des téléchargements) :

   ```sh
   uv venv
   uv pip install -r requirements.txt
   ```

3. Créez deux clés API gratuites, sans carte de paiement :
   - **Groq** sur <https://console.groq.com> (Groq avec un **q**, Grok avec un k est un autre produit)
   - **Google AI Studio** sur <https://aistudio.google.com>
4. Créez un fichier nommé `.env` dans **ce** dossier (celui de `requirements.txt`), avec vos deux clés :

   ```
   GROQ_API_KEY=gsk_...
   GEMINI_API_KEY=...
   ```

5. Lancez la vérification, jusqu'à **READY** :

   ```sh
   uv run python 00-install-check/install_check.py
   ```

Une ligne `FAIL` ? Les solutions sont dans `00-install-check/README.md` (en anglais). Sinon, montrez la sortie au formateur.

Optionnel, le modèle local : installez Ollama (<https://ollama.com>), puis `ollama pull llama3.2:3b`. À éviter avec moins de 8 Go de mémoire : Groq suffit pour tout.

## 3. Le contenu

| Dossier | Contenu |
|---|---|
| `00-install-check/` | la vérification de l'installation |
| `notebooks/` | les exercices, un notebook marimo chacun (`ex1_tokens.py` … `ex7_project.py`), avec `course.py` et `checks.py` |
| `scripts/` | deux scripts Python à lancer dans le terminal : `ex2_call.py` (un appel au modèle, avec une température) et `ex4_chatbot.py` (un chatbot sur les documents de médicaments) |
| `demos/` | la démo modèle de base vs modèle chat, et un notebook optionnel pour entraîner un mini-GPT |
| `slides/` | les slides des deux jours, en PDF |
| `data/` | les résumés, les documents de médicaments, le texte d'entraînement : sources et licences dans `data/README.md` |

Gardez la structure des dossiers telle quelle : les notebooks lisent leurs données dans `../data/`.

## 4. Ouvrir un exercice

```sh
uv run marimo edit notebooks/ex1_tokens.py
```

marimo n'exécute pas un notebook à l'ouverture : cliquez une fois sur **Run all** (en bas à droite).

### Dans un exercice

- Changez les données : une zone de texte, un curseur, une liste
- Écrivez la ligne marquée `# TODO`. Un indice est dans la boîte fermée en dessous
- Après chaque partie, une vérification affiche ✅ juste, ⏳ encore à faire, ou ❌ pas encore, avec un indice
- Le modèle n'est appelé que quand vous cliquez sur son bouton ▶
- Fini en avance ? Une option à la fin de chaque notebook
- Les solutions sont partagées après la séance

## 5. Lancer un script

```sh
uv run python scripts/ex2_call.py 0            # Groq, température 0
uv run python scripts/ex2_call.py 1.5 local    # Ollama, température 1,5
uv run python scripts/ex4_chatbot.py           # le chatbot, avec Groq
uv run python scripts/ex4_chatbot.py local     # le chatbot, avec Ollama
```

Ce qu'il faut essayer est écrit en haut de chaque script.

## Confidentialité

- Ne mettez jamais vos clés API dans un notebook. Elles restent dans `.env`
- Les exercices envoient du texte à Groq et à Google. Utilisez seulement les données fournies ici, ou des données publiques. **Pas de données personnelles ou confidentielles**
