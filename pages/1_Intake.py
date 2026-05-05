"""Intake Page - chat-based interview with the AI Governance agent."""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from intake_agent_v2 import build_intake_agent_v2, ProfileStateV2
from models import AISystemProfile


st.title("🗣️ 1. Intake")
st.markdown(
    "Have a conversation with the AI Governance Specialist. The agent will ask "
    "structured questions about your AI system and its current governance state."
)
st.divider()


# Initialize state
if "profile_state" not in st.session_state:
    st.session_state.profile_state = ProfileStateV2()

if "intake_agent" not in st.session_state:
    st.session_state.intake_agent = build_intake_agent_v2(st.session_state.profile_state)

if "intake_messages" not in st.session_state:
    st.session_state.intake_messages = []
    initial = st.session_state.intake_agent.invoke({
        "messages": [HumanMessage(content="Hi, I'm ready to start.")]
    })
    st.session_state.intake_messages = initial["messages"]

if "profile" not in st.session_state:
    st.session_state.profile = None


def try_finalize_profile():
    if not st.session_state.intake_messages:
        return
    last = st.session_state.intake_messages[-1]
    if not isinstance(last, AIMessage) or "INTAKE COMPLETE" not in last.content:
        return
    
    state = st.session_state.profile_state
    missing = [f for f in state.REQUIRED_FIELDS if f not in state.fields]
    
    if missing:
        st.warning(
            f"⚠️ Agent said INTAKE COMPLETE but missing required fields: `{', '.join(missing)}`. "
            f"Continue the conversation to fill these, or click **Reset conversation** below."
        )
        return
    
    try:
        fields = dict(state.fields)
        fields.setdefault("additional_context", "")
        profile = AISystemProfile(**fields)
        profile.evidence_attachments = list(state.evidence)
        st.session_state.profile = profile
    except Exception as e:
        st.error(f"⚠️ Profile validation error: {e}")


try_finalize_profile()


# Render chat history
for msg in st.session_state.intake_messages:
    if isinstance(msg, HumanMessage):
        if msg.content == "Hi, I'm ready to start.":
            continue
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        content_str = msg.content if isinstance(msg.content, str) else str(msg.content)
        if content_str and content_str.strip():
            with st.chat_message("assistant"):
                st.markdown(content_str)


# Input or completion state
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
        st.rerun()
else:
    st.success("✅ Intake complete!")
    profile = st.session_state.profile
    
    with st.container(border=True):
        st.markdown(f"**System:** {profile.system_name}")
        st.markdown(f"**Sector:** {profile.deployment_sector}")
        st.markdown(f"**Geography:** {', '.join(profile.deployment_geographies)}")
        st.markdown(f"**Evidence attached:** {len(profile.evidence_attachments)}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Next:** Continue to **2. Evidence** in the sidebar to upload more documents, or skip ahead to **3. Assessment**.")
    with col2:
        if st.button("🔄 Reset conversation", type="secondary"):
            st.session_state.profile_state = ProfileStateV2()
            st.session_state.intake_agent = build_intake_agent_v2(st.session_state.profile_state)
            st.session_state.intake_messages = []
            st.session_state.profile = None
            st.rerun()


with st.expander("🔍 Debug: profile state"):
    state = st.session_state.profile_state
    st.markdown(f"**Fields collected:** {len(state.fields)}/{len(state.REQUIRED_FIELDS)}")
    st.json({
        "fields": state.fields,
        "evidence_count": len(state.evidence),
        "evidence_filenames": [e.filename for e in state.evidence],
        "profile_finalized": st.session_state.profile is not None,
    })