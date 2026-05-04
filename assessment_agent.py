"""
Assessment Agent - takes a completed AISystemProfile and produces an AssessmentReport.

Architecture: Sequential phases, each using structured outputs. This is more
reliable than a free-form agent for tasks with known workflow.

Phases:
1. EU AI Act risk classification
2. Identify relevant framework controls
3. Per-control gap evaluation
4. Cross-framework synthesis
5. Executive summary
"""
import time
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI

from models import (
    AISystemProfile,
    AssessmentReport,
    GapFinding,
    EUAIActClassification,
    RelevantControlsSelection,
    CrossFrameworkSynthesis,
    ExecutiveSummary,
)
from pydantic import BaseModel, Field

load_dotenv()

# =============================================================================
# Field-to-control mapping for evidence linking
# =============================================================================
# When a profile field has attached evidence, these are the controls
# where the evidence is relevant. Used to feed evidence into the right
# control evaluations.
EVIDENCE_FIELD_TO_CONTROLS = {
    "has_documented_policy": [
        # ISO 42001 - core policy controls only
        "A.2.2",  # AI policy
        "A.2.3",  # Alignment with other organizational policies
        "A.2.4",  # Review of AI policy
        # NIST - governance and policy framework
        "GOVERN-1.1",  # Legal/regulatory awareness (policy is foundational)
        "GOVERN-1.2",  # Trustworthiness characteristics integrated
        "GOVERN-1.4",  # Documentation and transparency policies
    ],
    "has_impact_assessment": [
        # ISO 42001 - impact assessment controls
        "A.5.2",  # AI system impact assessment process
        "A.5.3",  # Documentation of AI system impact assessments
        "A.5.4",  # Assessing AI system impact on individuals or groups
        "A.5.5",  # Assessing societal impacts of AI systems
        # NIST - mapping (which is essentially impact analysis)
        "MAP-1.1",  # Context established
        "MAP-2.1",  # Tasks and methods documented
        "MAP-3.1",  # Potential benefits and risks examined
        "MAP-5.1",  # Likelihood and impacts of risk identified
    ],
    "has_human_oversight": [
        # ISO 42001 - human oversight controls
        "A.9.2",  # Processes for the responsible use of AI systems
        "A.9.3",  # Objectives for responsible use of AI system
        "A.9.4",  # Intended use of the AI system
        # NIST - oversight related
        "GOVERN-3.2",  # Roles and responsibilities for AI lifecycle
        "MANAGE-2.4",  # Mechanisms to deactivate AI systems
    ],
    "has_monitoring": [
        # ISO 42001 - operational monitoring
        "A.6.2.6",  # AI system operation and monitoring
        "A.6.2.7",  # AI system technical documentation
        "A.7.2",  # Data for development and enhancement (ongoing)
        # NIST - measurement and management of operating systems
        "MEASURE-2.6",  # Computational performance and capacity
        "MEASURE-3.1",  # AI risks identified are tracked
        "MEASURE-3.2",  # Risk tracking documented
        "MEASURE-4.1",  # Continued performance assessment
        "MANAGE-2.2",  # Risk treatment options
        "MANAGE-2.3",  # Procedures established to scale risks
    ],
    "has_bias_testing": [
        # ISO 42001 - bias-specific controls
        "A.6.1.4",  # Addressing bias in data
        "A.7.4",  # Quality of data for AI systems (bias is part of quality)
        # NIST - bias measurement
        "MEASURE-2.2",  # Test sets and human-subject testing
        "MEASURE-2.5",  # AI system validity reviewed
        "MEASURE-2.7",  # Security and resilience evaluated (includes adversarial bias)
        "MEASURE-2.11",  # Fairness and bias evaluated
        # EU AI Act - data quality is the closest match (Article 10)
        # NOTE: ANNEX-III-5-ESSENTIAL-SERVICES is the classification, not the bias requirement
        # We're being more conservative here — bias evidence speaks to data quality, not classification per se
    ],
}


