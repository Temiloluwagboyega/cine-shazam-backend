import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.db.database import db
import asyncio

subtitles_coll = db["subtitles"]

async def load_batch(skip, limit):
    """Fetch a batch of subtitles with skip+limit from Mongo."""
    cursor = subtitles_coll.find({}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return docs

def build_faiss(batch_size=512, fetch_size=2000):
    print("📥 Building FAISS index in streaming mode...")

    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    d = model.get_sentence_embedding_dimension()

    # FAISS index: cosine similarity (inner product on normalized embeddings)
    index = faiss.IndexFlatIP(d)
    meta = []

    loop = asyncio.get_event_loop()
    skip = 0
    total = 0

    while True:
        # fetch from Mongo in chunks
        docs = loop.run_until_complete(load_batch(skip, fetch_size))
        if not docs:
            break

        texts = [d.get("text", "") for d in docs if d.get("text")]
        batch_meta = [{
            "mongo_id": str(d.get("_id")),
            "movie_id": d.get("movie_id"),
            "movie_title": d.get("movie_title"),
            "start_time": d.get("start_time"),
            "end_time": d.get("end_time"),
            "text": d.get("text")
        } for d in docs if d.get("text")]

        # Encode in sub-batches to keep memory small
        embeddings = []
        for i in range(0, len(texts), batch_size):
            sub_batch = texts[i:i+batch_size]
            emb = model.encode(sub_batch, convert_to_numpy=True,
                               normalize_embeddings=True).astype("float16")
            embeddings.append(emb)

        if embeddings:
            embeddings = np.vstack(embeddings)
            index.add(embeddings)
            meta.extend(batch_meta)

        total += len(batch_meta)
        skip += fetch_size
        print(f"   → Processed {total} subtitles...")

    # Save final FAISS + meta
    faiss.write_index(index, settings.FAISS_INDEX_PATH)
    with open(settings.FAISS_META_PATH, "wb") as f:
        pickle.dump(meta, f)

    print("✅ Done!")
    print(f"   → Subtitles indexed: {total}")
    print(f"   → FAISS: {settings.FAISS_INDEX_PATH}")
    print(f"   → Meta: {settings.FAISS_META_PATH}")
