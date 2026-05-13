"""Recommendations Page - phased remediation roadmap."""
import json
import streamlit as st
from recommendation_agent import generate_recommendations


# =============================================================================
# Initialize session state defaults
# =============================================================================
if "profile" not in st.session_state:
    st.session_state.profile = None
if "assessment_report" not in st.session_state:
    st.session_state.assessment_report = None
if "remediation_plan" not in st.session_state:
    st.session_state.remediation_plan = None


# =============================================================================
# Page header
# =============================================================================
st.title("📋 4. Recommendations")
st.markdown(
    "Phased remediation roadmap with quick wins, foundation, maturity, and optimization actions."
)
st.divider()


# =============================================================================
# Block if assessment not run
# =============================================================================
if st.session_state.profile is None:
    st.warning("**Intake required first.**")
    st.stop()

if st.session_state.assessment_report is None:
    st.warning("**Assessment required first.** Please run the assessment on the previous page.")
    st.stop()


# =============================================================================
# Generate plan if not already done
# =============================================================================
if st.session_state.remediation_plan is None:
    st.markdown("### Generate roadmap")
    st.markdown("This takes about **30-60 seconds**. The plan will be tailored to the findings from your assessment.")
    
    if st.button("▶️ Generate Recommendations", type="primary"):
        with st.spinner("Generating phased remediation plan..."):
            try:
                plan = generate_recommendations(
                    st.session_state.profile,
                    st.session_state.assessment_report,
                )
                st.session_state.remediation_plan = plan
                st.rerun()
            except Exception as e:
                st.error(f"Plan generation failed: {e}")
    st.stop()


# =============================================================================
# Display the plan
# =============================================================================
plan = st.session_state.remediation_plan

# Executive summary
st.markdown("### Executive summary")
with st.container(border=True):
    st.markdown(plan.executive_summary)

st.divider()

# Phase metrics
total = (len(plan.quick_wins) + len(plan.foundation_phase) +
         len(plan.maturity_phase) + len(plan.optimization_phase))

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total actions", total)
with col2:
    st.metric("Quick wins", len(plan.quick_wins))
with col3:
    st.metric("Foundation", len(plan.foundation_phase))
with col4:
    st.metric("Maturity", len(plan.maturity_phase))
with col5:
    st.metric("Optimization", len(plan.optimization_phase))


# =============================================================================
# Helper: render a phase
# =============================================================================
def render_phase(title: str, emoji: str, timeline: str, actions: list):
    if not actions:
        return
    st.markdown(f"### {emoji} {title}")
    st.caption(timeline)
    for i, action in enumerate(actions, 1):
        with st.container(border=True):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.markdown(f"**{i}. {action.title}**")
                st.caption(f"Owner: {action.suggested_owner} · Effort: {action.effort}")
            with col_b:
                effort_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(action.effort, "⚪")
                st.markdown(f"### {effort_color}")
            
            st.markdown(action.description)
            
            if action.addresses_findings:
                with st.expander("Addresses findings"):
                    for finding_id in action.addresses_findings:
                        st.markdown(f"- `{finding_id}`")
            
            st.caption(f"**Success criteria:** {action.success_criteria}")
    st.divider()


render_phase("Quick Wins", "🚀", "First 30 days", plan.quick_wins)
render_phase("Foundation", "🏗️", "Months 1-3", plan.foundation_phase)
render_phase("Maturity", "📈", "Months 3-9", plan.maturity_phase)
render_phase("Optimization", "✨", "Months 9+", plan.optimization_phase)


# =============================================================================
# Re-run + export
# =============================================================================
if st.button("🔄 Regenerate plan", type="secondary"):
    st.session_state.remediation_plan = None
    st.rerun()


# =============================================================================
# JSON Export
# =============================================================================
st.divider()
st.markdown("### Export")

bundle = {
    "profile": st.session_state.profile.model_dump(),
    "assessment": st.session_state.assessment_report.model_dump(),
    "plan": st.session_state.remediation_plan.model_dump(),
}
st.download_button(
    "📥 Download full assessment (JSON)",
    data=json.dumps(bundle, indent=2),
    file_name=f"{st.session_state.profile.system_name.replace(' ', '_')}_assessment.json",
    mime="application/json",
)
st.caption("Word/Excel exports coming next session — JSON works today.")