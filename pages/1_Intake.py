"""Intake Page - chat-based interview with the AI Governance agent."""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from intake_agent_v2 import build_intake_agent_v2, ProfileStateV2
import persistence
from models import AISystemProfile

# =============================================================================
# Initialize persistence bridge (must run on every page for save to work)
# =============================================================================
persistence.init_storage()

# =============================================================================
# Page setup
# =============================================================================
st.title("🗣️ 1. Intake")
st.markdown(
    "Have a conversation with the AI Governance Specialist. The agent will ask "
    "structured questions about your AI system, then move you to evidence upload."
)
st.divider()


# =============================================================================
# Session state initialization
# =============================================================================
if "profile_state" not in st.session_state:
    st.session_state.profile_state = ProfileStateV2()

if "intake_agent" not in st.session_state:
    st.session_state.intake_agent = build_intake_agent_v2(st.session_state.profile_state)

if "intake_messages" not in st.session_state:
    # Kick off conversation with the agent's opening greeting
    with st.spinner("Connecting to AI Governance Specialist..."):
        try:
            initial = st.session_state.intake_agent.invoke({
                "messages": [HumanMessage(content="Hi, I'm ready to start.")]
            })
            st.session_state.intake_messages = initial["messages"]
        except Exception as e:
            st.error(f"Failed to start conversation: {e}")
            st.stop()

if "profile" not in st.session_state:
    st.session_state.profile = None


# =============================================================================
# Helpers
# =============================================================================
KICKOFF_MESSAGE = "Hi, I'm ready to start."


def extract_text(content):
    """Extract clean text from message content (handles strings or list-of-blocks)."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                # Standard format: {"type": "text", "text": "..."}
                text = block.get("text", "")
                if text:
                    parts.append(text)
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return str(content).strip()


def try_finalize_profile():
    """If the agent said INTAKE COMPLETE and we have all fields, build the profile."""
    if not st.session_state.intake_messages:
        return
    
    last = st.session_state.intake_messages[-1]
    if not isinstance(last, AIMessage):
        return
    
    last_text = extract_text(last.content)
    if "INTAKE COMPLETE" not in last_text:
        return
    
    state = st.session_state.profile_state
    missing = [f for f in state.REQUIRED_FIELDS if f not in state.fields]
    
    if missing:
        st.warning(
            f"The agent signaled INTAKE COMPLETE but these required fields are missing: "
            f"`{', '.join(missing)}`. Continue the conversation to fill them, or reset and start over."
        )
        return
    
    try:
        fields = dict(state.fields)
        fields.setdefault("additional_context", "")
        profile = AISystemProfile(**fields)
        profile.evidence_attachments = list(state.evidence)
        st.session_state.profile = profile
    except Exception as e:
        st.error(f"Profile validation error: {e}")


def reset_intake():
    """Clear all intake state and start fresh."""
    # Clear localStorage first so refresh doesn't restore old data
    persistence.clear_state()
    # Then re-initialize fresh in-memory state for this page
    st.session_state.profile_state = ProfileStateV2()
    st.session_state.intake_agent = build_intake_agent_v2(st.session_state.profile_state)
    st.session_state.profile = None
    if "intake_messages" in st.session_state:
        del st.session_state.intake_messages


# Always check for completion on every render
try_finalize_profile()


# =============================================================================
# Render the conversation
# =============================================================================
for msg in st.session_state.intake_messages:
    if isinstance(msg, HumanMessage):
        # Hide the kickoff message from the visible chat
        text = extract_text(msg.content)
        if text == KICKOFF_MESSAGE:
            continue
        with st.chat_message("user"):
            st.markdown(text)
    
    elif isinstance(msg, AIMessage):
        text = extract_text(msg.content)
        # Skip empty messages (sometimes happen with tool-calling messages)
        if not text:
            continue
        with st.chat_message("assistant"):
            st.markdown(text)


# =============================================================================
# Input or completion state
# =============================================================================
if st.session_state.profile is None:
    user_input = st.chat_input("Type your response here...")
    if user_input:
        st.session_state.intake_messages.append(HumanMessage(content=user_input))
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.intake_agent.invoke({
                    "messages": st.session_state.intake_messages
                })
                st.session_state.intake_messages = result["messages"]
            except Exception as e:
                st.error(f"Agent error: {e}")
        try_finalize_profile()
        # Auto-save after each exchange so partial intake survives refresh
        persistence.save_state()
        st.rerun()
else:
    # Intake complete — show success card with summary
    st.success("✅ Intake complete")
    
    profile = st.session_state.profile
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**System:** {profile.system_name}")
            st.markdown(f"**Sector:** {profile.deployment_sector}")
        with col2:
            st.markdown(f"**Geography:** {', '.join(profile.deployment_geographies)}")
            st.markdown(f"**Evidence attached:** {len(profile.evidence_attachments)}")
    
    st.markdown("### What's next")
    st.markdown(
        "- Continue to **2. Evidence** in the sidebar to upload supporting documents\n"
        "- Or skip ahead to **3. Assessment** if no additional evidence is needed"
    )
    
    if st.button("🔄 Start over", type="secondary"):
        reset_intake()
        st.rerun()


# =============================================================================
# Diagnostic panel (collapsed by default; useful when something looks off)
# =============================================================================
with st.expander("🔧 Diagnostics", expanded=False):
    state = st.session_state.profile_state
    collected = len(state.fields)
    required = len(state.REQUIRED_FIELDS)
    st.markdown(f"**Fields collected:** {collected} / {required}")
    
    if collected < required:
        missing = [f for f in state.REQUIRED_FIELDS if f not in state.fields]
        st.markdown(f"**Still needed:** `{', '.join(missing)}`")
    
    st.json({
        "fields": state.fields,
        "evidence_count": len(state.evidence),
        "evidence_filenames": [e.filename for e in state.evidence],
        "profile_finalized": st.session_state.profile is not None,
    })