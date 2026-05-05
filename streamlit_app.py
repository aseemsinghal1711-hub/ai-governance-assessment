"""
AI Governance Assessment Tool - Main app entry point.

Multi-page Streamlit app with custom modern SaaS styling.
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import os

# Bridge Streamlit Cloud secrets to environment variables
# Locally, .env loads via python-dotenv. On Streamlit Cloud, secrets come via st.secrets.
try:
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass  # st.secrets only works on Streamlit Cloud; locally we use .env

# =============================================================================
# Page config (must be first Streamlit call)
# =============================================================================
st.set_page_config(
    page_title="AI Governance Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "AI Governance Assessment Tool — Multi-framework gap analysis powered by Gemini.",
    },
)


# =============================================================================
# Custom CSS injection — modern SaaS styling
# =============================================================================
CUSTOM_CSS = """
<style>
/* === Typography === */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
}

/* Headings tighter, more confident */
h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #1F2937 !important;
}

h1 {
    font-size: 2.25rem !important;
    margin-bottom: 0.5rem !important;
}

/* === Sidebar styling === */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    padding-top: 1rem;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a {
    border-radius: 8px;
    margin: 2px 8px;
    padding: 8px 12px;
    transition: background-color 0.15s;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a:hover {
    background-color: #F3F4F6;
}

/* === Metrics / cards === */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    transition: box-shadow 0.15s, border-color 0.15s;
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.06);
    border-color: #D1D5DB;
}

[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] {
    color: #1F2937 !important;
    font-weight: 700 !important;
}

/* === Buttons === */
.stButton button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s !important;
    border: 1px solid transparent !important;
}

.stButton button[kind="primary"] {
    background: #7C3AED !important;
    color: #FFFFFF !important;
    border-color: #7C3AED !important;
}

.stButton button[kind="primary"]:hover {
    background: #6D28D9 !important;
    border-color: #6D28D9 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(124, 58, 237, 0.25);
}

.stButton button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #4B5563 !important;
    border: 1px solid #D1D5DB !important;
}

.stButton button[kind="secondary"]:hover {
    background: #F9FAFB !important;
    border-color: #9CA3AF !important;
}

/* === Status indicators (success / info / warning / error) === */
[data-testid="stAlertContainer"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
    padding: 12px 16px !important;
}

/* === Dividers cleaner === */
hr {
    margin: 2rem 0 !important;
    border-color: #E5E7EB !important;
}

/* === Hide Streamlit branding (cleaner look) === */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* === Custom card style for our progress cards === */
.progress-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    height: 100%;
    transition: border-color 0.15s, box-shadow 0.15s;
}

.progress-card:hover {
    border-color: #7C3AED;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.08);
}

.progress-card-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.progress-card-title {
    font-size: 0.875rem;
    color: #6B7280;
    margin-bottom: 0.25rem;
    font-weight: 500;
}

.progress-card-status {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 0.25rem;
}

.progress-card-detail {
    font-size: 0.75rem;
    color: #9CA3AF;
}

.progress-card-status-incomplete {
    color: #9CA3AF !important;
}

.progress-card-status-complete {
    color: #0D9488 !important;
}

