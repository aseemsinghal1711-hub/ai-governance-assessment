"""
Recommendation Agent - takes an AISystemProfile and AssessmentReport,
produces a phased RemediationPlan with prioritized actions.

Architecture: Single structured LLM call with the full assessment as context.
Phased structure (quick wins → foundation → maturity → optimization) forces
the agent to sequence work rather than list everything as equally urgent.
"""
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from models import (
    AISystemProfile,
    AssessmentReport,
    RemediationPlan,
)

load_dotenv()


# =============================================================================
# Recommendation prompt - the most demanding prompt in the system
# =============================================================================
RECOMMENDATION_PROMPT = """You are a senior AI governance consultant producing the remediation roadmap section of a partner-quality assessment deliverable. The CRO has approved the budget; you must now propose the *actual sequence of work* to close the gaps.

# AI System Profile
{profile_brief}

# Assessment Findings
EU AI Act Classification: {risk_tier}
Reasoning: {classification_reasoning}

Findings ({finding_count} total):
{findings_summary}

Cross-framework themes:
{themes}

Immediate concerns:
{immediate_concerns}

# Your job
Produce a RemediationPlan with FOUR sequenced phases. The phases are NOT four buckets to fill equally — they represent execution sequence. Earlier phases unblock later phases.

## Phase definitions

**quick_wins** (first 30 days): Low-effort actions with high signal value. They demonstrate executive commitment, build the team's credibility for the larger program, and produce visible artifacts. Examples: "Designate AI governance owner", "Inventory the AI system in a register", "Issue interim AI use policy". DO NOT put complex regulatory work here.

**foundation_phase** (months 1-3): The minimum viable governance baseline. These are the controls a regulator would consider table stakes for a high-risk system. Without these, the organization is exposed. Examples: "Conduct DPIA per GDPR Article 35", "Establish bias testing methodology", "Document AI policy and approve through governance committee". This is where regulatory baseline lives.

**maturity_phase** (months 3-9): Robust ongoing capabilities. Beyond meeting baseline, these establish the operating model — monitoring, periodic review, integrated risk management. Examples: "Deploy production monitoring with drift detection", "Establish quarterly bias re-testing cadence", "Integrate AI risk into enterprise risk register".

**optimization_phase** (months 9+): Leading practice. Excellence-level work that goes beyond compliance. Examples: "Establish red-team testing program", "Publish transparency report", "Pursue ISO 42001 certification".

## Sequencing logic — APPLY STRICTLY

1. If a finding is currently-enforceable regulatory exposure (e.g., GDPR violation now active), it goes in foundation_phase, NOT quick_wins. Quick wins are about momentum, not regulatory closure.

2. Group findings that share a common remediation. Example: missing bias testing + missing fairness metrics + missing disparate impact monitoring all close with ONE action ("Establish bias testing methodology") — don't write three separate actions for what is one workstream.

3. Earlier phases must unblock later phases. Don't put "monitor bias in production" in foundation if "establish bias testing methodology" hasn't happened yet. Sequence dependencies explicitly.

4. Budget realism: assume a small dedicated team (2-4 people) plus pulled-in subject matter experts. Do not propose 20 actions in foundation_phase. Aim for 4-7 actions per phase, each substantive.

## Required content per action

Each RemediationAction must contain:
- **title**: Action-oriented, starts with a verb. Examples: "Conduct DPIA", "Designate AI governance owner". NOT: "DPIA", "AI Policy", "Bias Testing".
- **description**: 2-3 sentences. WHAT to do, not WHY (the assessment already established why). Be specific about scope. Bad: "Address bias in the AI system." Good: "Engage Data Science team to perform disaggregated testing of Loan AI on historical decisions across gender, age, and ethnicity. Document methodology, metrics, and any disparate impact findings. Establish remediation plan for any disparate impact > 5%."
- **addresses_findings**: List of control IDs from the assessment that this action closes. Cite real IDs from the assessment, not invented ones. Multiple actions may address the same finding; one action may address multiple findings.
- **suggested_owner**: A role, not a person. Examples: "Chief Risk Officer", "AI Governance Lead", "Data Science Lead", "Legal & Privacy Counsel". Be specific to action — don't put everything on the CRO.
- **effort**: 'low' (days), 'medium' (weeks), 'high' (months of dedicated effort).
- **success_criteria**: Specific and measurable. Bad: "Bias is addressed." Good: "Disaggregated bias testing performed across 3 protected attributes with documented metrics; disparate impact findings within agreed tolerance OR remediation plan approved by governance committee."

## Executive summary

The executive_summary field is 3-4 sentences for senior leadership reading the roadmap. State:
- The total scope of the program (how many findings, how many phases)
- The critical-path items (what *must* happen by when)
- The expected end state if executed (e.g., "EU AI Act high-risk compliance baseline achieved by Q3 2026, full operating model in place by Q1 2027")
- The key dependency on leadership (e.g., "Requires CRO sponsorship and dedicated 0.5 FTE governance lead")

## Anti-patterns to avoid

- Don't write a single action that says "Implement governance program" — break it down to specific work
- Don't propose actions that aren't supported by findings in the assessment
- Don't put currently-enforceable regulatory work in quick_wins (it's foundation phase)
- Don't propose 15+ actions in any single phase (unrealistic)
- Don't write descriptions that re-explain why the gap exists (assessment already did this)
- Don't use generic owners like "the team" — name specific roles"""


def _profile_to_brief(profile: AISystemProfile) -> str:
    """Compact profile representation for inclusion in prompt."""
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


def _findings_to_summary(report: AssessmentReport) -> str:
    """Compact findings list for the prompt."""
    return "\n".join(
        f"- [{f.framework}] {f.control_id} ({f.control_title}): {f.status}/{f.severity}"
        for f in report.findings
    )


def generate_recommendations(
    profile: AISystemProfile,
    report: AssessmentReport,
) -> RemediationPlan:
    """Generate a phased remediation plan from profile + assessment."""
    print("\n" + "=" * 60)
    print("Generating remediation recommendations...")
    print("=" * 60)
    
    prompt = RECOMMENDATION_PROMPT.format(
        profile_brief=_profile_to_brief(profile),
        risk_tier=report.eu_ai_act_risk_tier,
        classification_reasoning=report.eu_ai_act_reasoning,
        finding_count=len(report.findings),
        findings_summary=_findings_to_summary(report),
        themes="\n".join(f"- {t}" for t in report.cross_framework_themes),
        immediate_concerns="\n".join(f"- {c}" for c in report.immediate_concerns),
    )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,  # slightly higher than assessment for varied recommendations
    ).with_structured_output(RemediationPlan)
    
    print("Calling LLM (this may take 30-60 seconds for a complex plan)...")
    plan = llm.invoke(prompt)
    
    total_actions = (
        len(plan.quick_wins) + len(plan.foundation_phase) +
        len(plan.maturity_phase) + len(plan.optimization_phase)
    )
    print(f"Plan generated: {total_actions} total actions across 4 phases")
    print(f"  Quick wins: {len(plan.quick_wins)}")
    print(f"  Foundation: {len(plan.foundation_phase)}")
    print(f"  Maturity: {len(plan.maturity_phase)}")
    print(f"  Optimization: {len(plan.optimization_phase)}")
    
    return plan