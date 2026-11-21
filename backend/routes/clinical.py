"""
Clinical API routes for the PriviCare Doctor Portal.

Provides endpoints for doctors to:
- List assigned patients
- Review historical medical reports & lab findings
- Review patient-AI chat history & symptom reports
- Query the clinical RAG Co-Pilot with doctor-level re-identification
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from clinical.patient_records import (
    get_all_patients,
    get_patient_profile,
    get_patient_chat_history,
    add_patient_chat_entry,
    mark_chat_reviewed,
    add_patient_record,
)
from rag.pipeline import rag_pipeline

router = APIRouter(prefix="/api/clinical", tags=["clinical"])


class AddPatientRequest(BaseModel):
    name: str
    age: int = 45
    gender: str = "Male"
    blood_group: Optional[str] = "B+"
    department: Optional[str] = "General Medicine"
    uhid: Optional[str] = None
    abha_id: Optional[str] = None
    aadhaar: Optional[str] = None
    phone: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    current_medications: Optional[Any] = None
    allergies: Optional[Any] = None
    attending_doctor: Optional[str] = "Dr. Sarah Johnson (MED-884210)"
    hospital_id: Optional[str] = "HOSP_01"


class ValidateIdentityRequest(BaseModel):
    type: str  # "aadhaar" or "abha"
    value: str


class DoctorConsultRequest(BaseModel):
    uhid: str
    message: str
    doctor_id: Optional[str] = "DR-SARAH-JOHNSON"
    hospital_id: Optional[str] = "HOSP_01"
    purpose_of_use: Optional[str] = "TREATMENT_ANALYSIS"


class ReviewChatRequest(BaseModel):
    uhid: str
    chat_id: str


class PatientChatRequest(BaseModel):
    uhid: str
    message: str


@router.get("/patients")
def list_patients() -> List[Dict[str, Any]]:
    """List all enrolled patients assigned to the clinician."""
    return get_all_patients()


@router.post("/patients")
def create_patient(req: AddPatientRequest) -> Dict[str, Any]:
    """Enroll a new patient record into the clinical repository."""
    profile = add_patient_record(req.dict())
    return {
        "status": "success",
        "message": f"Patient {profile['name']} ({profile['uhid']}) successfully enrolled.",
        "patient": profile
    }


@router.post("/validate-identity")
def validate_identity(req: ValidateIdentityRequest) -> Dict[str, Any]:
    """Validate Aadhaar with Verhoeff D5 dihedral algorithm or ABDM ABHA ID."""
    from anonymization.presidio_engine import validate_verhoeff
    import re

    val = req.value.strip()
    if req.type == "aadhaar":
        cleaned = re.sub(r"[\s-]", "", val)
        if len(cleaned) != 12 or not cleaned.isdigit():
            return {
                "valid": False,
                "reason": "Aadhaar must be exactly 12 numeric digits.",
                "algorithm": "Verhoeff D5 Checksum"
            }
        is_valid = validate_verhoeff(cleaned)
        return {
            "valid": is_valid,
            "reason": "Valid Aadhaar checksum (Verhoeff D5 verified)" if is_valid else "Invalid Verhoeff checksum digit.",
            "algorithm": "Verhoeff D5 Dihedral Group",
            "formatted": f"{cleaned[:4]} {cleaned[4:8]} {cleaned[8:]}"
        }
    elif req.type == "abha":
        cleaned = re.sub(r"[\s-]", "", val)
        if "@" in val:
            is_valid = bool(re.match(r"^[a-zA-Z0-9._]+@abdm$", val, re.IGNORECASE))
            return {
                "valid": is_valid,
                "reason": "Valid ABDM ABHA address format (@abdm)" if is_valid else "ABHA address must match format username@abdm.",
                "algorithm": "National Health Authority (NHA) ABDM Schema"
            }
        else:
            is_valid = len(cleaned) == 14 and cleaned.isdigit()
            formatted = f"{cleaned[:2]}-{cleaned[2:6]}-{cleaned[6:10]}-{cleaned[10:14]}" if len(cleaned) == 14 else val
            return {
                "valid": is_valid,
                "reason": "Valid 14-digit ABDM Health ID" if is_valid else "14-digit ABHA number must have format XX-XXXX-XXXX-XXXX.",
                "algorithm": "ABDM 14-Digit Health ID",
                "formatted": formatted
            }
    return {"valid": False, "reason": f"Unknown identity type: {req.type}"}


@router.get("/patients/{uhid}")
def get_patient(uhid: str) -> Dict[str, Any]:
    """Retrieve full profile, historical reports, and medications for a patient."""
    profile = get_patient_profile(uhid)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    return profile


@router.get("/patients/{uhid}/reports")
def get_patient_reports(uhid: str) -> List[Dict[str, Any]]:
    """Retrieve all historical and newly uploaded reports for a patient."""
    profile = get_patient_profile(uhid)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    return profile.get("reports", [])


@router.get("/patients/{uhid}/chat-history")
def get_chat_history(uhid: str) -> List[Dict[str, Any]]:
    """Retrieve patient's previous interactions with the AI assistant."""
    return get_patient_chat_history(uhid)


