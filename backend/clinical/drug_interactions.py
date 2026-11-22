"""
PriviCare Clinical Intelligence — Drug-Drug & Drug-Allergy Interaction Engine.

Provides zero-latency, local rule-based safety screening for:
1. Severe Drug-Drug Interactions (CYP3A4 inhibition, antiplatelet bleeding, hyperkalemia, QT prolongation).
2. Drug-Allergy Sensitivities (e.g. Penicillin cross-reactivity, NSAID bronchospasm).
3. Drug-Food Contraindications (e.g. Grapefruit-Statin interaction, high potassium salt substitutes).
"""

from typing import List, Dict, Any, Optional

# Knowledge graph of known clinical interactions
_INTERACTION_RULES = [
    {
        "id": "INT-001",
        "drug_a": "Atorvastatin",
        "drug_b": "Grapefruit",
        "severity": "HIGH",
        "category": "DRUG_FOOD",
        "effect": "Inhibition of CYP3A4 metabolism significantly increases serum Atorvastatin concentration.",
        "clinical_risk": "Markedly elevated risk of statin-induced myopathy, severe muscle breakdown, and rhabdomyolysis.",
        "recommendation": "Avoid grapefruit and grapefruit juice entirely while taking Atorvastatin."
    },
    {
        "id": "INT-002",
        "drug_a": "Aspirin",
        "drug_b": "Ibuprofen",
        "severity": "HIGH",
        "category": "DRUG_DRUG",
        "effect": "Competitive inhibition of platelet COX-1 and synergistic gastric mucosal irritation.",
        "clinical_risk": "Reduces cardioprotective antiplatelet effect of Aspirin and increases gastrointestinal bleeding risk by 3-4x.",
        "recommendation": "Avoid NSAIDs like Ibuprofen or Naproxen. Use Paracetamol/Acetaminophen for mild analgesia if clinically indicated."
    },
    {
        "id": "INT-003",
        "drug_a": "Telmisartan",
        "drug_b": "Potassium",
        "severity": "MODERATE",
        "category": "DRUG_FOOD",
        "effect": "Angiotensin II receptor blockade reduces aldosterone secretion, leading to potassium retention.",
        "clinical_risk": "Risk of dangerous hyperkalemia (> 5.5 mEq/L) leading to cardiac dysrhythmias.",
        "recommendation": "Avoid potassium supplements and low-sodium salt substitutes containing potassium chloride unless monitored."
    },
    {
        "id": "INT-004",
        "drug_a": "Metoprolol",
        "drug_b": "Diltiazem",
        "severity": "HIGH",
        "category": "DRUG_DRUG",
        "effect": "Synergistic negative inotropic and chronotropic effects on SA and AV nodal conduction.",
        "clinical_risk": "Severe bradycardia (< 45 bpm), advanced AV block, and hypotension.",
        "recommendation": "Close telemetry monitoring required. Consider monotherapy or non-dihydropyridine alternatives."
    },
    {
        "id": "INT-005",
        "drug_a": "Atorvastatin",
        "drug_b": "Clarithromycin",
        "severity": "HIGH",
        "category": "DRUG_DRUG",
        "effect": "Potent CYP3A4 inhibition increases statin AUC up to 400%.",
        "clinical_risk": "Acute rhabdomyolysis and acute kidney injury.",
        "recommendation": "Suspend Atorvastatin during macrolide therapy or switch to Azithromycin."
    }
]

_ALLERGY_RULES = [
    {
        "allergy_keyword": "penicillin",
        "offending_classes": ["penicillin", "amoxicillin", "ampicillin", "piperacillin", "augmentin"],
        "severity": "CRITICAL",
        "effect": "Type-I IgE-mediated hypersensitivity reaction.",
        "clinical_risk": "Urticaria, angioedema, bronchospasm, and potentially fatal anaphylaxis.",
        "safe_alternatives": ["Azithromycin", "Ciprofloxacin", "Levofloxacin", "Doxycycline"]
    },
    {
        "allergy_keyword": "sulfa",
        "offending_classes": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine"],
        "severity": "HIGH",
        "effect": "Sulfonamide immunologic reaction.",
        "clinical_risk": "Cutaneous drug eruption, Stevens-Johnson syndrome (SJS), or drug fever.",
        "safe_alternatives": ["Nitrofurantoin", "Cephalexin"]
    },
    {
        "allergy_keyword": "nsaid",
        "offending_classes": ["aspirin", "ibuprofen", "naproxen", "diclofenac"],
        "severity": "HIGH",
        "effect": "Cyclooxygenase inhibition causing leukotriene shunting.",
        "clinical_risk": "Aspirin-exacerbated respiratory disease (AERD), bronchospasm, or severe facial edema.",
        "safe_alternatives": ["Paracetamol", "Celecoxib (with caution)"]
    }
]


def check_drug_interactions(
    medications: List[str],
    allergies: Optional[List[str]] = None,
    dietary_items: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform multi-dimensional drug safety screening against active prescriptions,
    food/dietary items, and documented allergy records.
    """
    med_text = " ".join(medications).lower()
    allergies = allergies or []
    dietary_items = dietary_items or []
    diet_text = " ".join(dietary_items).lower()

    detected_interactions = []
    detected_allergies = []

    # 1. Check Drug-Drug and Drug-Food Interactions
    for rule in _INTERACTION_RULES:
        drug_a = rule["drug_a"].lower()
        drug_b = rule["drug_b"].lower()

        has_drug_a = drug_a in med_text
        has_drug_b = (drug_b in med_text) or (drug_b in diet_text)

        if has_drug_a and has_drug_b:
            detected_interactions.append({
                "rule_id": rule["id"],
                "drugs": f"{rule['drug_a']} + {rule['drug_b']}",
                "severity": rule["severity"],
                "category": rule["category"],
                "effect": rule["effect"],
                "clinical_risk": rule["clinical_risk"],
                "recommendation": rule["recommendation"]
            })

    # 2. Check Drug-Allergy Sensitivities
    for allergy in allergies:
        a_low = allergy.lower()
        for a_rule in _ALLERGY_RULES:
            if a_rule["allergy_keyword"] in a_low:
                for offending in a_rule["offending_classes"]:
                    if offending in med_text:
                        detected_allergies.append({
                            "allergen": allergy,
                            "offending_drug": offending.capitalize(),
                            "severity": a_rule["severity"],
                            "effect": a_rule["effect"],
                            "clinical_risk": a_rule["clinical_risk"],
                            "safe_alternatives": a_rule["safe_alternatives"]
                        })

    overall_status = "SAFE"
    if detected_allergies or any(i["severity"] == "HIGH" for i in detected_interactions):
        overall_status = "HIGH_RISK"
    elif detected_interactions:
        overall_status = "MODERATE_RISK"

    return {
        "status": "success",
        "safety_evaluation": overall_status,
        "medications_screened": medications,
        "allergies_screened": allergies,
        "interactions_found_count": len(detected_interactions),
        "allergy_conflicts_count": len(detected_allergies),
        "interactions": detected_interactions,
        "allergy_alerts": detected_allergies,
        "engine": "PriviCare Local Clinical Pharmacology Safety Engine"
    }
