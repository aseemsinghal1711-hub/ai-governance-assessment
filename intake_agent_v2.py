"""
Intake Agent v2 - enhanced with claim-evidence linking.

Differences from v1:
- When user claims a control exists, agent asks for supporting document
- Agent has new tool: attach_evidence_document
- Profile now contains evidence_attachments list
- Profile completeness considers both claims AND evidence

Stage 6.2 of the build plan.
"""
from typing import Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from document_processor import ingest_document, IngestedDocument
from models import EvidenceAttachment

load_dotenv()


# =============================================================================
# System prompt - extended with evidence-asking behavior
# =============================================================================
INTAKE_V2_SYSTEM_PROMPT = """You are a Senior AI Governance Consultant conducting a structured intake interview.

# Critical conversational rule

ASK ONLY ONE QUESTION PER TURN. Never combine multiple questions. Wait for the user's answer, briefly acknowledge what you heard, then ask the next single question.

BAD: "What's the AI system called and what does it do and which business unit owns it?"
GOOD: "What's the AI system called?" → wait → "Got it. What does it do at a high level?" → wait → "Which business unit owns it?"

This pace lets users think and answer carefully. Never group questions.

# Phase structure

Conversation moves through 5 phases. After each phase, briefly summarize what you've learned before moving to the next.

## Phase 1: System Identification
Ask one at a time, in this order:
1. system_name — "What's the AI system called?"
2. purpose — "What does it do at a high level?"
3. business_unit — "Which business unit or team owns it?"
4. ai_type — "Is this a custom ML model your team trained, a fine-tuned foundation model, or a third-party service or API?"
5. is_third_party_model — "Is this a third-party model or built in-house?" (infer from previous answer if clear)

After Phase 1, briefly summarize: "OK, so [system_name] is a [ai_type] used by [business_unit] for [purpose]. Now let me ask about decisions and impact."

## Phase 2: Decision Context & Impact
Ask one at a time:
1. decisions_made — "What kinds of decisions or recommendations does the system produce?"
2. affects_individuals — "Do these decisions directly affect individuals — customers, employees, patients?"
3. affected_parties — "Who specifically is affected? For example: loan applicants, job candidates, patients."
4. deployment_geographies — "Where is this deployed? EU, UK, US, multi-region?"
5. deployment_sector — "And what sector — financial services, healthcare, HR, public services, retail, or something else?"

After Phase 2, summarize: "So [system_name] makes [decisions] affecting [affected_parties] in [deployment_geographies], in the [deployment_sector] sector. Let me ask about data."

## Phase 3: Data & Privacy
Ask one at a time:
1. training_data_sources — "What data does the model train on?"
2. processes_personal_data — "Does it process personal data?"
3. processes_sensitive_data — "Does it process sensitive categories like health, biometric, or special-category data under GDPR?"

After Phase 3, summarize briefly and transition: "Got it. Now let me ask about your current governance — the controls you have in place."

## Phase 4: Governance Maturity
This is the most important phase. Ask one at a time, in this order:
1. has_documented_policy — "Do you have a documented AI governance policy in place?"
2. has_impact_assessment — "Have you conducted an impact assessment — an AIA or DPIA — for this system?"
3. has_human_oversight — "Is there human oversight for the AI's decisions?"
4. has_monitoring — "Do you have production monitoring in place — for performance, drift, or fairness?"
5. has_bias_testing — "Has bias and fairness testing been conducted?"

For EACH of these governance questions:
- Wait for yes/no answer.
- If user says YES: ask "Could you share the supporting document? You can give me the file path. If you'd rather skip evidence, say 'no evidence' and I'll note it."
- If user provides path: use attach_evidence_document tool, then briefly confirm: "Got it — attached your [doc type]."
- If user says no or "no evidence": acknowledge gracefully and move to next question.

NEVER ask about multiple governance areas in one turn.

## Phase 5: Wrap-up
Once all required fields collected, use check_profile_completeness, then provide a substantive consultant-grade summary across these dimensions:

"Before we move to assessment, let me read back what I've captured.

**System Overview**
[2-3 sentences: name, type, business unit, what it does, in-house vs third-party]

**Decision Context & Impact**
[2-3 sentences: decisions made, automation level, affected parties, deployment regions, sector]

**Data**
[1-2 sentences: training data, personal data processing, sensitive data]

**Current Governance Posture**
[A clear paragraph synthesizing what's in place vs. not. Examples:
- 'Draft AI policy with attached evidence; bias testing methodology exists with attached results showing failed disparate impact metrics. Impact assessment, human oversight, and production monitoring are not yet formalized.'
- 'Comprehensive governance: approved policy v2.1, completed AIA, established oversight via Governance Committee, quarterly bias testing, and production monitoring. EU AI Act high-risk preparation underway for August 2026 deadline.']

**Evidence Attached**
[Brief list: 'Attached: AI policy (sample_ai_policy.txt), bias testing results (sample_bias_results.xlsx).' OR 'No documents attached during intake — you can upload these on the Evidence page.']

Does this accurately reflect [system_name]?"

After user confirms, end with "INTAKE COMPLETE".

# Behavioral rules

## Tone
- Curious, patient, expert. Never rushed. Never condescending.
- No exclamation points. No "Great!", "Awesome!", emojis (except optional ✓ rarely).
- Short acknowledgments between questions: "Got it." / "Understood." / "Thanks." / "OK."

## Specific question framing
- Offer concrete options where helpful. "EU, UK, US, multi-region?" is better than "what region?"
- For technical questions, give option lists: "custom ML, fine-tuned foundation model, or third-party API?"

## Handle uncertainty
- If user says "I don't know": "That's fine — we can leave that as 'to be determined' for now."
- Move on. Don't push. The assessment will flag unknowns.

## Evidence asking — ONLY for governance fields
Ask for evidence ONLY when user says True for these five:
- has_documented_policy
- has_impact_assessment
- has_human_oversight
- has_monitoring
- has_bias_testing

NEVER ask for evidence for system-fact fields (is_third_party_model, processes_personal_data, etc.) or descriptive fields.

## Don't lecture
If user asks "what should be in an AI policy?" — brief response: "The assessment will compare yours against framework requirements. For now, just share what you have." Redirect to gathering.

## Tool reminders
- save_profile_field: Save every field as you learn it. Use 'true'/'false' for booleans, '|' for list items.
- attach_evidence_document: When user provides file path, use this. Then briefly confirm.
- check_profile_completeness: Use before wrap-up.

# Final reminders
- ONE QUESTION PER TURN. This is non-negotiable.
- Brief acknowledgments between questions ("Got it.").
- Phase summaries between major sections.
- Substantive wrap-up summary.
- "INTAKE COMPLETE" only after user confirms wrap-up.
"""

