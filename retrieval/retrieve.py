import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE_DIR / "retrieval/indexes"

EMBED_MODEL = "BAAI/bge-base-en-v1.5"
model = SentenceTransformer(EMBED_MODEL)

index = faiss.read_index(str(INDEX_DIR / "trademind.index"))

with open(INDEX_DIR / "trademind_metadata.pkl", "rb") as f:
    chunks, metadata = pickle.load(f)


def retrieve(query, ticker=None, sector=None, space=None, top_k=5):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k * 5)

    results = []

    for idx in indices[0]:
        meta = metadata[idx]

        # Apply filters
        if space and meta["space"] != space:
            continue

        if ticker and meta["ticker"] != ticker:
            continue

        if sector and meta["sector"] != sector:
            continue

        results.append({
            "text": chunks[idx],
            "metadata": meta
        })

    return results[:top_k]
