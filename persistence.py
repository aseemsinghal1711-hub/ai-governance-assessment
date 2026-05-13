"""
Persistence layer for AI Governance Assessment Tool.

Handles auto-save to browser localStorage and manual download/upload of session
backups. Data stays in user's browser (privacy-isolated per browser) with
optional JSON file export for portability across devices.

Architecture:
- save_state(): serializes session state to JSON, writes to localStorage
- load_state(): reads from localStorage, deserializes to session state
- export_state_to_json(): returns JSON string for download button
- import_state_from_json(): restores session from uploaded JSON
- clear_state(): wipes localStorage (used by "Start Fresh")
"""
import json
from datetime import datetime
from typing import Optional

import streamlit as st
from streamlit_local_storage import LocalStorage

# Schema version — increment when state structure changes incompatibly.
# load_state() checks this and refuses to load incompatible older versions.
SCHEMA_VERSION = "1.0"

# localStorage key under which we store the session blob
STORAGE_KEY = "ai_gov_session"

# Lazy singleton — created on first use, not at module import.
# This avoids errors when persistence.py is imported in contexts where
# Streamlit's session state isn't yet available.
_local_storage = None


def _get_storage():
    """Get or lazily create the LocalStorage instance."""
    global _local_storage
    if _local_storage is None:
        _local_storage = LocalStorage()
    return _local_storage


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


def _build_state_snapshot() -> dict:
    """Capture current session state into a serializable dict."""
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "saved_at": datetime.now().isoformat(),
        "current_page": st.session_state.get("current_page", "Intake"),
    }
    
    # Intake: profile object + conversation history
    if "profile" in st.session_state and st.session_state.profile is not None:
        snapshot["profile"] = _serialize_pydantic(st.session_state.profile)
        # Intake working state — incrementally-built fields during partial intake
    if "profile_state" in st.session_state:
        ps = st.session_state.profile_state
        snapshot["profile_state"] = {
            "fields": dict(ps.fields) if hasattr(ps, "fields") else {},
            "evidence": _serialize_pydantic(ps.evidence) if hasattr(ps, "evidence") else [],
        }
    
    if "intake_messages" in st.session_state:
        snapshot["intake_messages"] = st.session_state.intake_messages
    
    if "intake_complete" in st.session_state:
        snapshot["intake_complete"] = st.session_state.intake_complete
    
    # Evidence: list of EvidenceAttachment objects
    if "evidence_files" in st.session_state:
        snapshot["evidence_files"] = _serialize_pydantic(
            st.session_state.evidence_files
        )
    
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
        # In the future, add migration logic here for older versions
        return False
    
    # Lazy imports to avoid circular dependencies at module load
    from models import (
        AISystemProfile,
        EvidenceAttachment,
        AssessmentReport,
        RemediationPlan,
    )
    
    try:
        # Restore intake
        if "profile" in snapshot:
            st.session_state.profile = _deserialize_pydantic(
                snapshot["profile"], AISystemProfile
            )
            # Restore profile_state (incremental fields collected during intake)
        if "profile_state" in snapshot:
            # We lazy-import ProfileStateV2 to avoid module-load issues
            from intake_agent_v2 import ProfileStateV2
            ps = ProfileStateV2()
            ps_data = snapshot["profile_state"]
            if "fields" in ps_data:
                ps.fields = ps_data["fields"]
            if "evidence" in ps_data:
                ps.evidence = _deserialize_pydantic(ps_data["evidence"], EvidenceAttachment)
            st.session_state.profile_state = ps
        
        if "intake_messages" in snapshot:
            st.session_state.intake_messages = snapshot["intake_messages"]
        
        if "intake_complete" in snapshot:
            st.session_state.intake_complete = snapshot["intake_complete"]
        
        # Restore evidence
        if "evidence_files" in snapshot:
            st.session_state.evidence_files = _deserialize_pydantic(
                snapshot["evidence_files"], EvidenceAttachment
            )
        
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
        # Corrupted or malformed data — don't crash the app
        print(f"Failed to restore state: {e}")
        return False


# =============================================================================
# Public API
# =============================================================================
def save_state() -> bool:
    """
    Save current session state to browser localStorage.
    Called automatically after meaningful state changes.
    Returns True on success.
    """
    try:
        snapshot = _build_state_snapshot()
        json_blob = json.dumps(snapshot, default=str)
        _get_storage().setItem(STORAGE_KEY, json_blob)
        return True
    except Exception as e:
        print(f"Auto-save failed: {e}")
        return False


def load_state() -> bool:
    """
    Load session state from browser localStorage (auto-resume on app start).
    Returns True if state was loaded, False if no saved state existed.
    """
    try:
        json_blob = _get_storage().getItem(STORAGE_KEY)
        if not json_blob:
            return False
        
        snapshot = json.loads(json_blob)
        return _restore_state_snapshot(snapshot)
    except Exception as e:
        print(f"Auto-load failed: {e}")
        return False


def clear_state() -> bool:
    """
    Wipe saved state from localStorage AND clear current session.
    Used by "Start Fresh" button.
    """
    try:
        _get_storage().deleteItem(STORAGE_KEY)
        
        # Clear in-memory state too
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


def has_saved_state() -> bool:
    """Check whether saved state exists in localStorage."""
    try:
        json_blob = _get_storage().getItem(STORAGE_KEY)
        return bool(json_blob)
    except Exception:
        return False


def get_saved_at() -> Optional[str]:
    """Return the timestamp when state was last saved, or None."""
    try:
        json_blob = _get_storage().getItem(STORAGE_KEY)
        if not json_blob:
            return None
        snapshot = json.loads(json_blob)
        return snapshot.get("saved_at")
    except Exception:
        return None


def export_state_to_json() -> str:
    """
    Build a JSON string of the current session state (for download).
    Returns the JSON as a string, ready to be served by st.download_button.
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
        success = _restore_state_snapshot(snapshot)
        if success:
            # Also save to localStorage so it persists on next reload
            save_state()
        return success
    except Exception as e:
        print(f"Import from JSON failed: {e}")
        return False