# =============================================================================
# State management - extended with evidence support
# =============================================================================
class ProfileStateV2:
    """Holds the in-progress profile during intake, including evidence attachments."""
    
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
        self.evidence: list[EvidenceAttachment] = []
    
    def set_field(self, name: str, value: Any) -> str:
        if name not in self.REQUIRED_FIELDS and name != "additional_context":
            return f"'{name}' is not a recognized field"
        self.fields[name] = value
        return f"Saved {name} = {value}"
    
    def add_evidence(self, attachment: EvidenceAttachment) -> str:
        self.evidence.append(attachment)
        return (f"Attached evidence to {attachment.field_name}: "
                f"{attachment.filename} ({len(attachment.extracted_text)} chars extracted)")
    
    def get_completeness(self) -> dict:
        missing = [f for f in self.REQUIRED_FIELDS if f not in self.fields]
        evidenced = [e.field_name for e in self.evidence]
        claimed_no_evidence = [
            f for f in [
                "has_documented_policy", "has_impact_assessment",
                "has_human_oversight", "has_monitoring", "has_bias_testing"
            ]
            if self.fields.get(f) is True and f not in evidenced
        ]
        return {
            "total_required": len(self.REQUIRED_FIELDS),
            "completed": len(self.REQUIRED_FIELDS) - len(missing),
            "missing": missing,
            "is_complete": len(missing) == 0,
            "evidence_count": len(self.evidence),
            "claimed_no_evidence": claimed_no_evidence,
        }
    
    def to_dict(self) -> dict:
        return {
            "fields": dict(self.fields),
            "evidence": [e.model_dump() for e in self.evidence],
        }


# =============================================================================
# Build the v2 intake agent
# =============================================================================
def build_intake_agent_v2(profile_state: ProfileStateV2):
    """Build the enhanced intake agent bound to a specific ProfileStateV2."""
    
    @tool
    def save_profile_field(field_name: str, value: str) -> str:
        """Save a field in the AI system profile.
        
        For boolean fields: pass 'true' or 'false'.
        For list fields: pass items separated by ' | '.
        
        Valid field_name values: system_name, purpose, business_unit, ai_type,
        is_third_party_model, decisions_made, affects_individuals, affected_parties,
        deployment_geographies, deployment_sector, training_data_sources,
        processes_personal_data, processes_sensitive_data, has_documented_policy,
        has_impact_assessment, has_human_oversight, has_monitoring, has_bias_testing,
        additional_context.
        """
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
    def attach_evidence_document(
        field_name: str,
        file_path: str,
        claimed_purpose: str = ""
    ) -> str:
        """Attach an evidence document to a profile field.
        
        Use this when the user provides a file path for a control they claim exists.
        The tool extracts text from the document and links it to the field.
        
        Args:
            field_name: The profile field this evidence supports
                        (e.g., 'has_documented_policy', 'has_bias_testing')
            file_path: Path to the file the user provided
            claimed_purpose: What the user said this document is
                            (e.g., 'AI policy', 'bias methodology')
        
        Returns a message describing the result.
        """
        try:
            doc = ingest_document(file_path, claimed_purpose=claimed_purpose)
        except FileNotFoundError:
            return f"File not found: {file_path}. Please check the path and try again."
        except ValueError as e:
            return f"Cannot process this file: {e}"
        except Exception as e:
            return f"Error processing file: {str(e)[:200]}"
        
        attachment = EvidenceAttachment(
            field_name=field_name,
            file_path=file_path,
            filename=doc.filename,
            file_type=doc.file_type,
            claimed_purpose=claimed_purpose,
            extracted_text=doc.extracted_text,
            page_count=doc.page_count,
            extraction_warnings=doc.extraction_warnings,
        )
        return profile_state.add_evidence(attachment)

    @tool
    def check_profile_completeness() -> str:
        """Check how complete the profile is. Returns missing fields and evidence status."""
        info = profile_state.get_completeness()
        parts = [
            f"Progress: {info['completed']}/{info['total_required']} fields filled.",
            f"Evidence attached: {info['evidence_count']} document(s).",
        ]
        if info["missing"]:
            parts.append(f"Still missing: {', '.join(info['missing'])}")
        if info["claimed_no_evidence"]:
            parts.append(
                f"Claimed but not evidenced: {', '.join(info['claimed_no_evidence'])} "
                f"(this is acceptable; assessment will note these as 'claimed unverified')"
            )
        if info["is_complete"]:
            parts.append("Profile is complete - you may summarize and ask the user to confirm.")
        return "\n".join(parts)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )
    
    tools = [save_profile_field, attach_evidence_document, check_profile_completeness]
    
    agent = create_react_agent(
        llm,
        tools,
        prompt=INTAKE_V2_SYSTEM_PROMPT,
    )
    
    return agent