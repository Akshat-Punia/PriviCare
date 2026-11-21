"""
Chat route — accept a user message, run the full RAG pipeline, and return
the de-anonymised answer together with diagnostic telemetry for split-screen display.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from rag.pipeline import rag_pipeline

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Incoming chat message payload with ABAC attributes."""
    message: str
    user_id: Optional[str] = "default_user"
    hospital_id: Optional[str] = "HOSP_01"
    role: Optional[str] = "doctor"
    doctor_id: Optional[str] = None
    patient_id: Optional[str] = None
    purpose_of_use: Optional[str] = "DIRECT_CARE"
    break_glass: Optional[bool] = False
    use_scoped_hmac: Optional[bool] = True


class ChatResponse(BaseModel):
    """Chat response payload."""
    answer: str
    original_query: str
    anonymized_query: str
    retrieved_chunks: List[str]
    system_view: str
    security_audit: Dict[str, Any]


@router.post("/chat")
def chat(request: ChatRequest):
    """Process a chat query through the privacy-preserving RAG pipeline with ABAC enforcement."""
    result = rag_pipeline(
        query=request.message,
        user_id=request.user_id or "default_user",
        hospital_id=request.hospital_id or "HOSP_01",
        role=request.role or "doctor",
        doctor_id=request.doctor_id,
        patient_id=request.patient_id,
        purpose_of_use=request.purpose_of_use or "DIRECT_CARE",
        break_glass=bool(request.break_glass),
        use_scoped_hmac=True if request.use_scoped_hmac is None else request.use_scoped_hmac,
    )

    return {
        "answer": result["final_response"],
        "original_query": result["original_query"],
        "anonymized_query": result["anonymized_query"],
        "retrieved_chunks": result["retrieved_chunks"],
        "system_view": result["raw_llm_response"],
        "security_audit": result["security_audit"],
    }
