"""
Intake Agent - conducts a conversational interview with the user
to build an AISystemProfile.

Uses a system prompt to define behavior, a save_profile_field tool
to record information, and a completion check to know when to stop.
"""
from typing import Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()


# =============================================================================
# System prompt - this defines the agent's personality, goals, and behavior
# =============================================================================
INTAKE_SYSTEM_PROMPT = """You are an AI Governance Intake Specialist conducting a structured interview to assess an AI system against ISO 42001, NIST AI RMF, and the EU AI Act.

# Your role
You conduct a friendly but focused interview to characterize the AI system being assessed. You are like a senior consultant - patient, curious, and genuinely interested in understanding what the user is building.

# Your goals
Gather enough information to fill out an AISystemProfile with these fields:
- Basic identification: system_name, purpose, business_unit
- Technical: ai_type, is_third_party_model
- Decisions and impact: decisions_made, affects_individuals, affected_parties
- Deployment: deployment_geographies, deployment_sector
- Data: training_data_sources, processes_personal_data, processes_sensitive_data
- Existing governance: has_documented_policy, has_impact_assessment, has_human_oversight, has_monitoring, has_bias_testing

# How to behave
1. Start by greeting the user warmly and asking what AI system they want to assess. Begin with open questions ("tell me about it") rather than a list of questions.

2. As they describe the system, use the save_profile_field tool to record what you learn. Save fields as you confirm them, not when you guess them. Be conservative - if you're 80% sure, ask to confirm before saving.

3. Ask 1-3 questions per turn, not a wall of questions. Group related questions naturally ("Which countries is this deployed in, and what sector?").

4. Follow up on vague answers. "It uses AI" is not enough - you need specifics. "ML classification model" or "LLM-based summarization" is what you need.

5. Pay special attention to:
   - EU deployment (triggers EU AI Act analysis)
   - HR/hiring, credit scoring, healthcare, education, law enforcement (Annex III high-risk areas)
   - Whether the system makes decisions about individuals (drives risk classification)
   - Whether they use a third-party model (changes regulatory responsibilities)

6. If the user says "I don't know" for a field, save the field as "Unknown" and move on. Don't interrogate.

7. Periodically check the profile_completeness using the check_profile_completeness tool. Once it returns "complete", summarize what you've gathered and ask the user to confirm or correct it. Don't keep asking questions when you have enough.

8. After the user confirms the summary, end your turn with the exact phrase "INTAKE COMPLETE" so the orchestrator knows to proceed.

# Important constraints
- You are NOT performing the assessment yet - you are only gathering information.
- Don't lecture about regulations. If they ask "what does the EU AI Act require?", briefly note that the assessment phase will cover this and redirect to gathering information.
- Don't fabricate fields the user didn't tell you. Save what they said, not what you assumed.
- Be efficient. Most assessments need 5-8 conversational turns, not 20.
"""


# =============================================================================
# State management
# =============================================================================
# In a Streamlit context, we'll store the profile in session state.
# For now, we use a simple dict that the tools mutate.
# Streamlit integration happens in app.py.

class ProfileState:
    """Holds the in-progress profile during an intake conversation."""
    
    REQUIRED_FIELDS = [
        "system_name", "purpose", "business_unit",
        "ai_type", "is_third_party_model",
        "decisions_made", "affects_individuals", "affected_parties",
        "deployment_geographies", "deployment_sector",
        "training_data_sources", "processes_personal_data", "processes_sensitive_data",
        "has_documented_policy", "has_impact_assessment", 
        "has_human_oversight", "has_monitoring", "has_bias_testing",
    ]
    
    def __init__(self):
        self.fields: dict[str, Any] = {}
    
    def set_field(self, name: str, value: Any) -> str:
        """Save a field and return a confirmation string."""
        if name not in self.REQUIRED_FIELDS and name != "additional_context":
            return f"⚠️ '{name}' is not a recognized profile field. Valid fields: {', '.join(self.REQUIRED_FIELDS)}"
        self.fields[name] = value
        return f"✅ Saved {name} = {value}"
    
    def get_completeness(self) -> dict:
        """Return completeness info."""
        missing = [f for f in self.REQUIRED_FIELDS if f not in self.fields]
        return {
            "total_required": len(self.REQUIRED_FIELDS),
            "completed": len(self.REQUIRED_FIELDS) - len(missing),
            "missing": missing,
            "is_complete": len(missing) == 0,
        }
    
    def to_dict(self) -> dict:
        return dict(self.fields)


# =============================================================================
# Build the intake agent
# =============================================================================
def build_intake_agent(profile_state: ProfileState):
    """
    Build an intake agent bound to a specific ProfileState instance.
    
    The closure pattern (defining tools inside this function) lets the tools
    capture and mutate the specific profile_state instance for this session.
    """
    
    @tool
    def save_profile_field(field_name: str, value: str) -> str:
        """Save a field in the AI system profile.
        
        Use this whenever the user has clearly told you a piece of information.
        For boolean fields (e.g., processes_personal_data), pass 'true' or 'false'.
        For list fields (e.g., decisions_made), pass items separated by ' | '.
        
        Valid field_name values: system_name, purpose, business_unit, ai_type,
        is_third_party_model, decisions_made, affects_individuals, affected_parties,
        deployment_geographies, deployment_sector, training_data_sources,
        processes_personal_data, processes_sensitive_data, has_documented_policy,
        has_impact_assessment, has_human_oversight, has_monitoring, has_bias_testing,
        additional_context.
        """
        # Coerce simple types
        bool_fields = {
            "is_third_party_model", "affects_individuals",
            "processes_personal_data", "processes_sensitive_data",
            "has_documented_policy", "has_impact_assessment",
            "has_human_oversight", "has_monitoring", "has_bias_testing",
        }
        list_fields = {
            "decisions_made", "affected_parties",
            "deployment_geographies", "training_data_sources",
        }
        
        if field_name in bool_fields:
            coerced = value.strip().lower() in ("true", "yes", "y", "1")
        elif field_name in list_fields:
            coerced = [s.strip() for s in value.split("|") if s.strip()]
        else:
            coerced = value.strip()
        
        return profile_state.set_field(field_name, coerced)

    @tool
    def check_profile_completeness() -> str:
        """Check how complete the profile is. Returns a summary including missing fields.
        Call this when you think you might have enough info, before summarizing for the user.
        """
        info = profile_state.get_completeness()
        if info["is_complete"]:
            return (f"✅ Profile complete: {info['completed']}/{info['total_required']} "
                    f"fields filled. You can now summarize for the user and ask them to confirm.")
        else:
            return (f"📊 Progress: {info['completed']}/{info['total_required']} fields filled. "
                    f"Still missing: {', '.join(info['missing'])}")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,  # slightly lower for more consistent interview style
    )
    
    tools = [save_profile_field, check_profile_completeness]
    
    # The 'prompt' parameter sets the system message for every turn
    agent = create_react_agent(
        llm,
        tools,
        prompt=INTAKE_SYSTEM_PROMPT,
    )
    
    return agent