"""
Persistence layer for AI Governance Assessment Tool — file-based.

Users download their session state as a JSON file and re-upload it later
to restore. Simple, reliable, portable across devices and browsers.

Public API:
- export_state_to_json()    → returns JSON string for download button
- import_state_from_json()  → restores session from uploaded JSON bytes
- clear_state()             → wipes current session (for "Start Fresh")
- save_state()              → no-op (kept for compatibility with existing code)
- init_storage()            → no-op (kept for compatibility with existing code)
- load_state()              → no-op (kept for compatibility with existing code)
"""
import json
from datetime import datetime
from typing import Optional

import streamlit as st

# Schema version — increment when state structure changes incompatibly.
SCHEMA_VERSION = "1.0"


# =============================================================================
# Pydantic serialization helpers
# =============================================================================
def _serialize_pydantic(obj):
    """Convert a Pydantic model (or list of them) to a JSON-safe dict."""
    if obj is None:
        return None
    if isinstance(obj, list):
        return [_serialize_pydantic(item) for item in obj]
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj


def _deserialize_pydantic(data, model_class):
    """Restore a Pydantic model from dict (or list of dicts)."""
    if data is None:
        return None
    if isinstance(data, list):
        return [model_class(**item) if isinstance(item, dict) else item for item in data]
    if isinstance(data, dict):
        return model_class(**data)
    return data


# =============================================================================
# Snapshot build/restore
# =============================================================================
def _build_state_snapshot() -> dict:
    """Capture current session state into a serializable dict."""
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "saved_at": datetime.now().isoformat(),
    }
    
    # Intake: profile object + conversation history
    if "profile" in st.session_state and st.session_state.profile is not None:
        snapshot["profile"] = _serialize_pydantic(st.session_state.profile)
    
    # Intake working state — fields collected incrementally
    if "profile_state" in st.session_state:
        ps = st.session_state.profile_state
        snapshot["profile_state"] = {
            "fields": dict(ps.fields) if hasattr(ps, "fields") else {},
            "evidence": _serialize_pydantic(ps.evidence) if hasattr(ps, "evidence") else [],
        }
    
    if "intake_messages" in st.session_state:
        # Serialize LangChain messages: store type + content
        messages_data = []
        for msg in st.session_state.intake_messages:
            msg_type = msg.__class__.__name__  # "HumanMessage" or "AIMessage"
            content = msg.content
            messages_data.append({"type": msg_type, "content": content})
        snapshot["intake_messages"] = messages_data
    
    # Evidence: list of EvidenceAttachment objects
    if "evidence_files" in st.session_state:
        snapshot["evidence_files"] = _serialize_pydantic(st.session_state.evidence_files)
    
    # Assessment: AssessmentReport object
    if "assessment_report" in st.session_state and st.session_state.assessment_report is not None:
        snapshot["assessment_report"] = _serialize_pydantic(st.session_state.assessment_report)
    
    # Recommendations: RemediationPlan object
    if "remediation_plan" in st.session_state and st.session_state.remediation_plan is not None:
        snapshot["remediation_plan"] = _serialize_pydantic(st.session_state.remediation_plan)
    
    return snapshot


