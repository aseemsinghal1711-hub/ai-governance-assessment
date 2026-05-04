"""
Test the evidence-aware Assessment Agent.

Profile setup:
- Loan AI in EU (same as before)
- has_documented_policy=True with sample_ai_policy.txt attached
- has_bias_testing=True with sample_bias_results.xlsx attached
- All other governance False (no claims, no evidence)

Expected: agent produces findings with new statuses:
- Controls related to AI policy → met_with_evidence or evidence_partial
- Controls related to bias testing → met_with_evidence or evidence_partial
- Other governance controls → not_met (unchanged)
"""
from models import AISystemProfile, EvidenceAttachment
from document_processor import ingest_document
from assessment_agent import run_assessment


# Step 1: Build the profile (same Loan AI as before)
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
    has_documented_policy=True,    # NEW: claimed True with evidence
    has_impact_assessment=False,
    has_human_oversight=True,
    has_monitoring=False,
    has_bias_testing=True,          # NEW: claimed True with evidence
    additional_context="Approvals fully automated, declines reviewed by human credit officer",
)


# Step 2: Attach evidence documents
print("Attaching evidence documents...")

# Ingest the AI policy
policy_doc = ingest_document(
    "sample_ai_policy.txt",
    claimed_purpose="AI use policy"
)
policy_evidence = EvidenceAttachment(
    field_name="has_documented_policy",
    file_path="sample_ai_policy.txt",
    filename=policy_doc.filename,
    file_type=policy_doc.file_type,
    claimed_purpose="AI use policy",
    extracted_text=policy_doc.extracted_text,
    page_count=policy_doc.page_count,
    extraction_warnings=policy_doc.extraction_warnings,
)

# Ingest the bias testing results
bias_doc = ingest_document(
    "sample_bias_results.xlsx",
    claimed_purpose="Bias testing results"
)
bias_evidence = EvidenceAttachment(
    field_name="has_bias_testing",
    file_path="sample_bias_results.xlsx",
    filename=bias_doc.filename,
    file_type=bias_doc.file_type,
    claimed_purpose="Bias testing results",
    extracted_text=bias_doc.extracted_text,
    page_count=bias_doc.page_count,
    extraction_warnings=bias_doc.extraction_warnings,
)

test_profile.evidence_attachments = [policy_evidence, bias_evidence]

print(f"Profile prepared with {len(test_profile.evidence_attachments)} evidence documents:")
for e in test_profile.evidence_attachments:
    print(f"  - {e.field_name}: {e.filename} ({len(e.extracted_text)} chars)")


# Step 3: Run the assessment
report = run_assessment(test_profile)


# Step 4: Print the findings, highlighting evidence-aware ones
print("\n" + "=" * 70)
print("ASSESSMENT REPORT")
print("=" * 70)

print(f"\nEU AI Act Classification: {report.eu_ai_act_risk_tier.upper()}")
print(f"Reasoning: {report.eu_ai_act_reasoning}")

# Count by status to see the impact of evidence
status_counts = {}
for f in report.findings:
    status_counts[f.status] = status_counts.get(f.status, 0) + 1

print(f"\nStatus distribution:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")


# Show findings that involved evidence (the interesting ones)
print(f"\n--- Findings WITH EVIDENCE (the new capability) ---")
evidence_findings = [
    f for f in report.findings
    if f.status in ("met_with_evidence", "evidence_partial", "evidence_inadequate", "met_claimed_unverified")
]
for f in evidence_findings:
    print(f"\n[{f.framework}] {f.control_id}: {f.control_title}")
    print(f"  Status: {f.status} | Severity: {f.severity}")
    if f.evidence_filename:
        print(f"  Evidence: {f.evidence_filename}")
    if f.evidence_assessment:
        print(f"  Evidence assessment: {f.evidence_assessment}")
    print(f"  Reasoning: {f.reasoning}")


# Show a few non-evidence findings for comparison
print(f"\n--- Sample of OTHER findings (no evidence involved) ---")
other_findings = [
    f for f in report.findings
    if f.status not in ("met_with_evidence", "evidence_partial", "evidence_inadequate", "met_claimed_unverified")
][:3]
for f in other_findings:
    print(f"\n[{f.framework}] {f.control_id}: {f.control_title}")
    print(f"  Status: {f.status} | Severity: {f.severity}")
    print(f"  Reasoning: {f.reasoning[:200]}...")


print(f"\n--- Cross-framework themes ---")
for i, theme in enumerate(report.cross_framework_themes, 1):
    print(f"{i}. {theme}")

print(f"\n--- Executive summary ---")
print(report.overall_maturity_summary)