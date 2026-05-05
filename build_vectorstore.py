"""
Build the unified AI governance vector store using LOCAL embeddings.

Uses sentence-transformers/all-MiniLM-L6-v2 — a free, local embedding model.
No API calls, no quotas. Model downloads once (~90MB) and runs on your laptop.

Can be run as a script (python build_vectorstore.py) or imported and called
via build_store() — the latter is used by streamlit_app.py to auto-build
on Streamlit Cloud where the vector store doesn't exist yet.
"""
import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

# Import the framework data
from iso_42001 import ISO_42001_CONTROLS
from nist_ai_rmf import NIST_AI_RMF_CONTROLS
from eu_ai_act import EU_AI_ACT_RISK_TIERS, EU_AI_ACT_ANNEX_III

load_dotenv()

# Absolute path anchored to this file's location.
# This works correctly whether the working directory is the project folder
# (local dev) or some other path (Streamlit Cloud).
_DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ai_gov_chroma_db"
)


def prepare_text_for_embedding(item):
    """Combine fields into a rich text representation for embedding."""
    parts = [
        f"Framework: {item['framework']}",
        f"Category: {item.get('category', 'N/A')}",
        f"Title: {item['title']}",
        f"Requirement: {item['requirement']}",
    ]
    if item.get('evidence_examples'):
        parts.append(f"Evidence examples: {item['evidence_examples']}")
    if item.get('common_gaps'):
        parts.append(f"Common gaps: {item['common_gaps']}")
    if item.get('details'):
        parts.append(f"Details: {item['details']}")
    return "\n".join(parts)


def build_store(db_path: str = None, verbose: bool = True):
    """
    Build the AI governance vector store.
    
    Idempotent — safe to call multiple times. If the collection exists, it's
    deleted and rebuilt. Returns the count of indexed items.
    """
    if db_path is None:
        db_path = _DEFAULT_DB_PATH
    
    def log(msg):
        if verbose:
            print(msg)
    
    log("🔄 Loading the local embedding model (downloads ~90MB on first run)...")
    embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    log(f"✅ Model loaded. Embedding dimension: {embeddings_model.get_sentence_embedding_dimension()}")
    
    log("🔄 Setting up ChromaDB...")
    client = chromadb.PersistentClient(path=db_path)
    
    # Wipe old collection if it exists
    try:
        client.delete_collection(name="ai_governance")
        log("🧹 Removed old collection")
    except Exception:
        pass
    
    collection = client.create_collection(name="ai_governance")
    
    def index_items(items, label):
        log(f"\n🔄 Indexing {label} ({len(items)} items)...")
        ids = [item['id'] for item in items]
        documents = [prepare_text_for_embedding(item) for item in items]
        metadatas = [
            {
                "framework": item['framework'],
                "category": item.get('category', ''),
                "title": item['title'],
            }
            for item in items
        ]
        vectors = embeddings_model.encode(
            documents,
            show_progress_bar=verbose,
            convert_to_numpy=True
        ).tolist()
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=vectors,
            metadatas=metadatas
        )
        log(f"✅ Indexed {len(ids)} {label}")
    
    index_items(ISO_42001_CONTROLS, "ISO 42001 controls")
    index_items(NIST_AI_RMF_CONTROLS, "NIST AI RMF subcategories")
    index_items(EU_AI_ACT_RISK_TIERS, "EU AI Act risk tiers")
    index_items(EU_AI_ACT_ANNEX_III, "EU AI Act Annex III categories")
    
    total = collection.count()
    log(f"\n🎉 AI governance vector store built!")
    log(f"📊 Total items indexed: {total}")
    log(f"💾 Saved to: {db_path}")
    return total


def store_exists(db_path: str = None) -> bool:
    """Check whether the vector store has been built and contains data."""
    if db_path is None:
        db_path = _DEFAULT_DB_PATH
    if not os.path.exists(db_path):
        return False
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name="ai_governance")
        return collection.count() > 0
    except Exception:
        return False


# Allow running as a script: python build_vectorstore.py
if __name__ == "__main__":
    build_store()