def _get_evidence_for_control(
    control_id: str,
    control_framework: str,
    control_title: str,
    control_content: str,
    profile,  # AISystemProfile
) -> tuple[str, str]:
    """
    Find evidence relevant to this control using LLM-based relevance scanning.
    
    Replaces the old rigid field-to-control mapping with semantic relevance
    judgment by the LLM. Returns (formatted_evidence, evidence_filenames) where
    formatted_evidence is the prompt-ready string of relevant quotes, and
    evidence_filenames is a comma-separated list of filenames that contributed.
    
    Returns ("", "") if no evidence is relevant.
    """
    if not profile.evidence_attachments:
        return "", ""
    
    # Run the relevance scanner against all attached evidence
    relevance_results = _scan_evidence_for_relevance(
        profile=profile,
        control_id=control_id,
        control_framework=control_framework,
        control_title=control_title,
        control_content=control_content,
    )
    
    if not relevance_results:
        return "", ""
    
    # Format for the evaluation prompt
    formatted_evidence = _format_evidence_for_evaluation(relevance_results)
    filenames = ", ".join(filename for filename, _ in relevance_results)
    
    return formatted_evidence, filenames

# =============================================================================
# Shared resources - embedding model and vector store
# =============================================================================
_embeddings_model = None
_collection = None


def _get_resources():
    """Lazy-load embedding model and vector store."""
    global _embeddings_model, _collection
    if _embeddings_model is None:
        _embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    if _collection is None:
        client = chromadb.PersistentClient(path="./ai_gov_chroma_db")
        _collection = client.get_collection(name="ai_governance")
    return _embeddings_model, _collection


def _retrieve_framework_items(query: str, n_results: int = 8) -> list[dict]:
    """Retrieve the top-N most relevant framework items for a query."""
    embeddings_model, collection = _get_resources()
    query_vector = embeddings_model.encode([query], convert_to_numpy=True)[0].tolist()
    results = collection.query(query_embeddings=[query_vector], n_results=n_results)
    items = []
    for item_id, doc, meta in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0]
    ):
        items.append({
            "id": item_id,
            "framework": meta["framework"],
            "title": meta["title"],
            "content": doc,
        })
    return items


def _retrieve_by_ids(ids: list[str]) -> list[dict]:
    """Retrieve specific items by ID."""
    _, collection = _get_resources()
    if not ids:
        return []
    results = collection.get(ids=ids)
    items = []
    for item_id, doc, meta in zip(
        results["ids"], results["documents"], results["metadatas"]
    ):
        items.append({
            "id": item_id,
            "framework": meta["framework"],
            "title": meta["title"],
            "content": doc,
        })
    return items

# =============================================================================
# Evidence relevance scanner (new in Stage 6.4)
# =============================================================================
class RelevanceQuote(BaseModel):
    """A specific quote from a document that's relevant to a control."""
    
    quote: str = Field(
        description="Exact text from the document. Must be a verbatim "
                    "quote, not paraphrased. Up to 300 chars."
    )
    explanation: str = Field(
        description="One sentence explaining how this quote relates to the control. "
                    "Be specific. Bad: 'This is relevant.' Good: 'This quote "
                    "establishes the bias testing cadence required by the control.'"
    )


class RelevanceScanResult(BaseModel):
    """Output of the relevance scanner for one document evaluated against one control."""
    
    is_relevant: bool = Field(
        description="Whether this document contains content meaningfully relevant "
                    "to the control. Be strict. 'Probably' or 'tangentially' = False. "
                    "Only True if the document has specific content about the control's "
                    "subject matter."
    )
    relevant_quotes: list[RelevanceQuote] = Field(
        default_factory=list,
        description="Up to 4 specific quotes if is_relevant is True. Empty list if not."
    )


SCANNER_PROMPT = """You are scanning a document to find content relevant to a specific governance control.

# The control we're evaluating
ID: {control_id}
Framework: {control_framework}
Title: {control_title}
What it requires:
{control_content}

# The document
Filename: {filename}
Document content:
{document_text}

# Your task
Determine whether this document contains content meaningfully relevant to the control above.

STRICT RELEVANCE STANDARD:
- 'Relevant' means the document has specific content addressing the control's subject matter, NOT just tangentially related concepts.
- A general AI policy mentioning "transparency" is NOT automatically relevant to every transparency-adjacent control. It's relevant only if it has content speaking to what THIS control specifically requires.
- A bias testing report is not relevant to a documentation control just because both involve documentation.
- When in doubt, mark as NOT relevant. False positives are worse than false negatives here.

If relevant, quote up to 4 specific passages from the document that establish the relevance. Use exact verbatim text, not paraphrases. Each quote must be self-contained enough to demonstrate the connection.

If the document has no specific content about the control's subject matter, set is_relevant=False and return empty quotes."""


