"""
AI Governance Assessment Agent - Streamlit Web Interface

Run with: streamlit run app.py
"""
import streamlit as st
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

# =============================================================================
# Page configuration - must be the first Streamlit command
# =============================================================================
st.set_page_config(
    page_title="AI Governance Assessor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Cached resources - load once, reuse across reruns
# =============================================================================
@st.cache_resource
def load_embedding_model():
    """Load the local embedding model. Cached so it loads only once."""
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@st.cache_resource
def load_vector_store():
    """Connect to ChromaDB and return the collection."""
    client = chromadb.PersistentClient(path="./ai_gov_chroma_db")
    return client.get_collection(name="ai_governance")


@st.cache_resource
def load_agent():
    """Build the agent with tools. Cached so it builds only once."""
    embeddings_model = load_embedding_model()
    collection = load_vector_store()

    @tool
    def search_ai_governance_frameworks(query: str) -> str:
        """Search across ISO 42001, NIST AI RMF, and EU AI Act for AI governance
        requirements relevant to a query. Use this when the user asks about
        AI governance controls, risks, regulations, or compliance requirements.
        Returns the most relevant items with framework attribution."""
        query_vector = embeddings_model.encode(
            [query], convert_to_numpy=True
        )[0].tolist()
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=6
        )
        matches = []
        for item_id, doc, meta in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0]
        ):
            matches.append(
                f"[{meta['framework']}] {item_id}: {meta['title']}\n{doc[:600]}"
            )
        return "\n\n---\n\n".join(matches) if matches else "No relevant items found."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    agent = create_react_agent(llm, [search_ai_governance_frameworks])
    return agent


# =============================================================================
# Sidebar - shows context about the tool
# =============================================================================
with st.sidebar:
    st.title("🛡️ AI Governance Assessor")
    st.markdown("---")
    st.subheader("Knowledge Base")
    st.markdown(
        """
        - **ISO/IEC 42001:2023** (38 controls)
        - **NIST AI RMF 1.0** (72 subcategories)
        - **EU AI Act** (Regulation 2024/1689)
        
        Total: 124 governance items
        """
    )
    st.markdown("---")
    st.subheader("How to use")
    st.markdown(
        """
        Ask questions about:
        - AI governance controls
        - Regulatory requirements
        - Risk classification
        - Compliance approaches
        
        Example questions are at the top of the main panel.
        """
    )
    st.markdown("---")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()


# =============================================================================
# Main panel
# =============================================================================
st.title("AI Governance Assessment")
st.caption(
    "Multi-framework AI governance Q&A across ISO 42001, NIST AI RMF, and EU AI Act"
)

# Show example questions if conversation is empty
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.info("👋 Try one of these example questions to get started:")
    col1, col2 = st.columns(2)
    examples = [
        "What does the EU AI Act require for AI used in hiring?",
        "How should bias be addressed in AI training data?",
        "What are the human oversight requirements across frameworks?",
        "Compare incident reporting requirements in NIST and ISO 42001",
    ]
    for i, ex in enumerate(examples):
        with (col1 if i % 2 == 0 else col2):
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state.pending_question = ex
                st.rerun()


# =============================================================================
# Render conversation history
# =============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =============================================================================
# Handle user input
# =============================================================================
# Either a pending question (from example button) or new chat input
user_input = None
if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

chat_input = st.chat_input("Ask about AI governance requirements...")
if chat_input:
    user_input = chat_input

if user_input:
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run the agent and stream response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and searching frameworks..."):
            agent = load_agent()
            try:
                result = agent.invoke({"messages": [("user", user_input)]})
                response = result["messages"][-1].content
            except Exception as e:
                response = f"⚠️ Something went wrong: {str(e)}"

        st.markdown(response)
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )