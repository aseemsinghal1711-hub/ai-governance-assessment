"""
Test the recommendation agent.

Strategy: Run a fresh assessment to get a real assessment report, then feed
that report (along with the profile) into the recommendation agent.

This tests the integration point — that real assessment output works as
recommendation input.
"""
from models import AISystemProfile
from assessment_agent import run_assessment
from recommendation_agent import generate_recommendations


# Same Loan AI profile we've been using
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


print("Step 1: Running assessment to get a real AssessmentReport...")
report = run_assessment(test_profile)

print("\n\nStep 2: Generating recommendations from that assessment...")
plan = generate_recommendations(test_profile, report)


# Pretty print the plan
print("\n" + "=" * 70)
print("REMEDIATION PLAN")
print("=" * 70)

print(f"\n📋 Executive Summary:")
print(f"   {plan.executive_summary}")

def print_phase(phase_name, actions):
    if not actions:
        print(f"\n📍 {phase_name}: (none)")
        return
    print(f"\n📍 {phase_name} ({len(actions)} actions):")
    for i, action in enumerate(actions, 1):
        print(f"\n   [{i}] {action.title}")
        print(f"       Owner: {action.suggested_owner} | Effort: {action.effort}")
        print(f"       Addresses: {', '.join(action.addresses_findings)}")
        print(f"       Description: {action.description}")
        print(f"       Success: {action.success_criteria}")

print_phase("QUICK WINS (first 30 days)", plan.quick_wins)
print_phase("FOUNDATION PHASE (months 1-3)", plan.foundation_phase)
print_phase("MATURITY PHASE (months 3-9)", plan.maturity_phase)
print_phase("OPTIMIZATION PHASE (months 9+)", plan.optimization_phase)

print("\n" + "=" * 70)