def _scan_evidence_for_relevance(
    profile: AISystemProfile,
    control_id: str,
    control_framework: str,
    control_title: str,
    control_content: str,
) -> list[tuple[str, list[RelevanceQuote]]]:
    """
    Scan all attached evidence documents for content relevant to a specific control.
    
    Returns list of (filename, relevant_quotes) for each document with relevant content.
    Documents with no relevant content are filtered out.
    """
    if not profile.evidence_attachments:
        return []
    
    # Use a fast, cheap configuration for the scanner
    scanner_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,  # deterministic for scanning
    ).with_structured_output(RelevanceScanResult)
    
    relevant_findings = []
    
    for evidence in profile.evidence_attachments:
        # Truncate document text to keep prompt size reasonable
        doc_text = evidence.extracted_text[:8000]
        
        prompt = SCANNER_PROMPT.format(
            control_id=control_id,
            control_framework=control_framework,
            control_title=control_title,
            control_content=control_content[:1500],
            filename=evidence.filename,
            document_text=doc_text,
        )
        
        try:
            result = scanner_llm.invoke(prompt)
            if result.is_relevant and result.relevant_quotes:
                relevant_findings.append((evidence.filename, result.relevant_quotes))
        except Exception as e:
            # Skip this document if scanning fails; don't crash the whole assessment
            pass
    
    return relevant_findings


def _format_evidence_for_evaluation(
    relevance_results: list[tuple[str, list[RelevanceQuote]]]
) -> str:
    """Format scanner output into a string for the Phase 3 evaluation prompt."""
    if not relevance_results:
        return "No evidence documents contained content specifically relevant to this control."
    
    parts = []
    for filename, quotes in relevance_results:
        parts.append(f"\n=== From document: {filename} ===")
        for i, q in enumerate(quotes, 1):
            parts.append(f'  Quote {i}: "{q.quote}"')
            parts.append(f'    (Relevance: {q.explanation})')
    
    return "\n".join(parts)

# =============================================================================
# LLM helpers
# =============================================================================
def _llm_for_assessment():
    """LLM configured for analytical, consistent output."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
    )


def _profile_to_brief(profile: AISystemProfile) -> str:
    """Convert profile to a compact text brief for inclusion in prompts."""
    extra = ""
    if profile.additional_context:
        extra = f"\nAdditional context: {profile.additional_context}"
    return (
        f"AI System: {profile.system_name}\n"
        f"Purpose: {profile.purpose}\n"
        f"Business unit: {profile.business_unit}\n"
        f"Type: {profile.ai_type} | Third-party model: {profile.is_third_party_model}\n"
        f"Decisions made: {', '.join(profile.decisions_made)}\n"
        f"Affects individuals: {profile.affects_individuals}\n"
        f"Affected parties: {', '.join(profile.affected_parties)}\n"
        f"Deployment: {', '.join(profile.deployment_geographies)} | Sector: {profile.deployment_sector}\n"
        f"Training data: {', '.join(profile.training_data_sources)}\n"
        f"Processes personal data: {profile.processes_personal_data} | Sensitive data: {profile.processes_sensitive_data}\n"
        f"Existing governance:\n"
        f"  - AI policy: {profile.has_documented_policy}\n"
        f"  - Impact assessment: {profile.has_impact_assessment}\n"
        f"  - Human oversight: {profile.has_human_oversight}\n"
        f"  - Monitoring: {profile.has_monitoring}\n"
        f"  - Bias testing: {profile.has_bias_testing}"
        f"{extra}"
    )


# =============================================================================
# PHASE 1: EU AI Act Classification
# =============================================================================
PHASE_1_PROMPT = """You are an EU AI Act compliance specialist. Classify the AI system below into the correct EU AI Act risk tier.

# Reference: EU AI Act risk tiers
{eu_ai_act_context}

# AI System Profile
{profile_brief}

