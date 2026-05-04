"""
Build the unified AI governance vector store using LOCAL embeddings.

Uses sentence-transformers/all-MiniLM-L6-v2 — a free, local embedding model.
No API calls, no quotas. Model downloads once (~90MB) and runs on your laptop.
"""
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

# Import the framework data
from iso_42001 import ISO_42001_CONTROLS
from nist_ai_rmf import NIST_AI_RMF_CONTROLS
from eu_ai_act import EU_AI_ACT_RISK_TIERS, EU_AI_ACT_ANNEX_III

load_dotenv()

print("🔄 Loading the local embedding model (downloads ~90MB on first run)...")
# all-MiniLM-L6-v2 produces 384-dimensional vectors
# It's small, fast, and works well for semantic search over technical content
embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print(f"✅ Model loaded. Embedding dimension: {embeddings_model.get_sentence_embedding_dimension()}")

print("🔄 Setting up ChromaDB...")
client = chromadb.PersistentClient(path="./ai_gov_chroma_db")

# Wipe old collection if it exists (to switch from old Gemini-embedded vectors)
try:
    client.delete_collection(name="ai_governance")
    print("🧹 Removed old collection")
except Exception:
    pass

collection = client.create_collection(name="ai_governance")


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


def index_items(items, label):
    """Embed and index a batch of governance items using local model."""
    print(f"\n🔄 Indexing {label} ({len(items)} items)...")
    
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
    
    # Local embedding — no API call, runs on your CPU
    # show_progress_bar=True gives visual feedback for slow runs
    vectors = embeddings_model.encode(
        documents,
        show_progress_bar=True,
        convert_to_numpy=True
    ).tolist()
    
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=vectors,
        metadatas=metadatas
    )
    print(f"✅ Indexed {len(ids)} {label}")


# Index all three frameworks
index_items(ISO_42001_CONTROLS, "ISO 42001 controls")
index_items(NIST_AI_RMF_CONTROLS, "NIST AI RMF subcategories")
index_items(EU_AI_ACT_RISK_TIERS, "EU AI Act risk tiers")
index_items(EU_AI_ACT_ANNEX_III, "EU AI Act Annex III categories")

print(f"\n🎉 AI governance vector store built!")
print(f"📊 Total items indexed: {collection.count()}")
print(f"💾 Saved to: ./ai_gov_chroma_db/")
print(f"🆓 No API quota used — embeddings ran locally")