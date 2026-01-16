from fastapi import FastAPI, Header, HTTPException
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="Mini SaaS Multi-Tenant RAG API")

# -----------------------------
# API Keys → Clients
# -----------------------------
API_KEYS = {
    "tenantA_key": "clientA",
    "tenantB_key": "clientB",
}

# -----------------------------
# Paths
# -----------------------------
BASE_DATA_PATH = Path("data")

# -----------------------------
# LLM (lightweight & local)
# -----------------------------
MODEL_NAME = "EleutherAI/gpt-neo-125M"

llm_pipeline = pipeline(
    "text-generation",
    model=MODEL_NAME,
    max_length=256,
    do_sample=True,
    temperature=0.3,
)

# -----------------------------
# RAG Storage
# -----------------------------
RAG_SYSTEMS = {}

# -----------------------------
# Load documents per client
# -----------------------------
for _, client in API_KEYS.items():
    client_path = BASE_DATA_PATH / client
    if not client_path.exists():
        continue

    documents = []
    doc_names = []

    for file in client_path.glob("*.txt"):
        documents.append(file.read_text(encoding="utf-8"))
        doc_names.append(file.name)

    if not documents:
        continue

    vectorizer = TfidfVectorizer(
        stop_words=None,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(documents)

    RAG_SYSTEMS[client] = {
        "docs": documents,
        "doc_names": doc_names,
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
    }

# -----------------------------
# API key validation
# -----------------------------
def get_client_from_api_key(api_key: str) -> str:
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[api_key]

# -----------------------------
# API Endpoint
# -----------------------------
@app.get("/answer")
def get_answer(question: str, x_api_key: str = Header(...)):
    client = get_client_from_api_key(x_api_key)

    if client not in RAG_SYSTEMS:
        raise HTTPException(status_code=404, detail="No documents for this client")

    system = RAG_SYSTEMS[client]

    q_vec = system["vectorizer"].transform([question])
    similarities = cosine_similarity(q_vec, system["tfidf_matrix"])[0]

    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])

    # 🔽 seuil réaliste pour petits documents
    if best_score < 0.20:
        return {
            "answer": "Aucune réponse possible pour ce client.",
            "confidence": best_score,
        }

    context = system["docs"][best_idx]

    prompt = f"""
You are a professional assistant.
Answer ONLY using the information below.
If the answer is not present, say:
"Aucune réponse possible pour ce client."

DOCUMENT:
{context}

QUESTION:
{question}

ANSWER:
"""

    raw = llm_pipeline(prompt)[0]["generated_text"]
    answer = raw.split("ANSWER:")[-1].strip()

    return {
        "answer": answer,
        "source_document": system["doc_names"][best_idx],
        "confidence": round(best_score, 3),
    }
