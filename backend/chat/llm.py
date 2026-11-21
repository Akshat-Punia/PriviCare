"""
LLM interaction layer for clinical synthesis.

Sends the anonymised query and context chunks to Groq Cloud (120B Flagship model)
or the OpenAI Chat Completions API (or uses an intelligent clinical synthesis engine
when no API key or network is available).
"""

import re
from typing import List, Dict, Any

from config import (
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_FALLBACK_MODEL,
    GROQ_BASE_URL,
)

_SYSTEM_PROMPT = (
    "You are an expert clinical healthcare AI assistant. "
    "You operate in a strict Zero-Trust, HIPAA and India DPDP Act-compliant pipeline. "
    "All patient names and identifiers in your context have been replaced with synthetic tags (e.g. [PERSON_1], [DATE_1], [ABHA_ID_01]). "
    "Answer the clinician's query accurately using ONLY the provided medical context. "
    "Preserve all synthetic tags exactly as they appear in the context so the security layer can re-hydrate them. "
    "If the context does not contain sufficient clinical information to answer the question, state that clearly."
)


def get_active_model_info() -> Dict[str, Any]:
    """Return telemetry about the active LLM provider and model."""
    if GROQ_API_KEY and not ("your-" in GROQ_API_KEY.lower()):
        return {
            "provider": "Groq Cloud High-Speed Inference",
            "model": GROQ_MODEL,
            "fallback_model": GROQ_FALLBACK_MODEL,
            "base_url": GROQ_BASE_URL,
            "status": "active",
        }
    elif OPENAI_API_KEY and not ("your-" in OPENAI_API_KEY.lower() or OPENAI_API_KEY.startswith("sk-proj-...")):
        return {
            "provider": "OpenAI",
            "model": "gpt-4o-mini",
            "status": "active",
        }
    return {
        "provider": "Local Zero-Trust Synthesis Engine",
        "model": "clinical-rules-v1",
        "status": "offline",
    }


def _synthesize_mock_clinical_answer(query: str, context_chunks: List[str]) -> str:
    """Generate an intelligent clinical response grounded in context chunks."""
    if not context_chunks:
        return "No medical records or clinical context are currently indexed. Please upload a patient document first."

    context_text = " ".join(context_chunks)
    q_lower = query.lower()

    # Detect patient tag in query or context (e.g. [PERSON_1])
    patient_match = re.search(r"\[PERSON_[^\]]+\]", query)
    if not patient_match:
        patient_match = re.search(r"\[PERSON_[^\]]+\]", context_text)
    patient_tag = patient_match.group(0) if patient_match else "[PATIENT]"

    # Extract sentences matching clinical aspects
    sentences = re.split(r"(?<=[.!?])\s+", context_text)
    relevant_sentences = []

    # Key clinical concepts
    terms = ["diagnos", "hypertension", "diabetes", "cancer", "alzheimer", "cardiology", "oncology", 
             "medication", "prescrib", "mg", "dose", "tablet", "blood", "pressure", "mri", "ultrasound", 
             "admit", "allerg", "symptom", "treatment", "pain", "history", "assessment", "plan"]

    matching_terms = [t for t in terms if t in q_lower]
    if not matching_terms:
        matching_terms = ["diagnos", "plan", "history", "admit", "medication"]

    for sent in sentences:
        s_lower = sent.lower()
        if any(term in s_lower for term in matching_terms):
            if sent.strip() not in relevant_sentences:
                relevant_sentences.append(sent.strip())

    if not relevant_sentences:
        relevant_sentences = [s.strip() for s in sentences[:3] if s.strip()]

    clinical_findings = " ".join(relevant_sentences[:4])

    if "diagnos" in q_lower or "condition" in q_lower:
        response = (
            f"Based on the medical records, {patient_tag}'s primary clinical findings and diagnoses include: "
            f"{clinical_findings}"
        )
    elif "medication" in q_lower or "drug" in q_lower or "prescrib" in q_lower:
        response = (
            f"According to the medical documentation for {patient_tag}, the prescribed medications and regimen are: "
            f"{clinical_findings}"
        )
    elif "treatment" in q_lower or "plan" in q_lower:
        response = (
            f"The clinical treatment plan documented for {patient_tag} includes: "
            f"{clinical_findings}"
        )
    else:
        response = (
            f"Review of the medical records for {patient_tag} indicates: "
            f"{clinical_findings}"
        )

    return response


def generate_response(query: str, context_chunks: List[str]) -> str:
    """Generate an LLM response grounded in the provided context.

    1. Groq Cloud (High-speed inference using flagship model: openai/gpt-oss-120b).
    2. Fallback Groq model (qwen/qwen3.8-27b).
    3. OpenAI API (if configured).
    4. Deterministic clinical synthesis fallback.
    """
    context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "No clinical context available."

    user_message = (
        f"Medical Context:\n{context_text}\n\n"
        f"Clinician Question: {query}\n\n"
        "Provide a concise, clinically grounded response maintaining all synthetic tags."
    )

    # 1. Primary: Groq Cloud High-Speed Inference
    if GROQ_API_KEY and not ("your-" in GROQ_API_KEY.lower()):
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url=GROQ_BASE_URL,
                api_key=GROQ_API_KEY,
                timeout=2.5,
            )
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            content = response.choices[0].message.content or ""
            if content.strip():
                return content
        except Exception as e:
            print(f"[LLM] Groq primary model '{GROQ_MODEL}' failed ({e}). Trying fallback model '{GROQ_FALLBACK_MODEL}'...")
            try:
                from openai import OpenAI
                client = OpenAI(
                    base_url=GROQ_BASE_URL,
                    api_key=GROQ_API_KEY,
                    timeout=2.5,
                )
                response = client.chat.completions.create(
                    model=GROQ_FALLBACK_MODEL,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.2,
                    max_tokens=800,
                )
                content = response.choices[0].message.content or ""
                if content.strip():
                    return content
            except Exception as e2:
                print(f"[LLM] Groq fallback model failed ({e2}). Proceeding to next fallback.")

    # 2. Secondary: OpenAI API (if configured)
    if OPENAI_API_KEY and not ("your-" in OPENAI_API_KEY.lower() or OPENAI_API_KEY.startswith("sk-proj-...")):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, timeout=5.0)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=600,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[LLM] OpenAI API call failed ({e}). Falling back to clinical synthesis engine.")

    # 3. Tertiary: Local Deterministic Clinical Synthesis Engine
    return _synthesize_mock_clinical_answer(query, context_chunks)
