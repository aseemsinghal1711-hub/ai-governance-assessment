"""
Session Page - download/restore session backups and clear progress.

Provides three core operations:
1. Download backup: exports current session as JSON file
2. Restore from backup: uploads a JSON file and restores all state
3. Clear session: wipes everything to start fresh

In file-based persistence mode, users are responsible for downloading their
session before closing the browser. This is similar to "Save File" in any
desktop application.
"""
import streamlit as st
from datetime import datetime

import persistence


# =============================================================================
# Page setup
# =============================================================================
st.title("💾 Session")
st.markdown(
    "Save your progress as a file you can re-upload later, restore a previous "
    "session, or clear everything to start fresh."
)
st.divider()


# =============================================================================
# Current session summary
# =============================================================================
summary = persistence.get_session_summary()

if not summary["has_profile"] and summary["intake_messages_count"] == 0:
    st.info(
        "**No active session yet.** Once you start the Intake, your progress will appear here. "
        "You can also restore a previous session below if you have a backup file."
    )
else:
    st.markdown("### Current session")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if summary["has_profile"]:
            st.metric("System", summary.get("system_name", "—"))
        else:
            messages_count = summary["intake_messages_count"]
            st.metric("Intake messages", messages_count)
    
    with col2:
        st.metric("Evidence files", summary["evidence_count"])
    
    with col3:
        status_parts = []
        if summary["has_assessment"]:
            status_parts.append("Assessed")
        if summary["has_recommendations"]:
            status_parts.append("Recommended")
        status = " · ".join(status_parts) if status_parts else "In progress"
        st.metric("Status", status)
    
    st.divider()


# =============================================================================
# Download backup
# =============================================================================
st.markdown("### 📥 Download backup")
st.markdown(
    "Save your current progress to a file. Keep this file safe — you can "
    "upload it later (in this app or on another device) to pick up where you left off."
)

if summary["has_profile"] or summary["intake_messages_count"] > 0:
    json_str = persistence.export_state_to_json()
    
    # Filename includes system name if available + timestamp
    system_slug = "session"
    if summary["has_profile"]:
        system_slug = summary.get("system_name", "session").replace(" ", "_").replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"ai_gov_{system_slug}_{timestamp}.json"
    
    st.download_button(
        label="📥 Download backup file",
        data=json_str,
        file_name=filename,
        mime="application/json",
        type="primary",
        use_container_width=False,
    )
    
    st.caption(f"Filename: `{filename}` · Size: ~{len(json_str) // 1024} KB")
else:
    st.caption("Nothing to download yet — start the Intake first.")


st.divider()


# =============================================================================
# Restore from backup
# =============================================================================
st.markdown("### 📂 Restore from backup")
st.markdown(
    "Upload a previously downloaded backup file to restore your session. "
    "This will replace your current session."
)

uploaded_file = st.file_uploader(
    "Choose a backup file",
    type=["json"],
    key="backup_uploader",
    help="Select a JSON file you downloaded from this app earlier.",
)

if uploaded_file is not None:
    # Show preview before restoring
    try:
        import json
        preview = json.loads(uploaded_file.getvalue().decode("utf-8"))
        preview_saved_at = preview.get("saved_at", "Unknown")
        preview_system = preview.get("profile", {}).get("system_name", "—") if preview.get("profile") else "—"
        
        st.markdown("**Backup preview**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**System:** {preview_system}")
        with col2:
            # Format saved_at nicely if it's a valid ISO timestamp
            try:
                dt = datetime.fromisoformat(preview_saved_at)
                pretty_time = dt.strftime("%B %d, %Y at %I:%M %p")
            except Exception:
                pretty_time = preview_saved_at
            st.markdown(f"**Saved:** {pretty_time}")
        
        st.warning(
            "⚠️ Restoring will overwrite your current session. "
            "Make sure to download a backup first if you want to keep what you have."
        )
        
        if st.button("✅ Confirm restore", type="primary"):
            # Reset file uploader by clearing the file pointer
            uploaded_file.seek(0)
            success = persistence.import_state_from_json(uploaded_file.getvalue())
            
            if success:
                st.success("Session restored! Navigate to any page to see your data.")
                # Force a rerun so other pages see the new state
                st.rerun()
            else:
                st.error(
                    "Failed to restore. The file may be corrupted or from an "
                    "incompatible version of the app."
                )
    
    except Exception as e:
        st.error(f"Could not read the backup file: {e}")


st.divider()


# =============================================================================
# Clear session
# =============================================================================
st.markdown("### 🗑️ Clear session")
st.markdown(
    "Wipe all progress and start a new assessment. "
    "**This cannot be undone** — download a backup first if you want to keep your work."
)

if summary["has_profile"] or summary["intake_messages_count"] > 0:
    # Use a confirmation pattern: button reveals a confirm checkbox + final button
    if "clear_confirm_shown" not in st.session_state:
        st.session_state.clear_confirm_shown = False
    
    if not st.session_state.clear_confirm_shown:
        if st.button("🗑️ Clear my session", type="secondary"):
            st.session_state.clear_confirm_shown = True
            st.rerun()
    else:
        st.warning("Are you sure? This cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, clear everything", type="primary"):
                persistence.clear_state()
                st.session_state.clear_confirm_shown = False
                st.success("Session cleared.")
                st.rerun()
        with col2:
            if st.button("Cancel", type="secondary"):
                st.session_state.clear_confirm_shown = False
                st.rerun()
else:
    st.caption("Nothing to clear yet — start the Intake first.")