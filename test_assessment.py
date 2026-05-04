"""
Test the assessment agent on a hand-crafted profile.

Uses a fictional credit scoring AI - the same scenario we used for intake testing.
This avoids needing the intake agent to run first.
"""
from models import AISystemProfile
from assessment_agent import run_assessment


# Hand-crafted profile - bypasses the intake step for testing
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
    processes_sensitive_data=False,  # corrected: financial data is personal but not GDPR Art. 9 special category
    has_documented_policy=False,
    has_impact_assessment=False,
    has_human_oversight=True,
    has_monitoring=False,
    has_bias_testing=False,
    additional_context="Approvals fully automated, declines reviewed by human credit officer",
)


# Run the assessment
report = run_assessment(test_profile)


# Print the report nicely
print("\n" + "=" * 70)
print("ASSESSMENT REPORT")
print("=" * 70)

print(f"\n📋 EU AI Act Classification: {report.eu_ai_act_risk_tier.upper()}")
print(f"   Reasoning: {report.eu_ai_act_reasoning}")

print(f"\n📊 Overall Maturity Summary:")
print(f"   {report.overall_maturity_summary}")

print(f"\n⚠️  Immediate Concerns:")
for i, concern in enumerate(report.immediate_concerns, 1):
    print(f"   {i}. {concern}")

print(f"\n🔗 Cross-Framework Themes:")
for i, theme in enumerate(report.cross_framework_themes, 1):
    print(f"   {i}. {theme}")

print(f"\n📋 Findings Summary ({len(report.findings)} total):")
status_counts = {}
for f in report.findings:
    status_counts[f.status] = status_counts.get(f.status, 0) + 1
for status, count in status_counts.items():
    print(f"   {status}: {count}")

print(f"\n📋 Detailed Findings (top concerns first):")
# Sort by severity then status
severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
status_order = {"not_met": 0, "partial": 1, "met": 2, "not_applicable": 3}
sorted_findings = sorted(
    report.findings,
    key=lambda f: (severity_order.get(f.severity, 99), status_order.get(f.status, 99))
)

for f in sorted_findings[:10]:  # show top 10
    print(f"\n   [{f.framework}] {f.control_id}: {f.control_title}")
    print(f"   Status: {f.status} | Severity: {f.severity}")
    print(f"   Reasoning: {f.reasoning}")

if len(sorted_findings) > 10:
    print(f"\n   ... and {len(sorted_findings) - 10} more findings")

print("\n" + "=" * 70)