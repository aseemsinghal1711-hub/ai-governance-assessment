"""Quick sanity test of the AI governance vector store using local embeddings."""
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()
print("🔄 Loading local embedding model...")
embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./ai_gov_chroma_db")
collection = client.get_collection(name="ai_governance")


def search(query, n_results=5):
    print(f"\n{'='*70}")
    print(f"🔍 Query: {query}")
    print('='*70)
    query_vector = embeddings_model.encode([query], convert_to_numpy=True)[0].tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results
    )
    for i, (item_id, doc, meta) in enumerate(zip(
        results['ids'][0], results['documents'][0], results['metadatas'][0]
    ), 1):
        print(f"\n[{i}] {item_id} ({meta['framework']})")
        print(f"    {meta['title'][:120]}")


# Test queries across the three frameworks
search("What controls cover bias and fairness in AI systems?")
search("What does the EU AI Act say about hiring and recruitment AI?")
search("Requirements for human oversight of AI decisions")
search("Documentation needed for training data")
search("Incident reporting for AI systems")