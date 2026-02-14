import os
from pathlib import Path
import pickle
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data/raw"
INDEX_DIR = BASE_DIR / "retrieval/indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

EMBED_MODEL = "BAAI/bge-base-en-v1.5"
model = SentenceTransformer(EMBED_MODEL)


# ------------------------------
# Simple PDF Loader (No LangChain)
# ------------------------------
def load_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


# ------------------------------
# Simple Chunker
# ------------------------------
def chunk_text(text, chunk_size=800, overlap=150):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# ------------------------------
# Load All Docs (Upgraded)
# ------------------------------
def load_all_documents():
    chunks = []
    metadata = []

    # ---- MACRO ----
    macro_path = DATA_DIR / "macro"
    for pdf in macro_path.rglob("*.pdf"):
        text = load_pdf_text(str(pdf))
        text_chunks = chunk_text(text)

        for chunk in text_chunks:
            chunks.append(chunk)
            metadata.append({
                "space": "macro",
                "ticker": None,
                "sector": None,
                "source": pdf.name
            })

    # ---- SECTOR ----
    sector_path = DATA_DIR / "sector"
    for sector_folder in sector_path.iterdir():
        if sector_folder.is_dir():
            sector_name = sector_folder.name

            for pdf in sector_folder.rglob("*.pdf"):
                text = load_pdf_text(str(pdf))
                text_chunks = chunk_text(text)

                for chunk in text_chunks:
                    chunks.append(chunk)
                    metadata.append({
                        "space": "sector",
                        "ticker": None,
                        "sector": sector_name,
                        "source": pdf.name
                    })

    # ---- COMPANY ----
    company_path = DATA_DIR / "company"
    for ticker_folder in company_path.iterdir():
        if ticker_folder.is_dir():
            ticker = ticker_folder.name.upper()

            # Read sector mapping
            sector_map = {
                "TCS": "IT",
                "INFY": "IT",
                "HCLTECH": "IT",
                "HDFCBANK": "Banking",
                "ICICIBANK": "Banking",
                "SBIN": "Banking"
            }

            sector_name = sector_map.get(ticker)

            for pdf in ticker_folder.rglob("*.pdf"):
                text = load_pdf_text(str(pdf))
                text_chunks = chunk_text(text)

                for chunk in text_chunks:
                    chunks.append(chunk)
                    metadata.append({
                        "space": "company",
                        "ticker": ticker,
                        "sector": sector_name,
                        "source": pdf.name
                    })

    return chunks, metadata



# ------------------------------
# Build FAISS Index
# ------------------------------
def build_index(chunks, metadata):
    print(f"Total chunks: {len(chunks)}")
    print("Creating embeddings...")

    embeddings = model.encode(chunks, show_progress_bar=True)

    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "trademind.index"))

    with open(INDEX_DIR / "trademind_metadata.pkl", "wb") as f:
        pickle.dump((chunks, metadata), f)

    print("Vector store built successfully.")


if __name__ == "__main__":
    chunks, metadata = load_all_documents()
    build_index(chunks, metadata)
