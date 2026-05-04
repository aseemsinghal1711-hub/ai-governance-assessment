"""
NIST AI RMF Playbook - parsed from the official NIST CSV.
The CSV is in 'wide' format: columns are subcategory IDs, rows are properties.
"""
import csv
import os
from collections import defaultdict

CSV_PATH = os.path.join(os.path.dirname(__file__), "nist_playbook.csv")


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
        
        title = about[:120] if about else clean_id
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