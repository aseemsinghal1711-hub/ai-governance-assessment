"""Quick test of the relevance scanner in isolation."""
from models import AISystemProfile, EvidenceAttachment
from document_processor import ingest_document
from assessment_agent import _scan_evidence_for_relevance, _format_evidence_for_evaluation


# Build a minimal profile with one evidence document
policy_doc = ingest_document("medtech_ai_policy.txt", claimed_purpose="AI Policy")

profile = AISystemProfile(
    system_name="MedTriage AI v4.2",
    purpose="Clinical decision support for ED triage",
    business_unit="Clinical Operations",
    ai_type="ML classification",
    is_third_party_model=True,
    decisions_made=["Triage prioritization"],
    affects_individuals=True,
    affected_parties=["Patients"],
    deployment_geographies=["EU"],
    deployment_sector="Healthcare",
    training_data_sources=["ED records"],
    processes_personal_data=True,
    processes_sensitive_data=True,
    has_documented_policy=True,
    has_impact_assessment=True,
    has_human_oversight=True,
    has_monitoring=True,
    has_bias_testing=True,
)
profile.evidence_attachments = [EvidenceAttachment(
    field_name="has_documented_policy",
    file_path="medtech_ai_policy.txt",
    filename=policy_doc.filename,
    file_type=policy_doc.file_type,
    claimed_purpose="AI Policy",
    extracted_text=policy_doc.extracted_text,
    page_count=policy_doc.page_count,
)]


# Test 1: Control where the policy IS relevant
print("=" * 70)
print("Test 1: Bias testing control vs AI policy")
print("=" * 70)
print("(Policy mentions bias testing — scanner should find it)")
print()
results = _scan_evidence_for_relevance(
    profile=profile,
    control_id="MEASURE-2.11",
    control_framework="NIST AI RMF",
    control_title="Fairness and bias testing",
    control_content="The AI system shall be evaluated for fairness and bias across protected attributes including but not limited to gender, race, age, and disability. Testing methodology shall be documented and results regularly reviewed."
)
print(f"Documents flagged as relevant: {len(results)}")
print(_format_evidence_for_evaluation(results))


# Test 2: Control where the policy is NOT specifically relevant
print("\n" + "=" * 70)
print("Test 2: Computational performance control vs AI policy")
print("=" * 70)
print("(Policy doesn't discuss compute/performance — scanner should reject)")
print()
results = _scan_evidence_for_relevance(
    profile=profile,
    control_id="MEASURE-2.6",
    control_framework="NIST AI RMF",
    control_title="Computational performance and capacity planning",
    control_content="The computational performance and capacity of the AI system shall be measured. Hardware capacity, latency under load, and computational cost shall be tracked."
)
print(f"Documents flagged as relevant: {len(results)}")
print(_format_evidence_for_evaluation(results))


# Test 3: Borderline - third-party AI control
print("\n" + "=" * 70)
print("Test 3: Third-party AI control vs AI policy")
print("=" * 70)
print("(Policy DOES discuss third-party — scanner should find Section 5)")
print()
results = _scan_evidence_for_relevance(
    profile=profile,
    control_id="MANAGE-3.1",
    control_framework="NIST AI RMF",
    control_title="Third-party AI risk management",
    control_content="AI systems may depend on external resources and associated processes, including third-party data, software or hardware systems and personnel. Risks from these dependencies shall be identified and managed."
)
print(f"Documents flagged as relevant: {len(results)}")
print(_format_evidence_for_evaluation(results))