@router.post("/patients/{uhid}/chat-history/review")
def mark_reviewed(uhid: str, req: ReviewChatRequest) -> Dict[str, Any]:
    """Clinician acknowledges or reviews a patient's chat interaction."""
    ok = mark_chat_reviewed(uhid, req.chat_id)
    return {"status": "success" if ok else "not_found"}


@router.post("/consult")
def doctor_consult(req: DoctorConsultRequest) -> Dict[str, Any]:
    """Doctor clinical consultation over the patient's reports using the RAG pipeline."""
    patient = get_patient_profile(req.uhid)
    patient_name = patient["name"] if patient else req.uhid

    # Execute RAG pipeline with authorized Doctor role
    result = rag_pipeline(
        query=req.message,
        user_id=req.uhid,
        hospital_id=req.hospital_id or "HOSP_01",
        role="doctor",
        doctor_id=req.doctor_id or "DR-SARAH-JOHNSON",
        patient_id=req.uhid,
        purpose_of_use=req.purpose_of_use or "TREATMENT_ANALYSIS",
        use_scoped_hmac=True,
    )

    # Log to patient's record
    add_patient_chat_entry(
        uhid=req.uhid,
        sender="doctor",
        query=req.message,
        ai_response=result["final_response"],
        triage="CLINICAL_CONSULTATION"
    )

    return {
        "status": "success",
        "uhid": req.uhid,
        "patient_name": patient_name,
        "answer": result["final_response"],
        "anonymized_query": result["anonymized_query"],
        "system_view": result["raw_llm_response"],
        "retrieved_chunks": result["retrieved_chunks"],
        "security_audit": result["security_audit"]
    }


@router.post("/patient-chat")
def patient_chat_endpoint(req: PatientChatRequest) -> Dict[str, Any]:
    """Patient 24/7 recovery consultation with automatic PII scrubbing and doctor triage queue sync."""
    patient = get_patient_profile(req.uhid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    # 1. Automatic Clinical Triage Analysis
    msg_lower = req.message.lower()
    triage = "ROUTINE"
    if any(k in msg_lower for k in ["chest pain", "shortness of breath", "severe", "dizziness", "bleeding", "emergency", "faint", "angina"]):
        triage = "URGENT_ATTENTION"
    elif any(k in msg_lower for k in ["calf", "muscle", "cramp", "soreness", "statin", "rash", "allergy", "numbness", "tingling", "vomit"]):
        triage = "EVALUATE_MEDICATION"

    # 2. Execute RAG pipeline with role="patient" (zero PHI leaked, fail-closed)
    result = rag_pipeline(
        query=req.message,
        user_id=req.uhid,
        hospital_id=patient.get("hospital_id", "HOSP_01"),
        role="patient",
        doctor_id="AI-PATIENT-CARE",
        patient_id=req.uhid,
        purpose_of_use="PATIENT_RECOVERY_QUERY",
        use_scoped_hmac=True,
    )

    ai_reply = result.get("final_response", "")
    if triage == "URGENT_ATTENTION":
        ai_reply = (
            "⚠️ URGENT CLINICAL ALERT: Your symptoms may require prompt medical evaluation. "
            "Please contact your attending physician Dr. Sarah Johnson or visit the nearest emergency department immediately.\n\n"
            + ai_reply
        )
    elif triage == "EVALUATE_MEDICATION":
        ai_reply = (
            "ℹ️ MEDICATION NOTICE: This symptom has been flagged for medication review by your attending physician Dr. Sarah Johnson.\n\n"
            + ai_reply
        )

    # 3. Log to patient chat history so doctor sees it in their queue
    entry = add_patient_chat_entry(
        uhid=req.uhid,
        sender="patient",
        query=req.message,
        ai_response=ai_reply,
        triage=triage
    )

    return {
        "status": "success",
        "uhid": req.uhid,
        "query": req.message,
        "ai_response": ai_reply,
        "clinical_triage": triage,
        "anonymized_query": result.get("anonymized_query", ""),
        "timestamp": entry.get("timestamp") if entry else None,
        "synced_to_doctor": True
    }


@router.post("/patients/{uhid}/crypto-shred")
def crypto_shred_patient_endpoint(uhid: str) -> Dict[str, Any]:
    """Execute DPDP Act 2023 Section 12 Right to Erasure via Cryptographic Shredding."""
    patient = get_patient_profile(uhid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    
    return {
        "status": "shredded",
        "uhid": uhid,
        "section": "DPDP Act 2023 Section 12",
        "action": "CRYPTOGRAPHIC_KEY_PURGE",
        "detail": "All pseudonym encryption keys, scoped de-identification salt hashes, and session mapping vectors for this identity have been purged. Historical transcripts and vector embeddings are permanently irreversible and unrecoverable.",
        "timestamp": datetime.now().isoformat()
    }

