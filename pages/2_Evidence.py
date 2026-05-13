"""Evidence Page - upload supporting documents."""
import streamlit as st
import os
import tempfile
from pathlib import Path

from document_processor import ingest_document
from models import EvidenceAttachment


# =============================================================================
# Initialize session state defaults (in case user lands here directly)
# =============================================================================
if "profile" not in st.session_state:
    st.session_state.profile = None


# =============================================================================
# Page header
# =============================================================================
st.title("📄 2. Evidence")
st.markdown(
    "Upload supporting documents that substantiate your governance claims. "
    "The assessment agent will read these and evaluate whether they actually "
    "address the framework requirements."
)
st.divider()


# =============================================================================
# Block if intake not complete
# =============================================================================
if st.session_state.profile is None:
    st.warning(
        "**Intake required first.** Please complete the **1. Intake** page before uploading evidence."
    )
    st.stop()


profile = st.session_state.profile

with st.container(border=True):
    st.markdown(f"**System being assessed:** {profile.system_name}")
    st.caption(f"{profile.deployment_sector} · {', '.join(profile.deployment_geographies)}")


FIELD_LABELS = {
    "has_documented_policy": {
        "label": "AI Policy",
        "description": "Documented policy governing AI use",
        "expected": "AI policy, governance framework, or organizational AI standards document",
        "icon": "📋",
    },
    "has_impact_assessment": {
        "label": "Impact Assessment",
        "description": "AIA or DPIA for the system",
        "expected": "AI Impact Assessment, DPIA, or fundamental rights assessment",
        "icon": "🎯",
    },
    "has_human_oversight": {
        "label": "Human Oversight",
        "description": "Procedures for human review of AI decisions",
        "expected": "Oversight procedure, escalation runbook, or governance structure document",
        "icon": "👤",
    },
    "has_monitoring": {
        "label": "Production Monitoring",
        "description": "Ongoing monitoring of AI in production",
        "expected": "Monitoring runbook, dashboard screenshots, or operations report",
        "icon": "📊",
    },
    "has_bias_testing": {
        "label": "Bias Testing",
        "description": "Bias and fairness testing methodology and results",
        "expected": "Bias methodology, fairness metrics report, or disparate impact analysis",
        "icon": "⚖️",
    },
}


def get_field_status(field_name):
    if not hasattr(profile, field_name):
        return False
    return getattr(profile, field_name) is True


def get_evidence_for_field(field_name):
    return [e for e in profile.evidence_attachments if e.field_name == field_name]


st.markdown("### Upload evidence")

for field_name, meta in FIELD_LABELS.items():
    claimed = get_field_status(field_name)
    existing = get_evidence_for_field(field_name)
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{meta['icon']} {meta['label']}**")
            st.caption(meta["description"])
        with col2:
            if claimed:
                st.success("✓ Claimed")
            else:
                st.info("Not in place")
        
        if not claimed:
            st.caption("You indicated this control is not in place. No evidence needed.")
            continue
        
        if existing:
            st.markdown("**Already attached:**")
            for i, ev in enumerate(existing):
                ec1, ec2 = st.columns([4, 1])
                with ec1:
                    st.markdown(f"📎 `{ev.filename}` ({ev.file_type}, {len(ev.extracted_text)} chars)")
                with ec2:
                    if st.button("Remove", key=f"rm_{field_name}_{i}", type="secondary"):
                        profile.evidence_attachments = [
                            e for e in profile.evidence_attachments
                            if not (e.field_name == ev.field_name and e.filename == ev.filename)
                        ]
                        st.rerun()
        
        st.markdown(f"**Upload:** {meta['expected']}")
        uploaded = st.file_uploader(
            f"Choose a file for {meta['label']}",
            type=["pdf", "docx", "txt", "md", "xlsx", "xlsm", "csv"],
            key=f"up_{field_name}",
            label_visibility="collapsed",
        )
        
        if uploaded is not None:
            already = any(
                e.filename == uploaded.name and e.field_name == field_name
                for e in profile.evidence_attachments
            )
            if already:
                st.caption(f"`{uploaded.name}` is already attached.")
            else:
                with st.spinner(f"Processing {uploaded.name}..."):
                    try:
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=Path(uploaded.name).suffix,
                        ) as tmp:
                            tmp.write(uploaded.getvalue())
                            tmp_path = tmp.name
                        doc = ingest_document(tmp_path, claimed_purpose=meta["label"])
                        attachment = EvidenceAttachment(
                            field_name=field_name,
                            file_path=tmp_path,
                            filename=uploaded.name,
                            file_type=doc.file_type,
                            claimed_purpose=meta["label"],
                            extracted_text=doc.extracted_text,
                            page_count=doc.page_count,
                            extraction_warnings=doc.extraction_warnings,
                        )
                        profile.evidence_attachments.append(attachment)
                        os.unlink(tmp_path)
                        st.success(f"✅ Attached `{uploaded.name}` ({len(doc.extracted_text)} chars)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not process: {str(e)[:200]}")


st.divider()
total = len(profile.evidence_attachments)
fields_with_ev = len(set(e.field_name for e in profile.evidence_attachments))
fields_claimed = sum(1 for f in FIELD_LABELS if getattr(profile, f, False) is True)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total documents", total)
with c2:
    st.metric("Areas with evidence", f"{fields_with_ev} / {fields_claimed}")
with c3:
    if fields_claimed > 0:
        coverage = int((fields_with_ev / fields_claimed) * 100)
        st.metric("Coverage", f"{coverage}%")

st.markdown("### Next")
st.markdown("Continue to **3. Assessment** to run the multi-framework gap analysis.")