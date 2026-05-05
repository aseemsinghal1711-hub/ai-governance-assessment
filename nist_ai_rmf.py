"""
NIST AI RMF Playbook - parsed from the official NIST CSV.
The CSV is in 'wide' format: columns are subcategory IDs, rows are properties.
"""
import csv
import os
from collections import defaultdict

CSV_PATH = os.path.join(os.path.dirname(__file__), "nist_playbook.csv")

# Manually curated short titles for NIST AI RMF subcategories.
# Falls back to first 120 chars of section_about if a control isn't here.
NIST_TITLES = {
    # GOVERN function
    "GOVERN-1.1": "Legal and Regulatory Requirements for AI Systems",
    "GOVERN-1.2": "AI Risk Management Policies and Organizational Accountability Structures",
    "GOVERN-1.3": "AI Risk Measurement, Prioritization, and Resource Allocation",
    "GOVERN-1.4": "AI Documentation and Transparency Policies and Procedures",
    "GOVERN-1.5": "Continuous Monitoring, Incident Response, and Appeal Processes",
    "GOVERN-1.6": "AI System Inventory and Asset Management",
    "GOVERN-1.7": "Policies for Systematic AI System Decommissioning",
    "GOVERN-2.1": "Independent AI Risk Management Responsibilities and Reporting",
    "GOVERN-2.2": "AI Risk Management Training and Awareness Integration",
    "GOVERN-2.3": "Senior Leadership Accountability and AI Risk Oversight",
    "GOVERN-3.1": "Multidisciplinary Team Composition and Diversity",
    "GOVERN-3.2": "Multi-disciplinary Engagement and AI Governance Roles",
    "GOVERN-4.1": "Organizational Risk Culture and Independent Challenge Mechanisms",
    "GOVERN-4.2": "AI Impact Assessments for Risk Management Oversight",
    "GOVERN-4.3": "AI System Testing, Incident Tracking, and Information Sharing",
    "GOVERN-5.1": "Participatory Stakeholder Engagement for AI System Fitness",
    "GOVERN-5.2": "Risk-Based Resource Allocation and Deployment Decisions",
    "GOVERN-6.1": "Third-Party AI Governance and Risk Management",
    "GOVERN-6.2": "Third-Party AI Redundancy and Contingency Procedures",
    
    # MAP function
    "MAP-1.1": "Context Mapping for Intended Use and Potential Impacts",
    "MAP-1.2": "Multidisciplinary Team Composition and Critical Inquiry",
    "MAP-1.3": "Business Purpose and Societal Value Alignment",
    "MAP-1.4": "AI System Context and Business Use Documentation",
    "MAP-1.5": "Organizational AI Risk Tolerance and Acceptance Criteria",
    "MAP-1.6": "Stakeholder Requirements and Societal Impact Integration",
    "MAP-2.1": "Definition of AI System Tasks and Intended Benefits",
    "MAP-2.2": "AI Lifecycle Interdependencies and Potential Impacts",
    "MAP-2.3": "Socio-Technical Testing and Evaluation Protocols",
    "MAP-3.1": "System Purpose Documentation for Impact Assessment",
    "MAP-3.2": "Stakeholder Engagement for Anticipating Negative Impacts",
    "MAP-3.3": "Narrow Application Scope for Effective Risk Management",
    "MAP-3.4": "Human-AI Configurations and Domain Expert Roles",
    "MAP-3.5": "Human Oversight Roles and Governance Responsibilities",
    "MAP-4.1": "Third-Party AI Technology and Personnel Risk Mapping",
    "MAP-4.2": "Third-Party and Open-Source Technology Risk Evaluation",
    "MAP-5.1": "AI Impact Likelihood Evaluation and Deployment Decisions",
    "MAP-5.2": "Anticipated Benefits and Costs of AI System Deployment",
    
    # MEASURE function
    "MEASURE-1.1": "AI Risk Measurement Approaches and Metric Selection",
    "MEASURE-1.2": "Appropriateness of AI Metrics and Effectiveness Controls",
    "MEASURE-1.3": "Internal Experts and Independent Assessors for AI Measurement",
    "MEASURE-2.1": "Test Sets and Performance Evaluation Methodologies",
    "MEASURE-2.2": "AI System Trustworthy Characteristics Evaluation",
    "MEASURE-2.3": "AI System Performance and Validity Demonstration",
    "MEASURE-2.4": "Deployment Performance Monitoring and Drift Detection",
    "MEASURE-2.5": "AI System Reliability, Robustness, and Validity Assessment",
    "MEASURE-2.6": "AI System Safety Risk and Failure Mode Documentation",
    "MEASURE-2.7": "AI System Security and Resilience Evaluation",
    "MEASURE-2.8": "AI System Transparency and Accountability Examination",
    "MEASURE-2.9": "AI Model Explainability and Interpretability Documentation",
    "MEASURE-2.10": "Privacy Risk Assessment of AI System Outputs",
    "MEASURE-2.11": "Fairness and Bias Evaluation Across Three Bias Categories",
    "MEASURE-2.12": "Environmental Impact and Sustainability of AI Systems",
    "MEASURE-2.13": "Effectiveness Demonstration Through Independent Verification",
    "MEASURE-3.1": "Risk Tracking Mechanisms and Identified Risk Approaches",
    "MEASURE-3.2": "Risk Tracking for Difficult-to-Assess AI Risks",
    "MEASURE-3.3": "Feedback Processes for End Users and Affected Communities",
    "MEASURE-4.1": "Measurement Approach Effectiveness and Context Validity",
    "MEASURE-4.2": "Trustworthiness Measurement Across the AI System Lifecycle",
    "MEASURE-4.3": "Performance Measurement and Improvement Documentation",
    
    # MANAGE function
    "MANAGE-1.1": "AI System Suitability and Risk-Benefit Tradeoff Assessment",
    "MANAGE-1.2": "Organizational AI Risk Tolerance and Resource Prioritization",
    "MANAGE-1.3": "Risk Response Planning Based on Established Tolerances",
    "MANAGE-1.4": "Residual Risk Acceptance, Transfer, and Transparent Monitoring",
    "MANAGE-2.1": "Risk Response Alternatives and Trustworthiness Tradeoffs",
    "MANAGE-2.2": "Post-Deployment AI System Performance Monitoring",
    "MANAGE-2.3": "Treatment Procedures for Unidentified AI Risks",
    "MANAGE-2.4": "AI System Deactivation and Decommissioning Protocols",
    "MANAGE-3.1": "Risk Management of Third-Party AI Resources",
    "MANAGE-3.2": "Risk Management for Pre-Trained Models and Transfer Learning",
    "MANAGE-4.1": "Continuous AI Monitoring and External Feedback Mechanisms",
    "MANAGE-4.2": "Continuous Monitoring, Incident Analysis, and Improvement",
    "MANAGE-4.3": "AI Error Identification and Remediation Documentation",
}


