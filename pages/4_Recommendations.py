"""Recommendations page - phased remediation roadmap."""
import streamlit as st

st.title("📋 4. Recommendations")
st.markdown("Phased remediation roadmap for closing identified gaps.")

st.info("📌 This page is under construction. Implementation coming in Stage 7.4.")

if st.session_state.assessment_report is None:
    st.warning("Run assessment first.")
elif st.session_state.remediation_plan is None:
    st.markdown("Ready to generate recommendations.")
else:
    plan = st.session_state.remediation_plan
    total = (len(plan.quick_wins) + len(plan.foundation_phase) +
             len(plan.maturity_phase) + len(plan.optimization_phase))
    st.success(f"Plan generated: {total} actions across 4 phases.")