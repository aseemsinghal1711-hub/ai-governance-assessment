"""
Test the full multi-agent pipeline end-to-end.

This is the integration test - it runs intake (via hand-coded profile),
assessment, and recommendations all in one shot.
"""
from models import AISystemProfile
from full_assessment import run_full_pipeline, save_result


# The same Loan AI profile we've been using
test_profile = AISystemProfile(
    system_name="Loan AI",
    purpose="Decides whether to approve personal loans",
    business_unit="Fintech retail lending",
    ai_type="ML classification model",
    is_third_party_model=False,
    decisions_made=["Loan approval", "Loan denial"],
    affects_individuals=True,
    affected_parties=["Individuals applying for personal loans"],
    deployment_geographies=["EU"],
    deployment_sector="Financial services / consumer lending",
    training_data_sources=["Historical loan portfolio - last 7 years"],
    processes_personal_data=True,
    processes_sensitive_data=False,
    has_documented_policy=False,
    has_impact_assessment=False,
    has_human_oversight=True,
    has_monitoring=False,
    has_bias_testing=False,
    additional_context="Approvals fully automated, declines reviewed by human credit officer",
)


# Run the full pipeline
result = run_full_pipeline(test_profile)


# Show a summary of the bundled result
print("\n" + "=" * 70)
print("BUNDLED RESULT SUMMARY")
print("=" * 70)
print(f"\nGenerated at: {result.generated_at}")
print(f"\n📋 System: {result.profile.system_name}")
print(f"   Sector: {result.profile.deployment_sector}")
print(f"   Geography: {', '.join(result.profile.deployment_geographies)}")

print(f"\n📊 Assessment:")
print(f"   EU AI Act tier: {result.report.eu_ai_act_risk_tier}")
print(f"   Findings: {len(result.report.findings)}")
print(f"   Themes: {len(result.report.cross_framework_themes)}")

print(f"\n📋 Plan:")
print(f"   Quick wins: {len(result.plan.quick_wins)}")
print(f"   Foundation: {len(result.plan.foundation_phase)}")
print(f"   Maturity: {len(result.plan.maturity_phase)}")
print(f"   Optimization: {len(result.plan.optimization_phase)}")

# Save the result for later viewing
save_result(result, "loan_ai_assessment.json")
print("\nYou can now view loan_ai_assessment.json to see the full result.")