def _restore_state_snapshot(snapshot: dict) -> bool:
    """
    Restore session state from a snapshot dict.
    Returns True on success, False if incompatible schema or invalid data.
    """
    if not isinstance(snapshot, dict):
        return False
    
    # Schema version check
    snapshot_version = snapshot.get("schema_version")
    if snapshot_version != SCHEMA_VERSION:
        return False
    
    # Lazy imports to avoid circular dependencies at module load
    from models import (
        AISystemProfile,
        EvidenceAttachment,
        AssessmentReport,
        RemediationPlan,
    )
    from langchain_core.messages import HumanMessage, AIMessage
    
    try:
        # Restore intake profile
        if "profile" in snapshot:
            st.session_state.profile = _deserialize_pydantic(
                snapshot["profile"], AISystemProfile
            )
        
        # Restore profile_state (incremental fields collected during intake)
        if "profile_state" in snapshot:
            from intake_agent_v2 import ProfileStateV2, build_intake_agent_v2
            ps = ProfileStateV2()
            ps_data = snapshot["profile_state"]
            if "fields" in ps_data:
                ps.fields = ps_data["fields"]
            if "evidence" in ps_data:
                ps.evidence = _deserialize_pydantic(ps_data["evidence"], EvidenceAttachment) or []
            st.session_state.profile_state = ps
            # Rebuild the agent bound to the restored state
            st.session_state.intake_agent = build_intake_agent_v2(ps)
        
        # Restore intake conversation
        if "intake_messages" in snapshot:
            messages = []
            for msg_data in snapshot["intake_messages"]:
                msg_type = msg_data["type"]
                content = msg_data["content"]
                if msg_type == "HumanMessage":
                    messages.append(HumanMessage(content=content))
                elif msg_type == "AIMessage":
                    messages.append(AIMessage(content=content))
            st.session_state.intake_messages = messages
        
        # Restore evidence
        if "evidence_files" in snapshot:
            st.session_state.evidence_files = _deserialize_pydantic(
                snapshot["evidence_files"], EvidenceAttachment
            ) or []
        
        # Restore assessment
        if "assessment_report" in snapshot:
            st.session_state.assessment_report = _deserialize_pydantic(
                snapshot["assessment_report"], AssessmentReport
            )
        
        # Restore recommendations
        if "remediation_plan" in snapshot:
            st.session_state.remediation_plan = _deserialize_pydantic(
                snapshot["remediation_plan"], RemediationPlan
            )
        
        return True
    
    except Exception as e:
        print(f"Failed to restore state: {e}")
        return False


# =============================================================================
# Public API — file-based save/restore
# =============================================================================
def export_state_to_json() -> str:
    """
    Build a JSON string of the current session state (for download).
    Returns pretty-printed JSON ready for st.download_button.
    """
    snapshot = _build_state_snapshot()
    return json.dumps(snapshot, indent=2, default=str)


def import_state_from_json(json_bytes: bytes) -> bool:
    """
    Restore session state from an uploaded JSON file (bytes from file uploader).
    Returns True on success, False if data is invalid or incompatible.
    """
    try:
        snapshot = json.loads(json_bytes.decode("utf-8"))
        return _restore_state_snapshot(snapshot)
    except Exception as e:
        print(f"Import from JSON failed: {e}")
        return False


def clear_state() -> bool:
    """Wipe current in-memory session state."""
    try:
        keys_to_clear = [
            "profile",
            "profile_state",
            "intake_agent",
            "intake_messages",
            "intake_complete",
            "evidence_files",
            "assessment_report",
            "remediation_plan",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        return True
    except Exception as e:
        print(f"Clear state failed: {e}")
        return False


def get_session_summary() -> dict:
    """
    Return a human-readable summary of what's in the current session.
    Used by the Session page to show "you have X uploaded".
    """
    summary = {
        "has_profile": st.session_state.get("profile") is not None,
        "intake_messages_count": len(st.session_state.get("intake_messages", [])),
        "evidence_count": len(st.session_state.get("evidence_files", [])),
        "has_assessment": st.session_state.get("assessment_report") is not None,
        "has_recommendations": st.session_state.get("remediation_plan") is not None,
    }
    if summary["has_profile"]:
        summary["system_name"] = st.session_state.profile.system_name
    return summary


# =============================================================================
# Compatibility shims (no-ops, kept so existing code doesn't break)
# =============================================================================
def save_state() -> bool:
    """No-op. File-based save replaces auto-save."""
    return True


def load_state() -> bool:
    """No-op. File-based restore replaces auto-load."""
    return False


def init_storage():
    """No-op. No browser bridge needed in file-based mode."""
    pass


def has_saved_state() -> bool:
    """Always returns False in file-based mode."""
    return False


def get_saved_at() -> Optional[str]:
    """Returns None in file-based mode."""
    return None