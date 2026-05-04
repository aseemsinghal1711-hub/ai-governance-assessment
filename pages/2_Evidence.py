"""
Evidence Page - upload supporting documents to substantiate governance claims.

Users can upload PDFs, Word docs, Excel, CSV, or plain text. Each document
gets linked to a specific profile claim (the field_name) so the assessment
agent can read it during evaluation.
"""
import streamlit as st
import os
import tempfile
from pathlib import Path

from document_processor import ingest_document
from models import EvidenceAttachment


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
# Block access if intake not complete
# =============================================================================
if st.session_state.profile is None:
    st.warning(
        "**Intake required first.** Please complete the **1. Intake** page "
        "before uploading evidence — we need to know which AI system you're assessing."
    )
    st.stop()


# =============================================================================
# Show current system context
# =============================================================================
profile = st.session_state.profile

with st.container(border=True):
    st.markdown(f"**System being assessed:** {profile.system_name}")
    st.caption(f"{profile.deployment_sector} · {', '.join(profile.deployment_geographies)}")


# =============================================================================
# Field mapping — which claims need what evidence
# =============================================================================
# Maps the profile field to a human-readable label and what evidence is expected
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
        "expected": "AI Impact Assessment (AIA), Data Protection Impact Assessment (DPIA), or fundamental rights assessment",
        "icon": "🎯",
    },
    "has_human_oversight": {
        "label": "Human Oversight",
        "description": "Procedures for human review of AI decisions",
        "expected": "Oversight procedure document, escalation runbook, or governance structure document",
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
        "expected": "Bias testing methodology, fairness metrics report, or disparate impact analysis",
        "icon": "⚖️",
    },
}


# =============================================================================
# Helper: get profile claim status for a field
# =============================================================================
def get_field_status(field_name: str) -> tuple[bool, str]:
    """Return (claim_value, status_label)."""
    if not hasattr(profile, field_name):
        return False, "unknown"
    
    value = getattr(profile, field_name)
    if value is True:
        return True, "claimed"
    elif value is False:
        return False, "not in place"
    return False, "unknown"


# =============================================================================
# Helper: get already-attached evidence for a field
# =============================================================================
def get_evidence_for_field(field_name: str) -> list:
    """Return list of EvidenceAttachment objects already attached to this field."""
    return [e for e in profile.evidence_attachments if e.field_name == field_name]


# =============================================================================
# UPLOAD SECTION
# =============================================================================
st.markdown("### Upload evidence")
st.markdown(
    "For each governance area you've claimed is in place, upload the supporting document. "
    "If you've already attached evidence during intake, it will appear below."
)

# Render an upload section per governance area
for field_name, meta in FIELD_LABELS.items():
    claimed, status_label = get_field_status(field_name)
    existing_evidence = get_evidence_for_field(field_name)
    
    with st.container(border=True):
        # Header row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{meta['icon']} {meta['label']}**")
            st.caption(meta["description"])
        with col2:
            if claimed:
                st.success(f"✓ Claimed")
            else:
                st.info(f"Not in place")
        
        # If user said False during intake, no evidence needed
        if not claimed:
            st.caption(
                f"You indicated this control is not in place during intake. "
                f"No evidence needed — the assessment will mark this as not_met."
            )
            continue
        
        # Show existing evidence (if any)
        if existing_evidence:
            st.markdown("**Already attached:**")
            for i, ev in enumerate(existing_evidence):
                ev_col1, ev_col2 = st.columns([4, 1])
                with ev_col1:
                    st.markdown(f"📎 `{ev.filename}` ({ev.file_type}, {len(ev.extracted_text)} chars)")
                    if ev.extraction_warnings:
                        with st.expander("⚠️ Extraction notes", expanded=False):
                            for warning in ev.extraction_warnings:
                                st.caption(warning)
                with ev_col2:
                    if st.button("Remove", key=f"remove_{field_name}_{i}", type="secondary"):
                        # Remove this specific attachment from profile
                        profile.evidence_attachments = [
                            e for e in profile.evidence_attachments
                            if not (e.field_name == ev.field_name and e.filename == ev.filename)
                        ]
                        st.rerun()
        
        # Upload widget
        st.markdown(f"**Upload:** {meta['expected']}")
        uploaded_file = st.file_uploader(
            f"Choose a file for {meta['label']}",
            type=["pdf", "docx", "txt", "md", "xlsx", "xlsm", "csv"],
            key=f"upload_{field_name}",
            label_visibility="collapsed",
        )
        
        if uploaded_file is not None:
            # Check if already attached (avoid duplicates)
            already_attached = any(
                e.filename == uploaded_file.name and e.field_name == field_name
                for e in profile.evidence_attachments
            )
            
            if already_attached:
                st.caption(f"`{uploaded_file.name}` is already attached to this field.")
            else:
                # Save uploaded file to temp location for ingestion
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        # Write to temp file
                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=Path(uploaded_file.name).suffix,
                        ) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        # Ingest the document
                        doc = ingest_document(tmp_path, claimed_purpose=meta["label"])
                        
                        # Build the EvidenceAttachment
                        attachment = EvidenceAttachment(
                            field_name=field_name,
                            file_path=tmp_path,
                            filename=uploaded_file.name,  # use original name not temp
                            file_type=doc.file_type,
                            claimed_purpose=meta["label"],
                            extracted_text=doc.extracted_text,
                            page_count=doc.page_count,
                            extraction_warnings=doc.extraction_warnings,
                        )
                        
                        # Add to profile
                        profile.evidence_attachments.append(attachment)
                        
                        # Cleanup temp file (optional — can leave for debugging)
                        os.unlink(tmp_path)
                        
                        st.success(f"✅ Attached `{uploaded_file.name}` ({len(doc.extracted_text)} chars extracted)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not process file: {str(e)[:200]}")


# =============================================================================
# SUMMARY & NEXT STEP
# =============================================================================
st.divider()

total_evidence = len(profile.evidence_attachments)
fields_with_evidence = len(set(e.field_name for e in profile.evidence_attachments))
fields_claimed = sum(
    1 for f in FIELD_LABELS if getattr(profile, f, False) is True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total documents", total_evidence)
with col2:
    st.metric("Areas with evidence", f"{fields_with_evidence} / {fields_claimed}")
with col3:
    if fields_claimed > 0:
        coverage = int((fields_with_evidence / fields_claimed) * 100)
        st.metric("Evidence coverage", f"{coverage}%")
    else:
        st.metric("Evidence coverage", "—")

if fields_claimed > 0 and fields_with_evidence < fields_claimed:
    missing_count = fields_claimed - fields_with_evidence
    st.info(
        f"💡 You've claimed {fields_claimed} controls are in place. "
        f"{fields_with_evidence} have evidence attached, {missing_count} don't. "
        f"Controls without evidence will be marked as 'claimed but unverified' in the assessment — "
        f"this is acceptable but reduces audit defensibility."
    )

st.markdown("### Next step")
st.markdown(
    "When you've uploaded all available evidence, continue to **3. Assessment** "
    "in the sidebar to run the multi-framework gap analysis."
)