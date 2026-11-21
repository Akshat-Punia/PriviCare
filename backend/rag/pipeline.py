"""
End-to-end RAG pipeline with Contextual ABAC and Privacy-Preserving Isolation.

Security Statement:
HealthGuard AI is designed to prevent detected PHI and PII from entering vector storage
or external model requests, with leakage testing, auditability and fail-closed processing.

Unidirectional Architectural Flow:
1. Raw Document -> Local NER & Rule Engine (Aadhaar, ABHA, PAN, UHID, Phones, Names)
2. Scoped Pseudonymized Document -> LanceDB Vector Database
3. Clinician Query Interception -> Scoped HMAC Pseudonymization
4. Sanitized Context + Query -> External Model / LLM (Zero PHI transmitted)
5. Untrusted LLM Response -> Local Contextual ABAC Vault (Strict Verification)
6. Authorized Clinician -> Re-hydrated Clinical Response (or Sanitized for Researchers)
"""

from typing import Dict, Any, Optional

from anonymization.presidio_engine import analyze_text
from anonymization.pii_vault import get_vault
from chat.llm import generate_response
from rag.retrieval import retrieve_relevant_chunks


def rag_pipeline(
    query: str,
    user_id: str = "default_user",
    hospital_id: str = "HOSP_01",
    role: str = "doctor",
    doctor_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    purpose_of_use: str = "DIRECT_CARE",
    break_glass: bool = False,
    use_scoped_hmac: bool = True,
) -> Dict[str, Any]:
    """Execute the full privacy-preserving RAG pipeline with ABAC authorization."""
    vault = get_vault()

    # 1. Detect PII entities in the user prompt (supports Indian entities & OCR variants)
    detected_entities = analyze_text(query)

    # 2. Swap real identifiers with scoped HMAC pseudonyms inside isolated hospital vault
    anonymized_query, applied_tags = vault.anonymize_query(
        hospital_id,
        user_id,
        query,
        detected_entities,
        use_scoped_hmac=use_scoped_hmac,
    )

    # 3. Retrieve relevant anonymized chunks from vector database
    retrieved_chunks = retrieve_relevant_chunks(anonymized_query, top_k=4)

    # 4. Generate LLM response (Zero PHI boundary — LLM only sees synthetic tokens)
    raw_llm_response = generate_response(anonymized_query, retrieved_chunks)

    # 5. Local Contextual ABAC Re-identification
    # Fails closed if role != doctor or treatment relationship is missing
    reidentified_result = vault.reverse_lookup(
        hospital_id,
        user_id,
        raw_llm_response,
        user_role=role,
        doctor_id=doctor_id or user_id,
        target_patient_id=patient_id,
        purpose_of_use=purpose_of_use,
        is_break_glass=break_glass,
    )

    abac_audit = getattr(reidentified_result, "audit", {})

    return {
        "original_query": query,
        "anonymized_query": anonymized_query,
        "retrieved_chunks": retrieved_chunks,
        "raw_llm_response": raw_llm_response,
        "final_response": str(reidentified_result),
        "security_audit": {
            "pii_detected_count": len(detected_entities),
            "applied_tags": list(applied_tags.keys()),
            "hospital_id": hospital_id,
            "user_id": user_id,
            "role": role,
            "abac_status": abac_audit.get("status", "AUTHORIZED"),
            "re_identified": abac_audit.get("re_identified", True),
            "audit_id": abac_audit.get("audit_id", "N/A"),
            "compliance_guarantee": (
                "HealthGuard AI is designed to prevent detected PHI and PII from entering "
                "vector storage or external model requests, with leakage testing, auditability "
                "and fail-closed processing."
            ),
        },
    }
