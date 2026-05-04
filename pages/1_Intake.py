"""
Intake Page - browser-based conversational interview with the AI Governance agent.

Replaces the terminal-based intake from intake_agent_v2.py with a Streamlit chat UI.
The user has a back-and-forth conversation. When done, the profile is saved to
session state and the user can proceed to Evidence or Assessment.
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from intake_agent_v2 import build_intake_agent_v2, ProfileStateV2
from models import AISystemProfile


# =============================================================================
# Page header
# =============================================================================
st.title("🗣️ 1. Intake")
st.markdown(
    "Have a conversation with the AI Governance Specialist. The agent will ask about "
    "your AI system and its current governance state. You can stop anytime by clicking "
    "**Reset conversation** below."
)
st.divider()


# =============================================================================
# Initialize page-specific state
# =============================================================================
if "profile_state" not in st.session_state:
    st.session_state.profile_state = ProfileStateV2()

if "intake_agent" not in st.session_state:
    st.session_state.intake_agent = build_intake_agent_v2(st.session_state.profile_state)

if "intake_messages" not in st.session_state:
    st.session_state.intake_messages = []
    # Have the agent send the opening greeting
    initial_response = st.session_state.intake_agent.invoke({
        "messages": [HumanMessage(content="Hi, I'm ready to start.")]
    })
    st.session_state.intake_messages = initial_response["messages"]


# =============================================================================
# Helper: extract a profile from the conversation messages and state
# =============================================================================
def try_finalize_profile():
    """Check if the agent indicated completion, and if so, build the AISystemProfile."""
    if not st.session_state.intake_messages:
        return
    
    last_msg = st.session_state.intake_messages[-1]
    if not isinstance(last_msg, AIMessage):
        return
    
    if "INTAKE COMPLETE" not in last_msg.content:
        return
    
    state = st.session_state.profile_state
    
    # Check what's missing BEFORE trying to build
    missing_required = [f for f in state.REQUIRED_FIELDS if f not in state.fields]
    
    if missing_required:
        st.warning(
            f"⚠️ Agent said INTAKE COMPLETE but the following required fields are missing: "
            f"`{', '.join(missing_required)}`. The profile cannot be finalized. "
            f"You can either continue the conversation to fill these, or click "
            f"**Reset conversation** below to start over."
        )
        return
    
    try:
        fields = dict(state.fields)
        fields.setdefault("additional_context", "")
        
        profile = AISystemProfile(**fields)
        profile.evidence_attachments = list(state.evidence)
        st.session_state.profile = profile
    except Exception as e:
        st.error(
            f"⚠️ Profile validation error: {e}\n\n"
            f"Fields collected: {list(state.fields.keys())}\n\n"
            f"This usually means a field has the wrong type. Click **Reset conversation** "
            f"to start over, or check the debug expander for details."
        )


# =============================================================================
# Try to finalize on every render (handles refresh after intake completion)
# =============================================================================
try_finalize_profile()


# =============================================================================
# RENDER: the chat history
# =============================================================================
for msg in st.session_state.intake_messages:
    if isinstance(msg, HumanMessage):
        # Skip the kickoff "Hi, I'm ready to start" we sent programmatically
        if msg.content == "Hi, I'm ready to start.":
            continue
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        # Only render assistant messages that have text content (skip tool calls)
        if msg.content and msg.content.strip():
            with st.chat_message("assistant"):
                st.markdown(msg.content)


# =============================================================================
# RENDER: input or completion state
# =============================================================================
if st.session_state.profile is None:
    user_input = st.chat_input("Type your response here...")
    
    if user_input:
        # Add user message to history
        st.session_state.intake_messages.append(HumanMessage(content=user_input))
        
        # Show a spinner while the agent thinks
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.intake_agent.invoke({
                    "messages": st.session_state.intake_messages
                })
                st.session_state.intake_messages = result["messages"]
            except Exception as e:
                st.error(f"Agent error: {e}")
        
        # Check if the agent finished
        try_finalize_profile()
        
        # Force a rerun so the new messages render immediately
        st.rerun()
else:
    # Intake is complete — show success and CTAs
    st.success("✅ Intake complete!")
    
    profile = st.session_state.profile
    
    with st.container(border=True):
        st.markdown(f"**System:** {profile.system_name}")
        st.markdown(f"**Sector:** {profile.deployment_sector}")
        st.markdown(f"**Geography:** {', '.join(profile.deployment_geographies)}")
        st.markdown(f"**Evidence attached during intake:** {len(profile.evidence_attachments)}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Next steps")
        st.markdown(
            "Continue to **2. Evidence** in the sidebar to upload supporting "
            "documents, or skip ahead to **3. Assessment** if you've already provided "
            "all evidence during the conversation."
        )
    with col2:
        st.markdown("### Or start over")
        st.markdown("Reset and begin a new intake conversation.")
        if st.button("🔄 Reset conversation", type="secondary"):
            st.session_state.profile_state = ProfileStateV2()
            st.session_state.intake_agent = build_intake_agent_v2(st.session_state.profile_state)
            st.session_state.intake_messages = []
            st.session_state.profile = None
            st.rerun()


# =============================================================================
# DEBUG INFO (collapsible — useful during development)
# =============================================================================
with st.expander("🔍 Debug: profile state (developer view)"):
    state = st.session_state.profile_state
    st.markdown(f"**Fields collected:** {len(state.fields)}/{len(state.REQUIRED_FIELDS)}")
    st.json({
        "fields": state.fields,
        "evidence_count": len(state.evidence),
        "evidence_filenames": [e.filename for e in state.evidence],
        "profile_finalized": st.session_state.profile is not None,
    })