/* === Hero header === */
.hero-header {
    background: linear-gradient(135deg, #7C3AED 0%, #0D9488 100%);
    border-radius: 16px;
    padding: 32px 40px;
    color: #FFFFFF;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
}

.hero-header h1 {
    color: #FFFFFF !important;
    margin: 0 0 8px 0 !important;
    font-size: 2rem !important;
}

.hero-header p {
    color: rgba(255, 255, 255, 0.9);
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;
}

/* === Section headers with subtle accent === */
.section-label {
    display: inline-block;
    background: #F3E8FF;
    color: #7C3AED;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =============================================================================
# Initialize session state
# =============================================================================
if "profile" not in st.session_state:
    st.session_state.profile = None

if "evidence_files" not in st.session_state:
    st.session_state.evidence_files = []

if "assessment_report" not in st.session_state:
    st.session_state.assessment_report = None

if "remediation_plan" not in st.session_state:
    st.session_state.remediation_plan = None

if "intake_messages" not in st.session_state:
    st.session_state.intake_messages = []


# =============================================================================
# Helper for the progress cards
# =============================================================================
def progress_card(icon: str, title: str, status: str, detail: str, complete: bool):
    """Render a custom-styled progress card."""
    status_class = "progress-card-status-complete" if complete else "progress-card-status-incomplete"
    return f"""
    <div class="progress-card">
        <div class="progress-card-icon">{icon}</div>
        <div class="progress-card-title">{title}</div>
        <div class="progress-card-status {status_class}">{status}</div>
        <div class="progress-card-detail">{detail}</div>
    </div>
    """


# =============================================================================
# HERO HEADER
# =============================================================================
st.markdown("""
<div class="hero-header">
    <h1>AI Governance Assessment</h1>
    <p>Multi-framework gap analysis across ISO 42001, NIST AI RMF, and the EU AI Act — with evidence reading powered by Gemini.</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# OVERVIEW
# =============================================================================
st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
st.markdown("### How it works")

st.markdown("""
The assessment process moves through four stages. You can navigate between them using the sidebar 
and return to earlier stages to revise your inputs.
""")

stage_col1, stage_col2 = st.columns(2)

with stage_col1:
    st.markdown("""
    **1. Intake** — Conversational interview about your AI system. The agent asks 
    structured questions and asks for supporting documents when you claim controls exist.
    
    **2. Evidence** — Upload supporting documents (PDFs, Word, Excel, CSV, plain text). 
    The system extracts text and links it to your claims.
    """)

with stage_col2:
    st.markdown("""
    **3. Assessment** — Multi-framework gap analysis. The agent evaluates each control, 
    reading your evidence to distinguish claimed-but-unverified from genuinely substantiated.
    
    **4. Recommendations** — Phased remediation roadmap with quick wins, foundation, 
    maturity, and optimization actions.
    """)


# =============================================================================
# PROGRESS DASHBOARD
# =============================================================================
st.divider()

st.markdown('<div class="section-label">Your progress</div>', unsafe_allow_html=True)
st.markdown("### Current assessment status")

col1, col2, col3, col4 = st.columns(4)

# Card 1: Intake
with col1:
    if st.session_state.profile is not None:
        st.markdown(
            progress_card(
                icon="🗣️",
                title="Intake",
                status="Complete",
                detail=f"System: {st.session_state.profile.system_name}",
                complete=True,
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            progress_card(
                icon="🗣️",
                title="Intake",
                status="Not started",
                detail="Begin in the sidebar",
                complete=False,
            ),
            unsafe_allow_html=True,
        )

# Card 2: Evidence
with col2:
    evidence_count = len(st.session_state.evidence_files)
    if evidence_count > 0:
        st.markdown(
            progress_card(
                icon="📄",
                title="Evidence",
                status=f"{evidence_count} uploaded",
                detail="Documents linked to claims",
                complete=True,
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            progress_card(
                icon="📄",
                title="Evidence",
                status="None yet",
                detail="Optional but recommended",
                complete=False,
            ),
            unsafe_allow_html=True,
        )

# Card 3: Assessment
with col3:
    if st.session_state.assessment_report is not None:
        finding_count = len(st.session_state.assessment_report.findings)
        st.markdown(
            progress_card(
                icon="🔍",
                title="Assessment",
                status=f"{finding_count} findings",
                detail="Multi-framework analysis done",
                complete=True,
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            progress_card(
                icon="🔍",
                title="Assessment",
                status="Not run",
                detail="Requires intake first",
                complete=False,
            ),
            unsafe_allow_html=True,
        )

# Card 4: Recommendations
with col4:
    if st.session_state.remediation_plan is not None:
        plan = st.session_state.remediation_plan
        action_count = (
            len(plan.quick_wins) + len(plan.foundation_phase) +
            len(plan.maturity_phase) + len(plan.optimization_phase)
        )
        st.markdown(
            progress_card(
                icon="📋",
                title="Roadmap",
                status=f"{action_count} actions",
                detail="Phased remediation plan",
                complete=True,
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            progress_card(
                icon="📋",
                title="Roadmap",
                status="Pending",
                detail="Requires assessment first",
                complete=False,
            ),
            unsafe_allow_html=True,
        )


# =============================================================================
# CALL TO ACTION
# =============================================================================
st.divider()

if st.session_state.profile is None:
    st.markdown('<div class="section-label">Get started</div>', unsafe_allow_html=True)
    st.markdown("### Ready to assess your AI system?")
    st.markdown(
        "Click **1. Intake** in the sidebar to begin. The interview takes about 5-10 minutes "
        "and collects information about your AI system and its current governance state."
    )
else:
    st.markdown('<div class="section-label">In progress</div>', unsafe_allow_html=True)
    st.markdown(f"### Continuing assessment for: {st.session_state.profile.system_name}")
    st.markdown(
        "Pick up where you left off using the sidebar, or restart with the button below."
    )
    
    if st.button("🔄 Start a new assessment", type="secondary"):
        for key in ["profile", "evidence_files", "assessment_report", 
                    "remediation_plan", "intake_messages"]:
            st.session_state[key] = None if key not in ["evidence_files", "intake_messages"] else []
        st.rerun()


# =============================================================================
# FOOTER
# =============================================================================
st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption("**Frameworks**")
    st.caption("ISO 42001 · NIST AI RMF · EU AI Act")

with footer_col2:
    st.caption("**Built with**")
    st.caption("Streamlit · LangChain · Gemini · ChromaDB")

with footer_col3:
    st.caption("**Status**")
    st.caption("v2.0 · Evidence-aware assessment")