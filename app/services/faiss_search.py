# app/services/faiss_search.py
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

_index = None
_meta = None
_model = None

def load_resources():
    global _index, _meta, _model
    if _index is None:
        print("Loading FAISS index...", settings.FAISS_INDEX_PATH)
        _index = faiss.read_index(settings.FAISS_INDEX_PATH)
    if _meta is None:
        with open(settings.FAISS_META_PATH, "rb") as f:
            _meta = pickle.load(f)
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)

def search_text(query, top_k=5):
    load_resources()
    q_emb = _model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    D, I = _index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(_meta):
            continue
        item = _meta[idx].copy()
        item["score"] = float(score)
        results.append(item)
    return results
