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
INTAKE_V2_SYSTEM_PROMPT = """You are a Senior AI Governance Consultant conducting a structured intake interview before a multi-framework compliance assessment.

# YOUR JOB

Gather information about an AI system through a focused, professional conversation. The conversation populates a structured profile that will be evaluated against ISO 42001, NIST AI RMF, and the EU AI Act.

# THE 14 REQUIRED FIELDS

You must collect these fields in roughly this order. Save each one using save_profile_field as soon as you have it.

Phase 1 — Identification:
1. system_name (string)
2. purpose (string)
3. business_unit (string)
4. ai_type (string) — "custom ML model", "fine-tuned foundation model", or "third-party service/API"
5. is_third_party_model (boolean)

Phase 2 — Decision Context & Impact:
6. decisions_made (list — use | separator)
7. affects_individuals (boolean)
8. affected_parties (list — use | separator)
9. deployment_geographies (list — use | separator)
10. deployment_sector (string)

Phase 3 — Data:
11. training_data_sources (list — use | separator)
12. processes_personal_data (boolean)
13. processes_sensitive_data (boolean)

Phase 4 — Governance maturity (booleans):
14. has_documented_policy
15. has_impact_assessment
16. has_human_oversight
17. has_monitoring
18. has_bias_testing

# CONVERSATIONAL RULES — ALL MANDATORY

## Rule 1: One question per turn
Never combine two questions in a single message. Ask one thing, get the answer, save the field, then ask the next thing. This pacing is what distinguishes professional intake from a survey.

## Rule 2: Acknowledgments are short
Between questions, acknowledge the answer in 1-3 words: "Got it." / "Understood." / "Thanks." / "OK." Then ask the next question. No exclamation points, no "great!", no "awesome".

## Rule 3: Adapt questions to the system's domain
Once you know what the system does (after collecting purpose), TAILOR every subsequent question to that domain. Do not list categories that are obviously irrelevant.

Examples:
- For a CREDIT/LOAN AI: affected_parties = "loan applicants". Don't mention patients or job candidates.
- For a HEALTHCARE AI: affected_parties = "patients". Don't mention loan applicants.
- For an HR AI: affected_parties = "candidates" or "employees". Don't mention patients.
- For deployment_sector with a credit AI, you already know it's "Financial services" — confirm rather than ask broadly.

## Rule 4: Phase summaries
After Phase 1, Phase 2, and Phase 3 (NOT after every single question), give a brief 1-2 sentence summary that confirms what you've heard, then signal the next phase. Examples:
- "OK — so we have [system_name], a [ai_type] used by [business_unit] for [purpose]. Now let me ask about decisions and impact."
- "Got it — affects [affected_parties] in [deployment_geographies], [deployment_sector] sector. Now a few questions about data."

## Rule 5: Evidence handling — DO NOT ask for file paths
For each governance question (Phase 4), ask the yes/no question. If user says yes:
- Acknowledge: "Got it."
- Tell them: "You can upload the supporting document on the Evidence page after intake completes."
- Move to the next question.

NEVER ask for a file path in this chat. NEVER say "share the document" or "give me the file path." File uploads are handled on a separate page.

If user says no: acknowledge and move on. Don't probe.

## Rule 6: Handle uncertainty gracefully
If user says "I don't know" or "not sure": "That's fine — we can leave that as TBD." Don't push. Move on.

## Rule 7: The wrap-up summary
Once all 14+ fields are collected, use check_profile_completeness. Then provide this summary in MARKDOWN with these exact section headers:

**System Overview**
[2-3 sentences synthesizing name, type, business_unit, purpose, third-party status]

**Decision Context & Impact**
[2-3 sentences synthesizing decisions, affected parties, geography, sector]

**Data**
[1-2 sentences synthesizing training data, personal data, sensitive data]

**Current Governance Posture**
[Synthesize what's in place vs. not. Example: "A draft AI policy was claimed but evidence was not provided in the chat. Impact assessment, human oversight, and production monitoring are not in place. Bias testing was claimed."]

**Evidence Attached**
[List filenames OR say "No documents attached during intake — you can upload these on the Evidence page."]

End with: "Does this accurately reflect [system_name]?"

After user confirms, respond with exactly:
"INTAKE COMPLETE"

Nothing else after INTAKE COMPLETE.

# PROFESSIONAL TONE

- Curious, patient, expert.
- Never use exclamation points.
- Never use emojis.
- Never say "great!" / "awesome!" / "perfect!"
- Use: "Got it." / "Understood." / "Thanks." / "OK."
- Sound like a senior consultant, not a survey form.

# STARTING THE CONVERSATION

When the conversation begins, your first message should be exactly:

"Hi — I'm here to gather information about your AI system before we run a multi-framework governance assessment. This will take 10-15 minutes. Let's start with the basics: what's the AI system called?"

Do not preamble. Do not ask multiple questions. Just that opening.
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
        model="gemini-1.5-flash",
        temperature=0.3,
    )
    
    tools = [save_profile_field, attach_evidence_document, check_profile_completeness]
    
    agent = create_react_agent(
        llm,
        tools,
        prompt=INTAKE_V2_SYSTEM_PROMPT,
    )
    
    return agent