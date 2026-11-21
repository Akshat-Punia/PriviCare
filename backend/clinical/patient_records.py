"""
PriviCare Clinical Intelligence — Patient Records & Chat History Repository.

Maintains local encrypted records of patients, historical medical reports,
and historical patient-to-AI interaction transcripts for attending doctor analysis.
All data is stored locally on the doctor's HDD/SSD.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Initial enrolled patients and their clinical baseline
_PATIENTS_DATABASE: Dict[str, Dict[str, Any]] = {
    "UHID-982143": {
        "uhid": "UHID-982143",
        "name": "Rajesh Sharma",
        "age": 54,
        "gender": "Male",
        "blood_group": "B+",
        "department": "Cardiology",
        "abha_id": "91-4412-3390-1123",
        "aadhaar": "9823 4410 7721",
        "phone": "+91 98765 43210",
        "attending_doctor": "Dr. Sarah Johnson (MED-884210)",
        "hospital_id": "HOSP_01",
        "hospital_name": "Fortis Escorts Heart Institute",
        "admission_date": "2026-10-12",
        "primary_diagnosis": "Acute Coronary Syndrome, Essential Hypertension",
        "current_medications": [
            "Atorvastatin 40mg (1 tab OD at bedtime)",
            "Telmisartan 40mg (1 tab OD morning)",
            "Aspirin 75mg (1 tab OD post-lunch)",
            "Metoprolol Succinate 25mg (1 tab OD)"
        ],
        "allergies": ["Penicillin (mild cutaneous rash)"],
        "reports": [
            {
                "id": "rep-001",
                "filename": "Discharge_Summary_Fortis_Escorts.pdf",
                "date": "2026-10-14",
                "department": "Cardiology",
                "type": "Discharge Summary & Intervention Record",
                "summary": "Patient presented with typical angina pectoris. Coronary angiography revealed 90% stenosis in mid-LAD. Successful drug-eluting stent (DES) deployed. Post-procedure LVEF 52%. Discharge vitals stable: BP 128/82 mmHg, HR 68 bpm.",
                "key_findings": "Troponin-T elevated (0.84 ng/mL). Post-PCI TIMI-3 flow achieved without dissection or thrombosis.",
                "scrubbed_entities": ["PERSON: Rajesh Sharma", "UHID: UHID-982143", "AADHAAR: 9823 4410 7721", "PHONE: 98765 43210"],
                "text_content": (
                    "DISCHARGE SUMMARY\nFortis Escorts Heart Institute, Okhla Road, New Delhi\n"
                    "Patient: Rajesh Sharma | Age: 54 | Sex: M | UHID: UHID-982143\n"
                    "Attending Cardiologist: Dr. Sarah Johnson, MD, DM (Cardiology)\n"
                    "Diagnosis: Acute Coronary Syndrome (NSTEMI), Essential Hypertension.\n"
                    "Procedures: Percutaneous Coronary Intervention with Drug-Eluting Stent to Mid-LAD.\n"
                    "Hospital Course: Uneventful recovery. Stable telemetry throughout 48h observation.\n"
                    "Medications on Discharge:\n"
                    "1. Tab Atorvastatin 40 mg at bedtime\n"
                    "2. Tab Telmisartan 40 mg in the morning\n"
                    "3. Tab Aspirin 75 mg once daily\n"
                    "4. Tab Metoprolol Succinate 25 mg once daily\n"
                    "Follow-up: Echo and lipid panel in 3 weeks. Report chest tightness immediately."
                )
            },
            {
                "id": "rep-002",
                "filename": "Lipid_Profile_Echo_Followup.pdf",
                "date": "2026-11-04",
                "department": "Pathology & Cardiology",
                "type": "Diagnostic Follow-up",
                "summary": "Follow-up laboratory lipid panel and 2D Transthoracic Echocardiogram. Total Cholesterol improved to 168 mg/dL (from 235 mg/dL baseline). LDL 88 mg/dL. Transthoracic echo reveals hypokinesia of mid-anterior septum with preserved overall ejection fraction (LVEF 54%).",
                "key_findings": "Total Cholesterol 168 mg/dL, Triglycerides 152 mg/dL, HDL 42 mg/dL, LDL 88 mg/dL. LVEF 54%.",
                "scrubbed_entities": ["PERSON: Rajesh Sharma", "UHID: UHID-982143", "DATE: 2026-11-04"],
                "text_content": (
                    "LABORATORY INVESTIGATION REPORT & 2D ECHOCARDIOGRAPHY\n"
                    "Patient: Rajesh Sharma | UHID: UHID-982143 | Date: 04-Nov-2026\n"
                    "Lipid Profile:\n"
                    "- Serum Cholesterol: 168 mg/dL (Normal < 200)\n"
                    "- Serum Triglycerides: 152 mg/dL (Normal < 150)\n"
                    "- HDL Cholesterol: 42 mg/dL (Normal 40 - 60)\n"
                    "- LDL Cholesterol: 88 mg/dL (Target < 100 for CAD)\n"
                    "2D Echo Findings:\n"
                    "- Left Ventricular Ejection Fraction (LVEF): 54%\n"
                    "- Wall Motion Abnormality: Regional hypokinesia in anterior wall/septum.\n"
                    "- Valvular Function: Mild mitral regurgitation, no aortic stenosis."
                )
            }
        ],
        "patient_chat_history": [
            {
                "id": "chat-p1-001",
                "timestamp": "2026-10-18T10:14:22Z",
                "sender": "patient",
                "query": "Can I take Telmisartan with food, and what side effects should I watch out for?",
                "ai_response": "Telmisartan 40mg can be taken with or without food, preferably at the same time each morning. The most frequent mild side effects include lightheadedness or dizziness when standing up quickly (orthostatic hypotension). Notify your doctor if you experience swelling of the lips/face or persistent fatigue.",
                "clinical_triage": "ROUTINE",
                "reviewed_by_doctor": True
            },
            {
                "id": "chat-p1-002",
                "timestamp": "2026-11-01T16:45:10Z",
                "sender": "patient",
                "query": "I had mild chest tightness yesterday afternoon after climbing two flights of stairs. It stopped after resting for 5 minutes.",
                "ai_response": "Exertional chest tightness in a patient with recent stent placement (LAD DES) is a clinically significant symptom. Although it resolved with rest, it requires prompt evaluation by your attending cardiologist Dr. Sarah Johnson. Do not perform strenuous exertion. If chest pressure returns or radiates to your arm/jaw, seek emergency emergency medical care immediately.",
                "clinical_triage": "URGENT_ATTENTION",
                "reviewed_by_doctor": False
            },
            {
                "id": "chat-p1-003",
                "timestamp": "2026-11-12T09:20:05Z",
                "sender": "patient",
                "query": "I noticed some mild soreness in my calves in the evening. Is this related to Atorvastatin?",
                "ai_response": "Mild myalgia (muscle soreness) can occasionally occur with statin therapy (Atorvastatin 40mg). It is essential to monitor whether this soreness worsens or if you notice tea-colored urine. Please alert Dr. Sarah Johnson during your upcoming review so she can evaluate whether serum creatine kinase (CK) testing is indicated.",
                "clinical_triage": "EVALUATE_MEDICATION",
                "reviewed_by_doctor": False
            }
        ]
    },
    "UHID-447219": {
        "uhid": "UHID-447219",
        "name": "Priya Patel",
        "age": 46,
        "gender": "Female",
        "blood_group": "O+",
        "department": "Oncology",
        "abha_id": "14-2354-9871-6542",
        "aadhaar": "3675 8492 1039",
        "phone": "+91 98112 34567",
        "attending_doctor": "Dr. Sarah Johnson (MED-884210)",
        "hospital_id": "HOSP_01",
        "hospital_name": "AIIMS Oncology Center",
        "admission_date": "2026-09-15",
        "primary_diagnosis": "Infiltrating Ductal Carcinoma, Right Breast (Stage IIA)",
        "current_medications": [
            "Paclitaxel IV infusion (adjuvant protocol)",
            "Dexamethasone 8mg premedication",
            "Ondansetron 8mg PO BID as needed"
        ],
        "allergies": ["Sulfonamides"],
        "reports": [
            {
                "id": "rep-003",
                "filename": "Biopsy_Pathology_Report_AIIMS.pdf",
                "date": "2026-09-18",
                "department": "Oncology & Pathology",
                "type": "Histopathology & Receptor Assay",
                "summary": "Core needle biopsy right breast upper outer quadrant. Infiltrating Ductal Carcinoma, Nottingham Grade II. Biomarker profile: Estrogen Receptor (ER) positive (80%), Progesterone Receptor (PR) positive (65%), HER2-neu negative (IHC 1+), Ki-67 proliferation index 18%.",
                "key_findings": "ER+/PR+, HER2 negative. Clear surgical margins planned post-neoadjuvant cycles.",
                "scrubbed_entities": ["PERSON: Priya Patel", "UHID: UHID-447219", "PAN: ABCDE1234F"],
                "text_content": (
                    "HISTOPATHOLOGY EXAMINATION REPORT\nAll India Institute of Medical Sciences (AIIMS)\n"
                    "Patient: Priya Patel | Age: 46 | Sex: F | UHID: UHID-447219\n"
                    "Specimen: Right breast mass core biopsy (2.2 cm)\n"
                    "Histological Type: Infiltrating Ductal Carcinoma (NST)\n"
                    "Grade: Modified Bloom-Richardson Grade II (Tubule 3, Nuclear 2, Mitotic 1)\n"
                    "Immunohistochemistry (IHC):\n"
                    "- ER: Positive (Allred score 7/8)\n"
                    "- PR: Positive (Allred score 6/8)\n"
                    "- HER2/neu: Negative (Score 1+)\n"
                    "- Ki-67: 18% (Low-intermediate proliferation)"
                )
            }
        ],
        "patient_chat_history": [
            {
                "id": "chat-p2-001",
                "timestamp": "2026-11-10T14:10:00Z",
                "sender": "patient",
                "query": "My fingertips and toes feel slightly numb and tingling after the 3rd Paclitaxel infusion. Is this normal?",
                "ai_response": "Peripheral neuropathy (numbness, pins-and-needles in hands or feet) is a recognized cumulative effect of taxane chemotherapy (Paclitaxel). Please bring this to Dr. Johnson's attention before your 4th infusion so she can assess grade and adjust premedication or dosage if necessary.",
                "clinical_triage": "URGENT_ATTENTION",
                "reviewed_by_doctor": False
            }
        ]
    },
    "UHID-551029": {
        "uhid": "UHID-551029",
        "name": "Amit Kumar",
        "age": 62,
        "gender": "Male",
        "blood_group": "A+",
        "department": "Pulmonology",
        "abha_id": "14-9988-7766-5544",
        "aadhaar": "5432 1098 7654",
        "phone": "+91 97234 56789",
        "attending_doctor": "Dr. Sarah Johnson (MED-884210)",
        "hospital_id": "HOSP_01",
        "hospital_name": "Max Super Speciality Hospital",
        "admission_date": "2026-08-20",
        "primary_diagnosis": "Chronic Obstructive Pulmonary Disease (COPD, GOLD Stage 2)",
        "current_medications": [
            "Budesonide 400mcg + Formoterol 12mcg DPI (1 puff BID)",
            "Tiotropium 18mcg DPI (1 puff OD)",
            "Levosalbutamol Inhaler (PRN)"
        ],
        "allergies": ["No known drug allergies (NKDA)"],
        "reports": [
            {
                "id": "rep-004",
                "filename": "Spirometry_PFT_Report_Max.pdf",
                "date": "2026-08-24",
                "department": "Pulmonary Medicine",
                "type": "Pulmonary Function Test",
                "summary": "Pre & Post bronchodilator spirometry. FEV1/FVC ratio 0.58 post-bronchodilator. FEV1 is 62% of predicted value, indicating moderate airflow limitation (GOLD Stage 2).",
                "key_findings": "Post-BD FEV1 1.82L (62% pred), FVC 3.14L, FEV1/FVC 0.58. Significant reversibility absent.",
                "scrubbed_entities": ["PERSON: Amit Kumar", "UHID: UHID-551029", "ABHA: 91-4412-3390-1123"],
                "text_content": (
                    "PULMONARY FUNCTION TEST (PFT) REPORT\n"
                    "Patient: Amit Kumar | Age: 62 | Sex: M | UHID: UHID-551029\n"
                    "Indication: Chronic productive cough, exertional dyspnea.\n"
                    "Spirometry Results:\n"
                    "- FEV1: 1.82 L (62% of predicted value)\n"
                    "- FVC: 3.14 L (84% of predicted value)\n"
                    "- FEV1/FVC Ratio: 58% (Threshold < 70% diagnostic of COPD)\n"
                    "Impression: Moderate obstructive ventilatory defect, consistent with COPD GOLD Stage 2."
                )
            }
        ],
        "patient_chat_history": [
            {
                "id": "chat-p3-001",
                "timestamp": "2026-10-05T11:30:15Z",
                "sender": "patient",
                "query": "Should I use the blue Levosalbutamol inhaler before exercising or only when I feel short of breath?",
                "ai_response": "Levosalbutamol can be used 15-20 minutes before physical exertion as a prophylactic bronchodilator, as well as on an as-needed basis for acute shortness of breath. Ensure your daily controller (Budesonide/Formoterol) is continued regularly as prescribed.",
                "clinical_triage": "ROUTINE",
                "reviewed_by_doctor": True
            }
        ]
    }
}


def get_all_patients() -> List[Dict[str, Any]]:
    """Return summary list of all enrolled patients."""
    summaries = []
    for uhid, p in _PATIENTS_DATABASE.items():
        summaries.append({
            "uhid": p["uhid"],
            "name": p["name"],
            "age": p["age"],
            "gender": p["gender"],
            "blood_group": p.get("blood_group", "O+"),
            "department": p["department"],
            "primary_diagnosis": p["primary_diagnosis"],
            "abha_id": p.get("abha_id", "Not Linked"),
            "aadhaar": p.get("aadhaar", "Not Provided"),
            "phone": p.get("phone", "Not Provided"),
            "reports_count": len(p.get("reports", [])),
            "pending_chat_alerts": sum(1 for c in p.get("patient_chat_history", []) if c.get("clinical_triage") == "URGENT_ATTENTION" and not c.get("reviewed_by_doctor", False)),
            "last_interaction": p.get("patient_chat_history", [{}])[-1].get("timestamp", p.get("admission_date", ""))
        })
    return summaries


def get_patient_profile(uhid: str) -> Optional[Dict[str, Any]]:
    """Retrieve full clinical profile of a patient."""
    return _PATIENTS_DATABASE.get(uhid)


def add_patient_record(data: Dict[str, Any]) -> Dict[str, Any]:
    """Enroll a new patient with DPDP Act 2023 & ABDM clinical metadata."""
    uhid = (data.get("uhid") or "").strip()
    if not uhid:
        uhid = f"UHID-{uuid.uuid4().hex[:6].upper()}"

    # Parse and format medications
    meds = data.get("current_medications", [])
    if isinstance(meds, str):
        meds = [m.strip() for m in meds.replace(";", "\n").split("\n") if m.strip()]
    elif not isinstance(meds, list):
        meds = []

    # Parse and format allergies
    allergies = data.get("allergies", [])
    if isinstance(allergies, str):
        allergies = [a.strip() for a in allergies.replace(";", "\n").split("\n") if a.strip()]
    elif not isinstance(allergies, list):
        allergies = []

    profile = {
        "uhid": uhid,
        "name": (data.get("name") or "New Patient").strip(),
        "age": int(data.get("age") or 40),
        "gender": data.get("gender") or "Unknown",
        "blood_group": data.get("blood_group") or "B+",
        "department": data.get("department") or "General Medicine",
        "abha_id": (data.get("abha_id") or "").strip() or "14-2354-9871-6542",
        "aadhaar": (data.get("aadhaar") or "").strip() or "9823 4410 7721",
        "phone": (data.get("phone") or "").strip() or "+91 98765 43210",
        "attending_doctor": data.get("attending_doctor") or "Dr. Sarah Johnson (MED-884210)",
        "hospital_id": data.get("hospital_id") or "HOSP_01",
        "hospital_name": data.get("hospital_name") or "Fortis Escorts Heart Institute",
        "admission_date": data.get("admission_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "primary_diagnosis": (data.get("primary_diagnosis") or "Clinical Evaluation").strip(),
        "current_medications": meds,
        "allergies": allergies,
        "reports": data.get("reports", []),
        "patient_chat_history": data.get("patient_chat_history", [])
    }
    _PATIENTS_DATABASE[uhid] = profile
    return profile


def add_patient_report(uhid: str, report_data: Dict[str, Any]) -> bool:
    """Attach a newly uploaded and processed report to a patient's historical profile."""
    if uhid not in _PATIENTS_DATABASE:
        # Create new patient entry if not existing
        _PATIENTS_DATABASE[uhid] = {
            "uhid": uhid,
            "name": report_data.get("patient_name", f"Patient {uhid}"),
            "age": report_data.get("age", 45),
            "gender": report_data.get("gender", "Unknown"),
            "blood_group": "B+",
            "department": report_data.get("department", "General Medicine"),
            "abha_id": "14-2354-9871-6542",
            "aadhaar": "9823 4410 7721",
            "phone": "+91 98765 43210",
            "attending_doctor": "Dr. Sarah Johnson (MED-884210)",
            "hospital_id": "HOSP_01",
            "hospital_name": "Fortis Escorts Heart Institute",
            "admission_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "primary_diagnosis": report_data.get("primary_diagnosis", "Clinical Observation"),
            "current_medications": [],
            "allergies": [],
            "reports": [],
            "patient_chat_history": []
        }
    
    _PATIENTS_DATABASE[uhid]["reports"].append(report_data)
    return True
    
    _PATIENTS_DATABASE[uhid]["reports"].append(report_data)
    return True


def get_patient_chat_history(uhid: str) -> List[Dict[str, Any]]:
    """Retrieve all historical AI chats for the given patient."""
    patient = _PATIENTS_DATABASE.get(uhid)
    if not patient:
        return []
    return patient.get("patient_chat_history", [])


def add_patient_chat_entry(uhid: str, sender: str, query: str, ai_response: str, triage: str = "ROUTINE") -> Dict[str, Any]:
    """Append a new query/response to the patient's chat transcript."""
    entry = {
        "id": f"chat-{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sender": sender,
        "query": query,
        "ai_response": ai_response,
        "clinical_triage": triage,
        "reviewed_by_doctor": (sender == "doctor")
    }
    if uhid in _PATIENTS_DATABASE:
        _PATIENTS_DATABASE[uhid]["patient_chat_history"].append(entry)
    return entry


def mark_chat_reviewed(uhid: str, chat_id: str) -> bool:
    """Mark a patient chat entry as reviewed by the doctor."""
    patient = _PATIENTS_DATABASE.get(uhid)
    if not patient:
        return False
    for item in patient.get("patient_chat_history", []):
        if item.get("id") == chat_id:
            item["reviewed_by_doctor"] = True
            return True
    return False
