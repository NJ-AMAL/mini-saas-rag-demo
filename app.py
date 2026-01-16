from fastapi import FastAPI, Header, HTTPException
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI(title="Mini SaaS Multi-Tenant RAG API (Free Demo)")

# -----------------------------
# Configuration
# -----------------------------
API_KEYS = {
    "tenantA_key": "clientA",
    "tenantB_key": "clientB",
}

BASE_DATA_PATH = Path("data")
VECTOR_STORE_PATH = Path("vector_store")
VECTOR_STORE_PATH.mkdir(exist_ok=True)

# Dictionary to store TF-IDF systems per client
RAG_SYSTEMS = {}

# -----------------------------
# Initialize RAG per tenant (TF-IDF embeddings)
# -----------------------------
for tenant, client in API_KEYS.items():
    client_path = BASE_DATA_PATH / client
    if not client_path.exists():
        continue

    documents = []
    for file in client_path.glob("*.txt"):
        documents.append(file.read_text(encoding="utf-8"))

    if not documents:
        continue

    # Create TF-IDF vectorizer and matrix
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Store per client
    RAG_SYSTEMS[client] = {
        "docs": documents,
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix
    }

# -----------------------------
# Helper function
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
        raise HTTPException(status_code=404, detail="No documents available for this client")

    vectorizer = RAG_SYSTEMS[client]["vectorizer"]
    tfidf_matrix = RAG_SYSTEMS[client]["tfidf_matrix"]
    docs = RAG_SYSTEMS[client]["docs"]

    # Transform the question
    q_vec = vectorizer.transform([question])

    # Compute cosine similarity
    similarities = cosine_similarity(q_vec, tfidf_matrix)
    best_idx = np.argmax(similarities)
    answer = docs[best_idx]

    return {"answer": answer}
