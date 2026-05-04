"""Quick sanity test that the Pydantic models work."""
from models import (
    AISystemProfile, AssessmentReport, GapFinding, 
    RemediationPlan, RemediationAction
)

# Test 1: Create a sample profile
sample_profile = AISystemProfile(
    system_name="ResumeRanker v2",
    purpose="Automatically score and rank job applications for the global recruiting team",
    business_unit="People & Talent",
    ai_type="ML classification with NLP",
    is_third_party_model=False,
    decisions_made=[
        "Assigns a fit score (0-100) to each application",
        "Filters applications below threshold from recruiter view"
    ],
    affects_individuals=True,
    affected_parties=["job applicants", "recruiters"],
    deployment_geographies=["EU", "UK", "US"],
    deployment_sector="HR / Recruiting",
    training_data_sources=["historical hiring decisions (last 5 years)", "internal resume corpus"],
    processes_personal_data=True,
    processes_sensitive_data=False,
    has_documented_policy=False,
    has_impact_assessment=False,
    has_human_oversight=True,
    has_monitoring=False,
    has_bias_testing=False,
    additional_context="System launched 18 months ago, used by 30 recruiters globally"
)

print("✅ AISystemProfile created successfully")
print(f"   System: {sample_profile.system_name}")
print(f"   Risk indicators: EU deployment={('EU' in sample_profile.deployment_geographies)}, "
      f"affects individuals={sample_profile.affects_individuals}, "
      f"HR sector={sample_profile.deployment_sector}")
print()


# Test 2: Create a sample assessment
sample_finding = GapFinding(
    control_id="A.6.1.4",
    framework="ISO 42001",
    control_title="Addressing bias in data",
    status="not_met",
    severity="high",
    reasoning="No bias testing has been performed. System uses historical hiring "
              "decisions which may encode existing biases."
)

sample_assessment = AssessmentReport(
    eu_ai_act_risk_tier="high",
    eu_ai_act_reasoning="System falls under Annex III(4) - Employment, workers management. "
                        "Used for filtering and ranking job applicants, materially "
                        "influencing recruitment decisions.",
    findings=[sample_finding],
    cross_framework_themes=[
        "Bias testing absent across all three frameworks (ISO A.6.1.4, NIST MEASURE-2.11)"
    ],
    overall_maturity_summary="Early stage. Human oversight exists but lacks the "
                             "documented governance, bias testing, and impact assessment "
                             "required for a high-risk EU AI Act system.",
    immediate_concerns=[
        "EU AI Act high-risk classification triggers obligations from August 2026",
        "No bias testing creates potential discrimination liability"
    ]
)

print("✅ AssessmentReport created successfully")
print(f"   EU AI Act tier: {sample_assessment.eu_ai_act_risk_tier}")
print(f"   Findings: {len(sample_assessment.findings)}")
print()


# Test 3: Create a sample remediation
sample_action = RemediationAction(
    title="Conduct fairness audit on historical hiring decisions",
    description="Engage data science team to audit the training data for demographic "
                "imbalances and the model for disparate impact across protected attributes.",
    addresses_findings=["A.6.1.4", "MEASURE-2.11"],
    suggested_owner="Data Science Lead",
    effort="medium",
    success_criteria="Audit report delivered with quantitative bias metrics across "
                     "gender, age, and ethnicity. Mitigation plan documented for any "
                     "disparate impact > 5%."
)

sample_plan = RemediationPlan(
    quick_wins=[],
    foundation_phase=[sample_action],
    maturity_phase=[],
    optimization_phase=[],
    executive_summary="ResumeRanker v2 is high-risk under the EU AI Act. We recommend "
                      "completing a bias audit, formal AI impact assessment, and AI policy "
                      "documentation within 90 days to address regulatory exposure ahead of "
                      "August 2026 enforcement."
)

print("✅ RemediationPlan created successfully")
print(f"   Foundation phase actions: {len(sample_plan.foundation_phase)}")
print()

print("🎉 All Pydantic models work correctly. Ready for Stage 5.2.")