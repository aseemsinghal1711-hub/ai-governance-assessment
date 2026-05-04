"""
Pydantic models for the AI Governance Assessment workflow.

These models define the structured data that gets passed between agents:
- AISystemProfile: produced by the Intake Agent
- AssessmentReport: produced by the Assessment Agent
- RemediationPlan: produced by the Recommendation Agent

Structured outputs ensure agents communicate cleanly without parsing free-form text.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional

    # =============================================================================
# Evidence attachment - new for Stage 6.2
# =============================================================================
class EvidenceAttachment(BaseModel):
    """An evidence document the user has attached to a profile claim."""
    
    field_name: str = Field(
        description="The profile field this evidence supports "
                    "(e.g., 'has_documented_policy', 'has_bias_testing')"
    )
    file_path: str = Field(
        description="Path to the original file (for re-reading if needed)"
    )
    filename: str = Field(
        description="Original filename"
    )
    file_type: str = Field(
        description="File extension"
    )
    claimed_purpose: str = Field(
        description="What the user said this document demonstrates"
    )
    extracted_text: str = Field(
        description="Full text extracted from the document"
    )
    page_count: Optional[int] = Field(
        default=None,
        description="Number of pages/sheets/sections"
    )
    extraction_warnings: list[str] = Field(
        default_factory=list,
        description="Any extraction issues"
    )


# =============================================================================
# Profile - what the Intake Agent produces
# =============================================================================
class AISystemProfile(BaseModel):
    """
    Structured representation of an AI system being assessed.
    All fields are required — the Intake Agent should not finish until
    these are populated. Use 'Unknown' or empty list if user truly cannot answer.
    """
    
    # Basic identification
    system_name: str = Field(
        description="Internal name or identifier for the AI system"
    )
    purpose: str = Field(
        description="What the AI system is designed to do, in business terms"
    )
    business_unit: str = Field(
        description="Which business unit / department owns this AI system"
    )
    
    # Technical characterization
    ai_type: str = Field(
        description="Type of AI: e.g., 'ML classification model', 'LLM-based chatbot', "
                    "'computer vision', 'recommendation engine', 'generative AI'"
    )
    is_third_party_model: bool = Field(
        description="Whether the AI relies on a third-party model (e.g., GPT-4, "
                    "Claude, Gemini) vs. a model trained in-house"
    )
    
    # Decisions and impact
    decisions_made: list[str] = Field(
        description="List of decisions or outputs the AI system produces. "
                    "Be specific: 'ranks job candidates' not just 'helps with hiring'"
    )
    affects_individuals: bool = Field(
        description="Whether the AI's output materially affects individuals "
                    "(e.g., hiring decisions, credit approval, content moderation)"
    )
    affected_parties: list[str] = Field(
        description="Categories of people affected: e.g., 'job applicants', "
                    "'customers', 'employees', 'general public'"
    )
    
    # Deployment context
    deployment_geographies: list[str] = Field(
        description="Where the system is deployed. Use country/region names. "
                    "Critical for regulatory classification (EU vs US vs other)"
    )
    deployment_sector: str = Field(
        description="Industry sector: 'banking', 'healthcare', 'HR', 'retail', etc. "
                    "Some sectors have specific regulatory overlay"
    )
    
    # Data
    training_data_sources: list[str] = Field(
        description="Where training data came from. e.g., 'internal HR records', "
                    "'public web data', 'licensed dataset', 'synthetic'. "
                    "If using a third-party model, the user may not know — note that."
    )
    processes_personal_data: bool = Field(
        description="Whether the AI system processes personal data (PII)"
    )
    processes_sensitive_data: bool = Field(
        description="Whether the AI system processes sensitive personal data "
                    "(health, race, biometric, etc. per GDPR Article 9)"
    )
    
    # Existing governance
    has_documented_policy: bool = Field(
        description="Whether the organization has a documented AI policy that "
                    "applies to this system"
    )
    has_impact_assessment: bool = Field(
        description="Whether an AI impact assessment has been performed for this system"
    )
    has_human_oversight: bool = Field(
        description="Whether humans review or can override the AI's decisions"
    )
    has_monitoring: bool = Field(
        description="Whether the system is actively monitored post-deployment for "
                    "performance, drift, or issues"
    )
    has_bias_testing: bool = Field(
        description="Whether bias and fairness testing has been performed"
    )
    
    # Free-text context the agent can capture
    additional_context: str = Field(
        default="",
        description="Any other context the user shared that didn't fit other fields"
    )

    # Evidence attachments (new in Stage 6.2)
    evidence_attachments: list[EvidenceAttachment] = Field(
        default_factory=list,
        description="Documents the user has uploaded as evidence for their claims. "
                    "Each links to a specific profile field via field_name."
    )


# =============================================================================
# Assessment - what the Assessment Agent produces
# =============================================================================
GapStatus = Literal[
    "met_with_evidence",        # Claimed True AND document substantiates the claim
    "met_claimed_unverified",   # Claimed True but no document provided
    "evidence_partial",         # Document exists but only partially substantiates
    "evidence_inadequate",      # Document exists but does NOT substantiate the claim
    "partial",                  # Some elements present but gaps exist (legacy, no specific evidence)
    "not_met",                  # Significant gap; no claim or claim was False
    "not_applicable",           # Control truly doesn't apply to this system
]
GapSeverity = Literal["low", "medium", "high", "critical"]


class GapFinding(BaseModel):
    """A single gap finding for one control / subcategory."""
    
    control_id: str = Field(
        description="The framework-specific ID, e.g., 'A.6.1.4', 'GOVERN-1.1'"
    )
    framework: str = Field(
        description="'ISO 42001', 'NIST AI RMF', or 'EU AI Act'"
    )
    control_title: str = Field(
        description="Short title of the control"
    )
    status: GapStatus = Field(
        description="met = fully satisfied; partial = some elements present; "
                    "not_met = significant gap; not_applicable = doesn't apply to this system"
    )
    severity: GapSeverity = Field(
        description="Risk severity if this gap is not addressed. Critical = immediate "
                    "regulatory or fundamental rights risk. Low = good practice but not urgent."
    )
    reasoning: str = Field(
        description="Brief explanation of why this status was assigned, citing "
                    "specific facts from the AI system profile"
    )
    evidence_assessment: Optional[str] = Field(
        default=None,
        description="If evidence was provided for this control, brief assessment "
                    "of the document's adequacy. None if no evidence was provided. "
                    "e.g., 'AI policy covers governance principles but does not "
                    "specify bias testing cadence required by EU AI Act Article 10.'"
    )
    evidence_filename: Optional[str] = Field(
        default=None,
        description="Filename of the evidence document evaluated (if any)"
    )


class AssessmentReport(BaseModel):
    """The full assessment output from the Assessment Agent."""
    
    # EU AI Act classification
    eu_ai_act_risk_tier: Literal[
        "unacceptable", "high", "limited", "minimal", "not_applicable"
    ] = Field(
        description="EU AI Act risk classification. 'not_applicable' if system "
                    "is not deployed in EU and has no EU outputs"
    )
    eu_ai_act_reasoning: str = Field(
        description="Why this classification: cite specific Annex III categories, "
                    "Article 5 prohibitions, or reasons for not_applicable"
    )
    
    # Gap findings across frameworks
    findings: list[GapFinding] = Field(
        description="All gap findings, across all three frameworks. "
                    "Should cover 10-25 most important controls/subcategories."
    )
    
    # Cross-framework synthesis
    cross_framework_themes: list[str] = Field(
        description="Themes where multiple frameworks identify similar gaps. "
                    "e.g., 'Bias testing missing across all three frameworks (ISO A.6.1.4, "
                    "NIST MEASURE-2.11, EU AI Act Article 10 data quality)'"
    )
    
    # Summary
    overall_maturity_summary: str = Field(
        description="2-3 sentence summary of the organization's AI governance "
                    "maturity for this system"
    )
    immediate_concerns: list[str] = Field(
        description="Concerns requiring immediate attention. Focus on regulatory risks "
                    "and fundamental rights issues."
    )


# =============================================================================
# Remediation - what the Recommendation Agent produces
# =============================================================================
EffortLevel = Literal["low", "medium", "high"]


class RemediationAction(BaseModel):
    """A single remediation action."""
    
    title: str = Field(
        description="Short action title, action-oriented (start with a verb)"
    )
    description: str = Field(
        description="What needs to happen, in 2-3 sentences"
    )
    addresses_findings: list[str] = Field(
        description="List of control IDs this action addresses, "
                    "e.g., ['A.6.1.4', 'MEASURE-2.11']"
    )
    suggested_owner: str = Field(
        description="Suggested role to own this action: e.g., 'AI Risk Officer', "
                    "'Data Science Lead', 'Legal'"
    )
    effort: EffortLevel = Field(
        description="Estimated effort to complete"
    )
    success_criteria: str = Field(
        description="How we'll know this is done. Specific and measurable."
    )


class RemediationPlan(BaseModel):
    """The full remediation plan from the Recommendation Agent."""
    
    quick_wins: list[RemediationAction] = Field(
        description="Low-effort, high-impact actions to take in the first 30 days"
    )
    foundation_phase: list[RemediationAction] = Field(
        description="Must-have controls and processes (next 1-3 months). "
                    "These typically address regulatory baseline and critical gaps."
    )
    maturity_phase: list[RemediationAction] = Field(
        description="Deeper governance work (3-9 months). Builds robust ongoing capabilities."
    )
    optimization_phase: list[RemediationAction] = Field(
        description="Excellence-level actions (9+ months). Continuous improvement, "
                    "leading practice, optimization."
    )
    
    executive_summary: str = Field(
        description="3-4 sentence summary suitable for senior leadership. "
                    "Conveys urgency, effort, and key outcomes."
    )
    # =============================================================================
# Intermediate models used during assessment phases
# =============================================================================

class EUAIActClassification(BaseModel):
    """Output of Phase 1: EU AI Act risk classification."""
    
    risk_tier: Literal[
        "unacceptable", "high", "limited", "minimal", "not_applicable"
    ] = Field(
        description="The EU AI Act risk tier for this system"
    )
    reasoning: str = Field(
        description="2-4 sentences explaining the classification, citing specific "
                    "Annex III categories, Article 5 prohibitions, or Article 6(3) "
                    "exception logic where relevant"
    )
    annex_iii_categories: list[str] = Field(
        default_factory=list,
        description="Annex III categories that apply, e.g., ['ANNEX-III-4-EMPLOYMENT']. "
                    "Empty list if not high-risk under Annex III."
    )
    triggers_gpai_obligations: bool = Field(
        description="Whether the system uses a third-party GPAI model that may trigger "
                    "additional GPAI provider obligations on the upstream provider"
    )


class RelevantControlsSelection(BaseModel):
    """Output of Phase 2: Selection of framework controls relevant to this system."""
    
    relevant_control_ids: list[str] = Field(
        description="List of control/subcategory IDs relevant to assess for this system. "
                    "Use exact IDs from frameworks: 'A.2.2', 'GOVERN-1.1', 'ANNEX-III-4-EMPLOYMENT', etc. "
                    "Aim for 15-25 items total across the three frameworks - the most relevant ones, "
                    "not all of them."
    )
    selection_reasoning: str = Field(
        description="Brief explanation of which themes drove the selection. "
                    "e.g., 'Focused on bias, human oversight, transparency, and "
                    "data governance given high-risk EU AI Act classification'"
    )


class CrossFrameworkSynthesis(BaseModel):
    """Output of Phase 4: Cross-framework themes."""
    
    themes: list[str] = Field(
        description="Themes where multiple frameworks identify the same underlying gap. "
                    "Each theme should cite specific control IDs across frameworks. "
                    "e.g., 'Bias testing absent across all three frameworks "
                    "(ISO A.6.1.4, NIST MEASURE-2.11, EU AI Act Article 10)'"
    )


class ExecutiveSummary(BaseModel):
    """Output of Phase 5: Executive-level summary."""
    
    overall_maturity_summary: str = Field(
        description="2-3 sentences summarizing AI governance maturity for this system, "
                    "suitable for senior leadership"
    )
    immediate_concerns: list[str] = Field(
        description="Top 3-5 concerns requiring immediate attention. Focus on "
                    "regulatory exposure and fundamental rights risks."
    )
