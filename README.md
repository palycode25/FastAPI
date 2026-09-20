# API FastAPI – Génération de QCM

## Description

API REST que j'ai développée avec **FastAPI** pour générer des questionnaires à choix multiples (QCM) à partir d'une banque de questions, avec gestion de cette banque via un accès administrateur. J'y ai mis en œuvre une authentification Basic, une gestion fine des erreurs (401, 403, 404, 400) et une validation des données avec Pydantic.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `main.py` | Code source de l'API FastAPI |
| `questions.csv` | Banque de questions (subject, use, réponses, réponse correcte) |
| `requirements.txt` | Dépendances Python du projet |
| `requests.txt` | Exemples de requêtes `curl` pour tester l'API |

## Installation

```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
uvicorn main:app --reload
```

L'API est ensuite disponible sur `http://localhost:8000`.

## Authentification

L'API utilise l'authentification **HTTP Basic** (`Authorization: Basic <base64(username:password)>`) pour l'endpoint `/generate_quiz`.

Utilisateurs autorisés :

| Utilisateur | Mot de passe |
|---|---|
| alice | wonderland |
| bob | builder |
| clementine | mandarine |

L'endpoint `/create_question` est protégé par des identifiants **admin** transmis dans le corps de la requête (`admin_username` / `admin_password`).

## Endpoints

### `GET /verify`
Vérifie que l'API est fonctionnelle.

**Réponse**
```json
{ "message": "L'API est fonctionnelle." }
```

---

### `POST /generate_quiz`
Génère un QCM aléatoire selon un type de test et une ou plusieurs catégories.

**Authentification requise** (Basic Auth)

**Corps de la requête**
```json
{
  "test_type": "Test de positionnement",
  "categories": ["BDD"],
  "number_of_questions": 5
}
```

**Règles de validation**
- `number_of_questions` doit être **5, 10 ou 20**
- Renvoie **404** si aucune question ne correspond aux critères
- Renvoie **400** si le nombre de questions demandé dépasse le nombre disponible
- Renvoie **401** si l'authentification est absente ou incorrecte

---

### `POST /create_question`
Ajoute une nouvelle question à la banque (accès admin).

**Corps de la requête**
```json
{
  "admin_username": "admin",
  "admin_password": "4dm1N",
  "question": "Quelle est la capitale de la France ?",
  "subject": "Data Science",
  "correct": "B",
  "use": "Test de positionnement",
  "responseA": "Londres",
  "responseB": "Paris",
  "responseC": "Berlin"
}
```

Renvoie **403** si les identifiants admin sont incorrects.

## Exemples de tests (curl)

```bash
# 1. Vérifier que l'API est fonctionnelle
curl -X GET http://localhost:8000/verify

# 2. Générer un QCM (alice:wonderland en Base64 = YWxpY2U6d29uZGVybGFuZA==)
curl -X POST http://localhost:8000/generate_quiz \
  -H "Authorization: Basic YWxpY2U6d29uZGVybGFuZA==" \
  -H "Content-Type: application/json" \
  -d "{\"test_type\": \"Test de positionnement\", \"categories\": [\"BDD\"], \"number_of_questions\": 5}"

# 3. Créer une nouvelle question (admin)
curl -X POST http://localhost:8000/create_question \
  -H "Content-Type: application/json" \
  -d "{\"admin_username\": \"admin\", \"admin_password\": \"4dm1N\", \"question\": \"Quelle est la capitale de la France ?\", \"subject\": \"Data Science\", \"correct\": \"B\", \"use\": \"Test de positionnement\", \"responseA\": \"Londres\", \"responseB\": \"Paris\", \"responseC\": \"Berlin\"}"

# 4. Test authentification incorrecte (doit renvoyer 401)
curl -X POST http://localhost:8000/generate_quiz \
  -H "Authorization: Basic bWF1dmFpczptZHA=" \
  -H "Content-Type: application/json" \
  -d "{\"test_type\": \"Test de positionnement\", \"categories\": [\"BDD\"], \"number_of_questions\": 5}"

# 5. Test avec catégorie inexistante (doit renvoyer 404)
curl -X POST http://localhost:8000/generate_quiz \
  -H "Authorization: Basic YWxpY2U6d29uZGVybGFuZA==" \
  -H "Content-Type: application/json" \
  -d "{\"test_type\": \"Test de positionnement\", \"categories\": [\"Inexistant\"], \"number_of_questions\": 5}"
```

## Choix techniques

- **FastAPI** pour la légèreté du framework et la validation automatique des schémas via **Pydantic**.
- Authentification **HTTP Basic** encodée en Base64, gérée manuellement pour un contrôle explicite des codes d'erreur.
- Les données sont chargées en mémoire (**pandas**) depuis `questions.csv` au démarrage de l'API ; la création de question modifie ce DataFrame en mémoire (`global df`).
- Gestion des valeurs manquantes (`NaN`) avant sérialisation JSON pour éviter les erreurs de format sur les réponses optionnelles (`responseD`).

## Dépendances

Voir `requirements.txt` (FastAPI, Uvicorn, Pandas, Pydantic).