# Instructions
1. First check Article 5 prohibited practices. If the system engages in any prohibited practice, classify as 'unacceptable'.
2. If not prohibited, check Annex III high-risk categories. If the system falls into any Annex III area AND it doesn't qualify for the Article 6(3) exception, classify as 'high'.
3. If the system is a chatbot, generates synthetic content, does emotion recognition, or biometric categorization not covered by Article 5, it has limited risk transparency obligations.
4. Otherwise, classify as 'minimal' (or 'not_applicable' if there's no EU deployment and no EU-affecting outputs).
5. Note: 'profiling of natural persons' AUTO-TRIGGERS high-risk for any Annex III system.
6. Be specific in reasoning - cite the Annex III category number or Article 5 paragraph that applies."""


def phase_1_classify_eu_ai_act(profile: AISystemProfile) -> EUAIActClassification:
    print("Phase 1: Classifying EU AI Act risk tier...")
    eu_items = _retrieve_framework_items(
        f"EU AI Act risk classification {profile.deployment_sector} {' '.join(profile.decisions_made)}",
        n_results=10
    )
    eu_items = [i for i in eu_items if i["framework"] == "EU AI Act"]
    if len(eu_items) < 4:
        extra = _retrieve_framework_items("EU AI Act risk tiers Annex III", n_results=15)
        eu_items.extend([i for i in extra if i["framework"] == "EU AI Act"])
        seen = set()
        deduped = []
        for i in eu_items:
            if i["id"] not in seen:
                deduped.append(i)
                seen.add(i["id"])
        eu_items = deduped
    eu_context = "\n\n".join(
        f"[{item['id']}] {item['title']}\n{item['content'][:800]}"
        for item in eu_items[:8]
    )
    prompt = PHASE_1_PROMPT.format(
        eu_ai_act_context=eu_context,
        profile_brief=_profile_to_brief(profile),
    )
    llm = _llm_for_assessment().with_structured_output(EUAIActClassification)
    result = llm.invoke(prompt)
    print(f"   Classification: {result.risk_tier}")
    return result


# =============================================================================
# PHASE 2: Identify Relevant Controls
# =============================================================================
PHASE_2_PROMPT = """You are an AI governance specialist. Given an AI system profile and an EU AI Act classification, select the most relevant framework controls to assess.

# AI System Profile
{profile_brief}

# EU AI Act Classification
Risk tier: {risk_tier}
Reasoning: {classification_reasoning}

# Candidate framework items
{candidate_items}

# Instructions
Select 12-18 control IDs to assess in depth (keep this list focused). Prioritize controls that:
1. Are directly triggered by this system's risk profile
2. Cover the major themes: data governance, bias, human oversight, transparency, monitoring, third-party
3. Span all three frameworks (ISO 42001, NIST AI RMF, EU AI Act)
4. Match gaps already implied by the profile

Use the exact IDs as shown in the candidate list."""


def phase_2_select_relevant_controls(
    profile: AISystemProfile,
    classification: EUAIActClassification,
) -> RelevantControlsSelection:
    print("Phase 2: Selecting relevant framework controls...")
    query_terms = [
        profile.deployment_sector,
        profile.ai_type,
        " ".join(profile.decisions_made),
    ]
    if not profile.has_bias_testing:
        query_terms.append("bias fairness")
    if not profile.has_impact_assessment:
        query_terms.append("impact assessment")
    if not profile.has_documented_policy:
        query_terms.append("AI policy")
    if not profile.has_human_oversight:
        query_terms.append("human oversight")
    if profile.is_third_party_model:
        query_terms.append("third-party supplier")
    if profile.processes_personal_data:
        query_terms.append("personal data privacy")
    query = " ".join(query_terms)
    candidates = _retrieve_framework_items(query, n_results=30)
    candidate_text = "\n".join(
        f"- [{item['id']}] ({item['framework']}) {item['title']}"
        for item in candidates
    )
    prompt = PHASE_2_PROMPT.format(
        profile_brief=_profile_to_brief(profile),
        risk_tier=classification.risk_tier,
        classification_reasoning=classification.reasoning,
        candidate_items=candidate_text,
    )
    llm = _llm_for_assessment().with_structured_output(RelevantControlsSelection)
    result = llm.invoke(prompt)
    print(f"   Selected {len(result.relevant_control_ids)} controls for evaluation")
    return result


# =============================================================================
# PHASE 3: Per-Control Gap Evaluation
# =============================================================================
PHASE_3_PROMPT = """You are a senior AI governance auditor evaluating an AI system against a specific control. You assess BOTH user-claimed status AND attached evidence documents.

# AI System Profile
{profile_brief}

# Control being evaluated
ID: {control_id}
Framework: {control_framework}
Title: {control_title}
Full text:
{control_content}

# Evidence relevant to this control

The following quotes were extracted from the user's evidence documents and identified as specifically relevant to this control. They are verbatim quotes, not paraphrases.

{evidence_section}

Important: ONLY the quoted text above is verified evidence. Do not assume the documents contain content beyond what's quoted. If a quote is short or partial, work with that — don't extrapolate.

# Instructions

You must determine the status, severity, and reasoning for this control.

## Status determination - APPLY STRICTLY

If evidence was provided:
- 'met_with_evidence': Document substantiates the claim, addressing the core requirements of this control.
- 'evidence_partial': Document partially substantiates the claim. Names the gap explicitly. Example: "Policy exists but doesn't specify bias testing cadence."
- 'evidence_inadequate': Document exists but doesn't actually demonstrate compliance. Could be: wrong type of document, very stale, contradicts the claim, or is purely aspirational without operational substance.

If no evidence was provided AND user claimed this control exists (True in profile):
- 'met_claimed_unverified': Use this. The claim cannot be verified.

If user did not claim this control (False or absent in profile):
- 'not_met': The standard not-implemented status.

If the control truly doesn't apply to this AI system:
- 'not_applicable': Use sparingly. Most governance controls apply to most AI systems.

## Severity determination

Apply this rubric strictly:
* 'critical': Direct, currently-enforceable regulatory violation OR fundamental rights at active risk. Examples: EU AI Act Article 5 prohibition violation; high-risk system without ANY risk management as of Aug 2026; processing personal data without lawful basis.
* 'high': Clear gap with regulatory or rights implications but enforcement not yet active OR remediation feasible. Examples: missing bias testing for high-risk EU AI system before Aug 2026; no AI policy when one is needed; missing impact assessment for high-risk use case.
* 'medium': Material governance gap that supports good practice and audit defensibility, not legally mandated as critical. Examples: documentation present but incomplete; monitoring exists but lacks drift detection; oversight roles defined but training not formalized.
* 'low': Nice-to-have refinement; the basic intent is met but could be more robust.

CALIBRATION: A typical assessment of an early-stage governance system should show ~25% critical, ~40% high, ~25% medium, ~10% low. If you're labeling >50% critical, reconsider which gaps are TRULY currently-enforceable vs. serious-but-not-immediate.

NOTE: Severity interaction with status is nuanced — apply this rubric strictly:

* 'met_with_evidence' (document fully substantiates the claim): severity should be 'low' (residual risk only).

* 'met_claimed_unverified' (claim with no document): severity should be 'medium' (audit risk from unverified claim).

* 'evidence_partial' (document covers most but not all of the control): severity stays at the level it would have been at if evidence weren't provided, possibly one notch lower. The gap is real, just partially addressed.

* 'evidence_inadequate' (document exists but reveals active failure or doesn't substantiate the claim): severity should be HIGH or CRITICAL — same as 'not_met'. Evidence revealing active failures is NOT mitigation; it is documentation of a risk.

ESCALATION RULE — when evidence reveals failing metrics or admitted gaps:

If evidence shows specific failures (e.g., bias testing with FAILED disparate impact metrics, monitoring with breached thresholds, policy explicitly admitting unaddressed regulatory requirements), set status to 'evidence_inadequate' rather than 'evidence_partial'. The reasoning is that evidence revealing active failures is more probative than no evidence at all — the organization has documented evidence of non-compliance that they have not yet remediated.

Example: a bias testing document showing 'FAIL' for Disparate Impact (Age) at 0.78 (below 0.80 threshold) is NOT 'evidence_partial' for an EU bias control. It is 'evidence_inadequate' with severity 'high' or 'critical' — because the evidence affirmatively documents an active fairness failure that creates regulatory exposure under EU AI Act Article 10 and GDPR Article 22.

Conversely: a draft policy that explicitly states "DPIA has not been conducted" and "bias testing methodology does not yet exist" is 'evidence_inadequate' (not 'evidence_partial') for those specific controls, because the policy itself documents the absence of the controls being assessed.

## Read evidence proactively for what it admits

Documents often acknowledge gaps that ARE the findings you're looking for. Examples:
- A policy that says "bias testing methodology has not yet been documented" — this is itself evidence for bias-related controls being not_met.
- A test report that says "scope was limited to gender; age testing pending Q3" — this is evidence_partial for general bias controls.
- A policy that references "the Q3 remediation roadmap" without that roadmap being attached — flag this as a follow-up: the policy commits to remediation but the remediation document is not in evidence.

When you spot these patterns, your reasoning should explicitly call them out, even if the control isn't directly about that gap. Example phrasing: "The policy commits to a Q3 remediation roadmap to address these gaps; however, no roadmap document is included in evidence to verify that commitment is being executed."

## Reasoning - apply this precision standard

CITE PROFILE FACTS PRECISELY: Quote specific profile fields ("Profile states 'Bias testing: True' with attached methodology document").

CITE QUOTES IN REASONING: When evidence quotes are provided, your reasoning MUST quote the specific text. Format: "The policy states '...' which addresses the control's requirement for X." NEVER make claims about evidence content without quoting the supporting text. If you can't quote it, you can't claim it.

If evidence quotes do exist for this control: Your evidence_assessment field MUST include at least one direct quote from the provided evidence (in quotation marks), followed by your interpretation. Generic statements like "the policy covers governance" without quoting the policy text are forbidden.

CITE REGULATIONS WHEN CONFIDENT: Use specific provisions when known (GDPR Article 22, EU AI Act Article 9). Use general language when uncertain ("relevant GDPR provisions"). NEVER invent article numbers.

CITE EFFECTIVE DATES: For EU AI Act controls, note timing where relevant:
- Article 5 prohibitions: enforceable from 2 February 2025
- GPAI rules: applicable from 2 August 2025
- Most high-risk obligations: applicable from 2 August 2026
- Annex II products: applicable from 2 August 2027

## Evidence assessment field

If you set status to 'met_with_evidence', 'evidence_partial', or 'evidence_inadequate', you MUST populate evidence_assessment with 1-2 sentences specifically describing what the document does and doesn't cover relative to this control. Do not paraphrase the entire document. Focus on the gap or strength relevant to THIS control.

If status is 'met_claimed_unverified', 'not_met', or 'not_applicable', set evidence_assessment to None.

Always populate evidence_filename if a document was provided in the Evidence section above.

## Anti-patterns to avoid

- Don't accept evidence at face value because it exists. A 1-page draft policy doesn't substantiate a sophisticated AI governance claim.
- Don't penalize evidence for not being complete - if it covers the control's core requirements, that's met. Reserve 'evidence_partial' for actual gaps in coverage.
- Don't write evidence_assessment for status='not_met' (no evidence to assess).
- Don't make up details about the document. Only cite what you can see in the evidence text.
- AVOID REPETITIVE REASONING: When the same evidence document is being evaluated against multiple controls, focus your reasoning on what's UNIQUELY relevant to THIS specific control. Don't repeat the same observations about the document across different findings. If a policy is missing DPIA, mention that for impact-assessment-related controls; if it's missing bias methodology, mention that for bias-related controls. Each finding's reasoning should highlight what THIS specific control's intent reveals about the document's adequacy — not generic "the policy is a draft" observations."""

def phase_3_evaluate_controls(
    profile: AISystemProfile,
    selection: RelevantControlsSelection,
) -> list[GapFinding]:
    """Phase 3: Evaluate each selected control. One LLM call per control."""
    print(f"Phase 3: Evaluating {len(selection.relevant_control_ids)} controls...")
    if profile.evidence_attachments:
        print(f"   ({len(profile.evidence_attachments)} evidence documents available for matching)")
    
    control_items = _retrieve_by_ids(selection.relevant_control_ids)
    findings = []
    llm = _llm_for_assessment().with_structured_output(GapFinding)
    
    for i, item in enumerate(control_items, 1):
# Scan all evidence for content relevant to this control
        evidence_text, evidence_filename = _get_evidence_for_control(
            control_id=item["id"],
            control_framework=item["framework"],
            control_title=item["title"],
            control_content=item["content"],
            profile=profile,
        )
        
        if evidence_text:
            # Truncate very long evidence to keep prompts manageable
            truncated = evidence_text[:5000]
            if len(evidence_text) > 5000:
                truncated += f"\n\n[... document continues; {len(evidence_text)-5000} more chars truncated]"
            evidence_section = (
                f"FILENAME: {evidence_filename}\n"
                f"DOCUMENT CONTENT:\n{truncated}"
            )
            evidence_indicator = f"[evidence: {evidence_filename}]"
        else:
            evidence_section = "No evidence document was provided for this control."
            evidence_indicator = ""
        
        print(f"   [{i}/{len(control_items)}] {item['id']} {evidence_indicator}...", end=" ", flush=True)
        
        prompt = PHASE_3_PROMPT.format(
            profile_brief=_profile_to_brief(profile),
            control_id=item["id"],
            control_framework=item["framework"],
            control_title=item["title"],
            control_content=item["content"][:2000],
            evidence_section=evidence_section,
        )
        
        try:
            finding = llm.invoke(prompt)
            finding.control_id = item["id"]
            finding.framework = item["framework"]
            finding.control_title = item["title"]
            findings.append(finding)
            print(f"{finding.status} ({finding.severity})")
        except Exception as e:
            print(f"skipped ({str(e)[:60]})")
    
    print(f"   Produced {len(findings)} gap findings")
    return findings

# =============================================================================
# PHASE 4: Cross-Framework Synthesis
# =============================================================================
PHASE_4_PROMPT = """You are a senior AI governance consultant synthesizing assessment findings into root-cause themes for a partner-level deliverable.

# Findings
{findings_summary}

# What "good" looks like
You are NOT producing a checklist of clusters. You are producing partner-quality diagnostic statements that pass the "so what" test:
- A junior associate writes: "Multiple frameworks have bias-related gaps (ISO A.6.1.4, NIST MEASURE-2.11)."
- A senior consultant writes: "Bias risk is unmeasured by design: there is no testing methodology, no fairness metrics in the model lifecycle, and no monitoring for disparate impact in production. This is not a 'tighten testing' issue — it is a 'fairness was never operationalized' issue, which is why the gap appears across all three frameworks (ISO 42001 A.6.1.4, NIST AI RMF MEASURE-2.11)."

# Required structure for each theme
Each theme MUST contain:
1. A SHARP LABEL (3-7 words, diagnostic, not descriptive). Examples: "Foundational governance void", "Bias risk unmeasured by design", "Decision-stage transparency missing", "Operational data drift unmonitored". Avoid generic words like "absence" or "lack".
2. A DIAGNOSIS in 2-3 sentences. Name the meta-issue and what kind of problem it is. Use a "this is X, not Y" framing where it adds clarity.
3. CONTROL CITATIONS embedded as evidence, not appended as a list. Format: "(ISO 42001 A.6.1.4, NIST AI RMF MEASURE-2.11, EU AI Act ANNEX-III-5)". Cite 2-6 controls per theme.
4. (Optional but encouraged) A DEPENDENCY OBSERVATION when relevant: note if the theme is upstream of other gaps. Example: "Until policy scaffolding exists, downstream controls like X cannot be meaningfully addressed."

# Production constraints
- Identify 4-6 themes (not 3-7 — be more focused).
- Each theme should be ~3-5 sentences total. Tight, not bloated.
- Themes should be MUTUALLY DISTINCT. If two themes overlap, merge them or sharpen what makes each unique.
- Order themes by importance: regulatory exposure first, fundamental rights second, governance hygiene last.

# Anti-patterns to avoid
- Generic openings like "Absence of...", "Lack of...", "Insufficient..." — replace with diagnostic verbs ("Bias risk is unmeasured", "Governance scaffolding is absent")
- Long bullet lists of controls dominating the theme text
- Themes that are essentially "stuff is missing" — every theme should have a 'so what'
- Themes that just rephrase a single finding — themes must span multiple controls

Focus on themes where status is 'not_met' or 'partial'."""


def phase_4_synthesize_themes(findings: list[GapFinding]) -> CrossFrameworkSynthesis:
    print("Phase 4: Synthesizing cross-framework themes...")
    findings_text = "\n".join(
        f"- [{f.framework}] {f.control_id} ({f.control_title}): {f.status} / {f.severity} - {f.reasoning[:200]}"
        for f in findings
    )
    prompt = PHASE_4_PROMPT.format(findings_summary=findings_text)
    llm = _llm_for_assessment().with_structured_output(CrossFrameworkSynthesis)
    result = llm.invoke(prompt)
    print(f"   Identified {len(result.themes)} cross-framework themes")
    return result


# =============================================================================
# PHASE 5: Executive Summary
# =============================================================================
PHASE_5_PROMPT = """You are a senior AI governance consultant writing the executive summary section of a partner-quality assessment deliverable. The CEO and CRO will read this. They have 60 seconds. Make every sentence count.

# AI System
{profile_brief}

# EU AI Act Classification
{risk_tier}: {classification_reasoning}

# Findings count
{findings_summary}

# Cross-framework themes
{themes}

# What "good" looks like
The summary must be UNMISTAKABLY ABOUT THIS SPECIFIC SYSTEM. If you could swap the system name with another AI system and the summary still reads correctly, you have failed. Bad and good examples below:

GENERIC (FAILS): "The system is high-risk under the EU AI Act and lacks governance, exposing the organization to regulatory non-compliance and potential harm to individuals."

SPECIFIC (PASSES): "Loan AI is a high-risk EU AI Act Annex III(5) system in active EU production, making automated credit decisions for personal loans without the documented risk management or bias testing that the EU AI Act requires for high-risk systems by 2 August 2026. The organization has approximately {{months_remaining}} months to establish foundational governance or accept material regulatory exposure under EU AI Act Article 99 (penalties up to €15M or 3% of global turnover). The fact that approvals are fully automated while only declines receive human review additionally implicates GDPR Article 22 (automated individual decisions with legal effects)."

The PASSES example is concrete because it cites: the specific Annex III category, the specific decisions made, the specific date, the specific penalty article, and the specific operating-model risk.

# Required content for overall_maturity_summary
- 2-4 sentences (you may go to 4 if needed for specificity)
- Reference at least 2 specific facts from the profile (system name, sector, jurisdiction, specific decisions made, specific governance gaps)
- Reference at least 1 specific regulatory hook with article/date when confident (e.g., "EU AI Act Article 9 risk management, applicable from 2 August 2026", "GDPR Article 22 automated decision-making rights")
- State the regulatory timeline urgency where relevant (today's date is May 2026; key EU AI Act high-risk obligations apply from 2 August 2026 — that's roughly 3 months)
- Avoid filler phrases like "It is important to note that" or "Significant regulatory exposure"

# Required content for immediate_concerns (3-5 items)
Each concern should:
- Be specific to THIS system's operating context (not generic AI-governance-101 statements)
- Cite a regulation, control, or specific operational fact when possible
- Include the practical "what happens if this isn't addressed" consequence
- Be ranked: regulatory exposure with active enforcement first, then enforcement-by-date, then fundamental rights, then governance hygiene

GENERIC concerns (avoid): "Lack of bias testing creates risk of discrimination."
SPECIFIC concerns (use): "No bias testing on the historical loan portfolio means disparate impact across protected attributes (gender, age, ethnicity) goes undetected — a direct fundamental rights risk under EU AI Act Article 10 data quality requirements and an active GDPR Article 22(3) violation given fully automated approvals."

# Constraints
- Use specific numbers/dates/articles when confident; use general language ("relevant provisions") when not
- Do NOT invent article numbers or dates
- Do NOT use jargon for jargon's sake — but DO use precise regulatory language where it adds specificity
- The CEO/CRO are sophisticated readers — they can handle "GDPR Article 22" without explanation, but they need plain-English explanation of *why it matters*"""


def phase_5_executive_summary(
    profile: AISystemProfile,
    classification: EUAIActClassification,
    findings: list[GapFinding],
    synthesis: CrossFrameworkSynthesis,
) -> ExecutiveSummary:
    print("Phase 5: Drafting executive summary...")
    counts = {"met": 0, "partial": 0, "not_met": 0, "not_applicable": 0}
    for f in findings:
        counts[f.status] = counts.get(f.status, 0) + 1
    findings_summary = (
        f"Total: {len(findings)} | Met: {counts['met']} | Partial: {counts['partial']} | "
        f"Not met: {counts['not_met']} | Not applicable: {counts['not_applicable']}"
    )
    themes_text = "\n".join(f"- {t}" for t in synthesis.themes)
    prompt = PHASE_5_PROMPT.format(
        profile_brief=_profile_to_brief(profile),
        risk_tier=classification.risk_tier,
        classification_reasoning=classification.reasoning,
        findings_summary=findings_summary,
        themes=themes_text,
    )
    llm = _llm_for_assessment().with_structured_output(ExecutiveSummary)
    result = llm.invoke(prompt)
    print("   Summary drafted")
    return result


# =============================================================================
# Orchestration
# =============================================================================
def run_assessment(profile: AISystemProfile) -> AssessmentReport:
    """Run the full 5-phase assessment and return an AssessmentReport."""
    print(f"\n{'='*60}")
    print(f"Running assessment for: {profile.system_name}")
    print(f"{'='*60}\n")
    classification = phase_1_classify_eu_ai_act(profile)
    
    selection = phase_2_select_relevant_controls(profile, classification)
    
    findings = phase_3_evaluate_controls(profile, selection)
    
    synthesis = phase_4_synthesize_themes(findings)
    
    summary = phase_5_executive_summary(profile, classification, findings, synthesis)
    report = AssessmentReport(
        eu_ai_act_risk_tier=classification.risk_tier,
        eu_ai_act_reasoning=classification.reasoning,
        findings=findings,
        cross_framework_themes=synthesis.themes,
        overall_maturity_summary=summary.overall_maturity_summary,
        immediate_concerns=summary.immediate_concerns,
    )
    print(f"\n{'='*60}")
    print(f"Assessment complete")
    print(f"{'='*60}")
    return report