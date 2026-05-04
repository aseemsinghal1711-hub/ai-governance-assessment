"""
Test the evidence-aware Assessment Agent against a MATURE system.

This is a stress test: profile claims most controls exist AND provides
real evidence. Tests whether the agent:
- Properly recognizes met_with_evidence when warranted
- Stays critical of subtle gaps (the policy mentions EU AI Act prep is in progress)
- Distinguishes between "good evidence" and "complete evidence"
- Handles a different sector (healthcare vs financial services)
"""
from models import AISystemProfile, EvidenceAttachment
from document_processor import ingest_document
from assessment_agent import run_assessment


# Profile: a relatively mature MedTriage AI
test_profile = AISystemProfile(
    system_name="MedTriage AI v4.2",
    purpose="Clinical decision support for emergency room triage prioritization",
    business_unit="Clinical Operations",
    ai_type="ML classification with NLP for symptom processing",
    is_third_party_model=True,  # Different from Loan AI
    decisions_made=[
        "Recommends triage priority level (ESI 1-5)",
        "Flags high-risk symptom patterns for nurse review",
    ],
    affects_individuals=True,
    affected_parties=["Patients arriving at emergency department", "Triage nurses"],
    deployment_geographies=["EU", "UK"],
    deployment_sector="Healthcare / Emergency Medicine",
    training_data_sources=[
        "De-identified ED triage records from 47 partner hospitals (2018-2024)",
        "Public emergency medicine datasets",
    ],
    processes_personal_data=True,
    processes_sensitive_data=True,  # Health data is sensitive per GDPR Art. 9
    has_documented_policy=True,
    has_impact_assessment=True,
    has_human_oversight=True,
    has_monitoring=True,
    has_bias_testing=True,
    additional_context=(
        "AI provides recommendations only; licensed nurses make final triage decisions. "
        "47 EU/UK hospitals deployed. Vendor-supplied model with quarterly retraining. "
        "Q1 2026 bias test revealed marginal Equal Opportunity for one ethnicity, "
        "with active remediation underway."
    ),
)


# Attach evidence documents
print("Attaching evidence documents...")

evidence_files = [
    ("medtech_ai_policy.txt", "has_documented_policy", "AI Governance Policy v2.1"),
    ("medtech_impact_assessment.txt", "has_impact_assessment", "AI Impact Assessment"),
    ("medtech_bias_methodology.txt", "has_bias_testing", "Bias Testing Methodology v3.0"),
    ("medtech_bias_results_q1_2026.xlsx", "has_bias_testing", "Q1 2026 Bias Test Results"),
]

for filepath, field_name, purpose in evidence_files:
    doc = ingest_document(filepath, claimed_purpose=purpose)
    test_profile.evidence_attachments.append(EvidenceAttachment(
        field_name=field_name,
        file_path=filepath,
        filename=doc.filename,
        file_type=doc.file_type,
        claimed_purpose=purpose,
        extracted_text=doc.extracted_text,
        page_count=doc.page_count,
        extraction_warnings=doc.extraction_warnings,
    ))

print(f"Profile prepared with {len(test_profile.evidence_attachments)} evidence documents:")
for e in test_profile.evidence_attachments:
    print(f"  - {e.field_name}: {e.filename} ({len(e.extracted_text)} chars)")


# Run the assessment
report = run_assessment(test_profile)


# Show what we got
print("\n" + "=" * 70)
print("ASSESSMENT REPORT - MedTriage AI (mature scenario)")
print("=" * 70)

print(f"\nEU AI Act Classification: {report.eu_ai_act_risk_tier.upper()}")
print(f"Reasoning: {report.eu_ai_act_reasoning}")

# Status distribution
status_counts = {}
severity_counts = {}
for f in report.findings:
    status_counts[f.status] = status_counts.get(f.status, 0) + 1
    severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

print(f"\nStatus distribution:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

print(f"\nSeverity distribution:")
for severity, count in sorted(severity_counts.items()):
    print(f"  {severity}: {count}")


# Findings WITH evidence (the interesting capability)
print(f"\n--- Findings WITH EVIDENCE ---")
evidence_findings = [
    f for f in report.findings
    if f.status in ("met_with_evidence", "evidence_partial",
                    "evidence_inadequate", "met_claimed_unverified")
]
for f in evidence_findings:
    print(f"\n[{f.framework}] {f.control_id}: {f.control_title}")
    print(f"  Status: {f.status} | Severity: {f.severity}")
    if f.evidence_filename:
        print(f"  Evidence: {f.evidence_filename}")
    if f.evidence_assessment:
        print(f"  Evidence assessment: {f.evidence_assessment}")
    print(f"  Reasoning: {f.reasoning[:400]}...")


print(f"\n--- Cross-framework themes ---")
for i, theme in enumerate(report.cross_framework_themes, 1):
    print(f"{i}. {theme}")

print(f"\n--- Executive summary ---")
print(report.overall_maturity_summary)

print(f"\n--- Immediate concerns ---")
for i, c in enumerate(report.immediate_concerns, 1):
    print(f"{i}. {c}")