def function_from_id(subcat_id):
    if subcat_id.startswith("GOVERN"):
        return "GOVERN"
    if subcat_id.startswith("MAP"):
        return "MAP"
    if subcat_id.startswith("MEASURE"):
        return "MEASURE"
    if subcat_id.startswith("MANAGE"):
        return "MANAGE"
    return "UNKNOWN"


def category_from_id(subcat_id):
    parts = subcat_id.replace("-", " ").split()
    if len(parts) >= 2 and "." in parts[1]:
        cat_num = parts[1].split(".")[0]
        return f"{parts[0]} {cat_num}"
    return parts[0] if parts else "UNKNOWN"


def load_nist_ai_rmf():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"NIST playbook CSV not found at {CSV_PATH}")
    
    subcategories = defaultdict(lambda: {"section_about": "", "actions": []})
    
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        raise ValueError("CSV file is empty")
    
    header = rows[0]
    subcat_ids = [col.strip() for col in header[1:]]
    
    for row in rows[1:]:
        if not row:
            continue
        property_name = row[0].strip().lower()
        values = row[1:]
        
        for i, subcat_id in enumerate(subcat_ids):
            if not subcat_id:
                continue
            value = values[i].strip() if i < len(values) else ""
            if not value:
                continue
            
            if property_name == "section_about":
                subcategories[subcat_id]["section_about"] = value
            elif property_name.startswith("action") or property_name.startswith("suggested"):
                subcategories[subcat_id]["actions"].append(value)
            else:
                subcategories[subcat_id]["actions"].append(f"[{property_name}] {value}")
    
    controls = []
    for subcat_id, data in subcategories.items():
        clean_id = subcat_id.replace(" ", "-")
        about = data["section_about"]
        actions_text = " | ".join(data["actions"]) if data["actions"] else ""
        
        title = NIST_TITLES.get(clean_id, about[:120] if about else clean_id)
        requirement = about if about else f"NIST AI RMF subcategory {clean_id}"
        
        controls.append({
            "id": clean_id,
            "title": title,
            "framework": "NIST AI RMF",
            "category": category_from_id(subcat_id),
            "requirement": requirement,
            "evidence_examples": actions_text[:3000],
            "common_gaps": "",
        })
    
    return controls


NIST_AI_RMF_CONTROLS = load_nist_ai_rmf()


if __name__ == "__main__":
    print(f"Loaded {len(NIST_AI_RMF_CONTROLS)} NIST AI RMF subcategories")
    
    if NIST_AI_RMF_CONTROLS:
        print(f"First 5 IDs: {[c['id'] for c in NIST_AI_RMF_CONTROLS[:5]]}")
        print(f"Last 5 IDs: {[c['id'] for c in NIST_AI_RMF_CONTROLS[-5:]]}")
        
        from collections import Counter
        functions = Counter(function_from_id(c['id']) for c in NIST_AI_RMF_CONTROLS)
        print(f"Count by function: {dict(functions)}")
        
        sample = NIST_AI_RMF_CONTROLS[0]
        print(f"--- Sample: {sample['id']} ---")
        print(f"Requirement: {sample['requirement'][:150]}")