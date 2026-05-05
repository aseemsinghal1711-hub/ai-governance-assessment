"""Assessment Page - run the multi-framework gap assessment and display findings."""
import streamlit as st
from assessment_agent import run_assessment


# =============================================================================
# Initialize session state defaults
# =============================================================================
if "profile" not in st.session_state:
    st.session_state.profile = None
if "assessment_report" not in st.session_state:
    st.session_state.assessment_report = None


# =============================================================================
# Page header
# =============================================================================
st.title("🔍 3. Assessment")
st.markdown(
    "Run a multi-framework gap analysis across ISO 42001, NIST AI RMF, and the EU AI Act. "
    "The agent will read your evidence documents and evaluate each control."
)
st.divider()


# =============================================================================
# Block if intake not complete
# =============================================================================
if st.session_state.profile is None:
    st.warning(
        "**Intake required first.** Please complete the **1. Intake** page before running assessment."
    )
    st.stop()


profile = st.session_state.profile


# =============================================================================
# Show context
# =============================================================================
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**System:** {profile.system_name}")
    with col2:
        st.markdown(f"**Sector:** {profile.deployment_sector}")
    with col3:
        st.markdown(f"**Evidence:** {len(profile.evidence_attachments)} document(s)")


# =============================================================================
# Run assessment button
# =============================================================================
if st.session_state.assessment_report is None:
    st.markdown("### Ready to run")
    st.markdown(
        "The assessment will take **2-4 minutes** depending on how many evidence documents are attached. "
        "It will run 5 phases: EU AI Act classification, control selection, evidence-aware evaluation, "
        "cross-framework synthesis, and executive summary."
    )
    
    if st.button("▶️ Run Assessment", type="primary"):
        with st.spinner("Running multi-framework assessment... this may take 2-4 minutes."):
            try:
                report = run_assessment(profile)
                st.session_state.assessment_report = report
                st.rerun()
            except Exception as e:
                st.error(f"Assessment failed: {e}")
    st.stop()


# =============================================================================
# Display the report
# =============================================================================
report = st.session_state.assessment_report

st.markdown("### Assessment Report")

# EU AI Act classification
with st.container(border=True):
    risk_color = {"high": "🔴", "limited": "🟡", "minimal": "🟢", "prohibited": "⛔"}.get(
        report.eu_ai_act_risk_tier, "⚪"
    )
    st.markdown(f"**EU AI Act Classification:** {risk_color} `{report.eu_ai_act_risk_tier.upper()}`")
    st.caption(report.eu_ai_act_reasoning)

st.divider()

# Status distribution
st.markdown("### Findings overview")

status_counts = {}
severity_counts = {}
for f in report.findings:
    status_counts[f.status] = status_counts.get(f.status, 0) + 1
    severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total findings", len(report.findings))
with col2:
    st.metric("Critical", severity_counts.get("critical", 0))
with col3:
    st.metric("High", severity_counts.get("high", 0))
with col4:
    st.metric("Met with evidence", status_counts.get("met_with_evidence", 0))

st.divider()

# Executive summary
st.markdown("### Executive summary")
with st.container(border=True):
    st.markdown(report.overall_maturity_summary)

# Cross-framework themes
if report.cross_framework_themes:
    st.markdown("### Cross-framework themes")
    for i, theme in enumerate(report.cross_framework_themes, 1):
        with st.container(border=True):
            st.markdown(f"**{i}.** {theme}")

# Immediate concerns
if report.immediate_concerns:
    st.markdown("### Immediate concerns")
    for concern in report.immediate_concerns:
        st.warning(concern)

# Detailed findings
st.markdown("### All findings")

# Filter by status
status_filter = st.multiselect(
    "Filter by status",
    options=list(status_counts.keys()),
    default=list(status_counts.keys()),
)

severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
sorted_findings = sorted(
    report.findings,
    key=lambda f: severity_order.get(f.severity, 99),
)

for f in sorted_findings:
    if f.status not in status_filter:
        continue
    
    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(f.severity, "⚪")
    
    # Display: framework + control_id + status are reliable; title may be garbled in source data
    expander_label = f"{severity_emoji} **[{f.framework}] {f.control_id}** — {f.status} ({f.severity})"
    
    with st.expander(expander_label):
        # The control_title field in some data sources is truncated mid-sentence.
        # Display it but don't make it the primary descriptor.
        if f.control_title and f.control_title.strip():
            st.caption(f"Control area: {f.control_title.strip()}")
        
        if f.evidence_filename:
            st.markdown("**Evidence document**")
            st.code(f.evidence_filename, language=None)
        
        if f.evidence_assessment:
            st.markdown("**Evidence assessment**")
            st.write(f.evidence_assessment)
        
        st.markdown("**Reasoning**")
        st.write(f.reasoning)

st.divider()

# Re-run button
if st.button("🔄 Re-run assessment", type="secondary"):
    st.session_state.assessment_report = None
    if "remediation_plan" in st.session_state:
        st.session_state.remediation_plan = None
    st.rerun()

st.markdown("### Next step")
st.markdown("Continue to **4. Recommendations** in the sidebar for the phased remediation roadmap.")