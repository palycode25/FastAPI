from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import base64

app = FastAPI()

# Chargement des données
df = pd.read_csv("questions.csv")

# Utilisateurs autorisés
USERS = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine"
}

# Admin
ADMIN = {"username": "admin", "password": "4dm1N"}


# --- Authentification Basic ---
def authenticate(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Authentification requise.")
    try:
        decoded = base64.b64decode(authorization[6:]).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Format d'authentification invalide.")

    if USERS.get(username) != password:
        raise HTTPException(status_code=401, detail="Identifiants incorrects.")
    return username


# --- Modèles Pydantic ---
class QuizRequest(BaseModel):
    test_type: str
    categories: List[str]
    number_of_questions: int

class QuestionCreate(BaseModel):
    admin_username: str
    admin_password: str
    question: str
    subject: str
    correct: str
    use: str
    responseA: str
    responseB: str
    responseC: str
    responseD: Optional[str] = None


# --- Endpoints ---

# 1. GET /verify
@app.get("/verify")
def verify():
    return {"message": "L'API est fonctionnelle."}


# 2. POST /generate_quiz
@app.post("/generate_quiz")
def generate_quiz(payload: QuizRequest, authorization: Optional[str] = Header(None)):
    # Authentification
    authenticate(authorization)

    # Validation du nombre de questions
    if payload.number_of_questions not in [5, 10, 20]:
        raise HTTPException(status_code=400, detail="Le nombre de questions doit être 5, 10 ou 20.")

    # Filtrage par type de test et catégories
    filtered = df[
        (df["use"] == payload.test_type) &
        (df["subject"].isin(payload.categories))
    ]

    if filtered.empty:
        raise HTTPException(status_code=404, detail="Aucune question ne correspond aux critères.")

    if len(filtered) < payload.number_of_questions:
        raise HTTPException(
            status_code=400,
            detail=f"Seulement {len(filtered)} questions disponibles pour ces critères."
        )

    # Sélection aléatoire
    sample = filtered.sample(n=payload.number_of_questions)

    # Nettoyage des NaN pour le JSON
    return sample.where(pd.notnull(sample), None).to_dict(orient="records")


# 3. POST /create_question
@app.post("/create_question")
def create_question(payload: QuestionCreate):
    global df

    # Vérification admin
    if payload.admin_username != ADMIN["username"] or payload.admin_password != ADMIN["password"]:
        raise HTTPException(status_code=403, detail="Accès refusé. Identifiants admin incorrects.")

    # Ajout de la nouvelle question
    new_row = {
        "question":  payload.question,
        "subject":   payload.subject,
        "correct":   payload.correct,
        "use":       payload.use,
        "responseA": payload.responseA,
        "responseB": payload.responseB,
        "responseC": payload.responseC,
        "responseD": payload.responseD,
        "remark":    None
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    return {"message": "Question créée avec succès."}
