"""
Upload route — accept a document file, extract text, detect and anonymize PII,
generate embeddings, store everything in LanceDB vector database, and index
into the patient's PriviCare medical archive.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from anonymization.presidio_engine import analyze_text
from anonymization.pii_vault import get_vault
from ingestion.parser import extract_text_from_pdf, extract_text_from_txt, extract_text_from_image, extract_text_from_dicom, redact_image_pii
from ingestion.chunker import chunk_text
from rag.embeddings import generate_embeddings
from rag.vector_db import add_documents, create_table_if_not_exists
from clinical.patient_records import add_patient_report

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form("default_user"),
    hospital_id: Optional[str] = Form("HOSP_01"),
    uhid: Optional[str] = Form(None),
):
    """Upload a PDF, TXT, or scanned image report for OCR, PII anonymization and RAG indexing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_bytes = file.file.read()
    filename_lower = file.filename.lower()

    # 1. Extract text (OCR for scans/images, text extraction for PDF/TXT)
    if filename_lower.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".txt"):
        raw_text = extract_text_from_txt(file_bytes)
    elif filename_lower.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        raw_text = extract_text_from_image(file_bytes)
    elif filename_lower.endswith(".dcm"):
        raw_text, _ = extract_text_from_dicom(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, TXT, scanned image (PNG/JPG), or DICOM (.dcm) file.",
        )

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file.")

    # 2. Chunk text
    chunks = chunk_text(raw_text, chunk_size=500, overlap=50)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text chunks produced.")

    # 3. Detect PII & anonymize consistently across all chunks using the scoped vault
    vault = get_vault()
    active_user = user_id or "default_user"
    active_hospital = hospital_id or "HOSP_01"
    all_entities = []
    anonymized_chunks: List[str] = []

    for chunk in chunks:
        entities = analyze_text(chunk)
        all_entities.extend(entities)
        anon_chunk, _ = vault.anonymize_text(active_hospital, active_user, chunk, entities, use_scoped_hmac=True)
        anonymized_chunks.append(anon_chunk)

    # 4. Generate embeddings for the clean, anonymized chunks
    document_id = str(uuid.uuid4())
    vectors = generate_embeddings(anonymized_chunks)

    # 5. Store in LanceDB
    create_table_if_not_exists()
    records = [
        {
            "id": str(uuid.uuid4()),
            "text": anon_text,
            "vector": vec,
            "document_id": document_id,
            "department": "Clinical Records",
        }
        for anon_text, vec in zip(anonymized_chunks, vectors)
    ]
    add_documents(records)

    # 6. Build response & index into patient's archive
    entity_types_found = list({e.get("type", "UNKNOWN") for e in all_entities})
    target_uhid = uhid or (active_user if "UHID" in str(active_user) else "UHID-982143")

    add_patient_report(
        uhid=target_uhid,
        report_data={
            "id": f"rep-{uuid.uuid4().hex[:6]}",
            "filename": file.filename,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "department": "Uploaded Clinical Report",
            "type": "Diagnostic Report (OCR/Text)",
            "summary": f"Uploaded report '{file.filename}' processed through PriviCare Zero-Trust pipeline.",
            "key_findings": f"Processed {len(anonymized_chunks)} chunks with {len(entity_types_found)} PII categories scrubbed.",
            "scrubbed_entities": [f"{e.get('type')}: {e.get('text', '')}" for e in all_entities[:6]],
            "text_content": raw_text[:2000]
        }
    )

    return {
        "status": "success",
        "document_id": document_id,
        "filename": file.filename,
        "chunks_processed": len(anonymized_chunks),
        "entities_found": entity_types_found,
        "sample_anonymized_text": anonymized_chunks[0][:500] if anonymized_chunks else "",
        "user_id": active_user,
        "uhid": target_uhid,
    }
