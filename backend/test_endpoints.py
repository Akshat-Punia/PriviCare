import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import health_check
from routes.privacy import switch_role, SwitchRoleRequest, generate_erasure_report, ErasureRequest, vector_storage_xray, get_benchmark_results
from routes.chat import chat, ChatRequest
from routes.clinical import (
    list_patients,
    get_patient,
    doctor_consult,
    DoctorConsultRequest,
    validate_identity,
    ValidateIdentityRequest,
    patient_chat_endpoint,
    PatientChatRequest,
    crypto_shred_patient_endpoint,
    get_user_dashboard,
    update_user_consent,
    UpdateConsentRequest,
    check_interactions_endpoint,
    CheckInteractionsRequest,
    generate_summary_endpoint,
    GenerateSummaryRequest,
    get_fhir_bundle_endpoint,
    get_vitals_endpoint,
    record_vitals_endpoint,
    RecordVitalsRequest,
    download_patient_audit_log,
    download_patient_fhir_bundle,
)

print("[TEST 1] health_check", flush=True)
res1 = health_check()
print("Result:", res1, flush=True)
assert res1["status"] == "healthy"

print("\n[TEST 2] get_benchmark_results", flush=True)
res2 = get_benchmark_results()
print("Metrics:", res2.get("metrics"), flush=True)
assert res2["metrics"]["recall"] == 98.38

print("\n[TEST 3] vector_storage_xray", flush=True)
res3 = vector_storage_xray()
print("Raw PII in Storage:", res3["raw_pii_detected_in_storage"], "Engine:", res3["storage_engine"], flush=True)
assert res3["raw_pii_detected_in_storage"] == 0

print("\n[TEST 4] switch_role (Doctor)", flush=True)
res4 = switch_role(SwitchRoleRequest(role="doctor", hospital_id="HOSP_01"))
print("Role:", res4["role"], "Mode:", res4["mode"], flush=True)
assert res4["can_reidentify"] is True

print("\n[TEST 5] switch_role (Researcher - Zero Re-ID)", flush=True)
res5 = switch_role(SwitchRoleRequest(role="researcher", hospital_id="HOSP_01"))
print("Role:", res5["role"], "Can Re-ID:", res5["can_reidentify"], flush=True)
assert res5["can_reidentify"] is False

print("\n[TEST 6] generate_erasure_report (DPDP Section 12)", flush=True)
res6 = generate_erasure_report(ErasureRequest(
    hospital_id="HOSP_01",
    patient_identifier="Rajesh Sharma",
    requested_by="Data Protection Officer"
))
print("Legal Basis:", res6["legal_classification"], flush=True)
print("Certificate ID:", res6["certificate_id"], flush=True)
assert "Section 12" in res6["legal_classification"]

print("\n[TEST 7] chat (Doctor Role - Re-identification Allowed)", flush=True)
res7 = chat(ChatRequest(
    message="What is Rajesh Sharma diagnosed with?",
    user_id="doctor@hospital.org",
    role="doctor"
))
print("Anonymized Query:", res7["anonymized_query"], flush=True)
print("Answer Preview:", res7["answer"][:80], flush=True)
print("ABAC Status:", res7["security_audit"]["abac_status"], flush=True)
assert res7["security_audit"]["abac_status"] == "AUTHORIZED"

print("\n[TEST 8] chat (Researcher Role - Fails Closed)", flush=True)
res8 = chat(ChatRequest(
    message="What is Rajesh Sharma diagnosed with?",
    user_id="researcher@hospital.org",
    role="researcher"
))
print("ABAC Status:", res8["security_audit"]["abac_status"], flush=True)
print("Re-identified:", res8["security_audit"]["re_identified"], flush=True)
assert res8["security_audit"]["re_identified"] is False

print("\n[TEST 9] list_patients (PriviCare Doctor Portal)", flush=True)
patients = list_patients()
print(f"Enrolled Patients: {len(patients)}", [p["name"] for p in patients], flush=True)
assert len(patients) >= 3

print("\n[TEST 10] get_patient (UHID-982143 History & Reports)", flush=True)
p_detail = get_patient("UHID-982143")
print(f"Patient: {p_detail['name']} | Reports: {len(p_detail['reports'])} | Prior Chats: {len(p_detail['patient_chat_history'])}", flush=True)
assert p_detail["uhid"] == "UHID-982143"
assert len(p_detail["reports"]) >= 2
assert len(p_detail["patient_chat_history"]) >= 3

print("\n[TEST 11] doctor_consult (RAG Co-Pilot over Patient Records)", flush=True)
consult_res = doctor_consult(DoctorConsultRequest(
    uhid="UHID-982143",
    message="Summarize coronary findings and medication regimen.",
    doctor_id="DR-SARAH-JOHNSON"
))
print("Doctor Consult Answer Preview:", consult_res["answer"][:80], flush=True)
assert consult_res["status"] == "success"
assert consult_res["security_audit"]["abac_status"] == "AUTHORIZED"

print("\n[TEST 12] validate_identity (Verhoeff D5 Checksum & ABDM ABHA)", flush=True)
v_aadhaar = validate_identity(ValidateIdentityRequest(type="aadhaar", value="3675 8492 1039"))
print("Aadhaar Verhoeff Valid:", v_aadhaar["valid"], "| Algorithm:", v_aadhaar["algorithm"], flush=True)
assert v_aadhaar["valid"] is True
v_bad = validate_identity(ValidateIdentityRequest(type="aadhaar", value="3675 8492 1038"))
print("Invalid Aadhaar Rejected:", not v_bad["valid"], "| Reason:", v_bad["reason"], flush=True)
assert v_bad["valid"] is False
v_abha = validate_identity(ValidateIdentityRequest(type="abha", value="14-2354-9871-6542"))
assert v_abha["valid"] is True
v_phone = validate_identity(ValidateIdentityRequest(type="phone", value="+91 98765 43210"))
assert v_phone["valid"] is True

print("\n[TEST 13] patient_chat (Patient 24/7 Recovery AI & Triage Sync)", flush=True)
p_chat = patient_chat_endpoint(PatientChatRequest(
    uhid="UHID-982143",
    message="Is mild calf soreness normal with Atorvastatin 40mg?"
))
print("Clinical Triage:", p_chat["clinical_triage"], "| Synced to Doctor:", p_chat["synced_to_doctor"], flush=True)
assert p_chat["clinical_triage"] == "EVALUATE_MEDICATION"
assert p_chat["status"] == "success"

print("\n[TEST 14] crypto_shred (DPDP Act 2023 Section 12 Right to Erasure)", flush=True)
shred_res = crypto_shred_patient_endpoint("UHID-982143")
print("Erasure Status:", shred_res["status"], "| Section:", shred_res["section"], flush=True)
assert shred_res["status"] == "shredded"

print("\n[TEST 15] get_user_dashboard (User & Patient Digital Health Card)", flush=True)
u_dash = get_user_dashboard("UHID-982143")
print("User Name:", u_dash["user"]["name"], "| ABHA:", u_dash["user"]["abha_id"], "| Masked Aadhaar:", u_dash["user"]["aadhaar_masked"], flush=True)
print("Consents Active:", len(u_dash["consents"]), "| Audit Trail Entries:", len(u_dash["audit_trail"]), flush=True)
assert u_dash["status"] == "success"
assert u_dash["user"]["uhid"] == "UHID-982143"
assert len(u_dash["consents"]) >= 3
assert len(u_dash["prescriptions"]) >= 3

print("\n[TEST 16] update_user_consent (DPDP Consent Revocation / Grant)", flush=True)
c_update = update_user_consent(UpdateConsentRequest(
    uhid="UHID-982143",
    hospital_name="AIIMS New Delhi Network",
    department="Tele-Consultation",
    consent_granted=False,
    purpose="Secondary Opinion & Zero-Leak Vector RAG"
))
print("Consent Updated:", c_update["message"], "| Granted:", c_update["consent"]["granted"], flush=True)
assert c_update["status"] == "success"
assert c_update["consent"]["granted"] is False

print("\n[TEST 17] check_interactions (Drug-Drug & Drug-Food Interaction Engine)", flush=True)
inter_res = check_interactions_endpoint(CheckInteractionsRequest(
    medications=["Atorvastatin 40mg", "Aspirin 75mg", "Ibuprofen 400mg"],
    dietary_items=["Grapefruit juice", "Low sodium salt"]
))
print("Interactions Detected:", inter_res["interactions_found_count"], "| Safety:", inter_res["safety_evaluation"], flush=True)
assert inter_res["interactions_found_count"] >= 2
assert inter_res["safety_evaluation"] == "HIGH_RISK"

print("\n[TEST 18] check_interactions (Drug-Allergy Sensitivity Screening)", flush=True)
allergy_res = check_interactions_endpoint(CheckInteractionsRequest(
    medications=["Amoxicillin 500mg", "Telmisartan 40mg"],
    allergies=["Penicillin (anaphylaxis)"]
))
print("Allergy Conflicts:", allergy_res["allergy_conflicts_count"], flush=True)
assert allergy_res["allergy_conflicts_count"] >= 1
assert allergy_res["safety_evaluation"] == "HIGH_RISK"

print("\n[TEST 19] generate_summary (Automated SOAP Note & Discharge Summary)", flush=True)
soap_res = generate_summary_endpoint("UHID-982143", GenerateSummaryRequest(re_identify=True))
print("SOAP Generated for:", soap_res["patient_name"], "| Standards:", soap_res["standards"], flush=True)
assert soap_res["status"] == "success"
assert "[S] SUBJECTIVE" in soap_res["summary_markdown"]
assert "[P] PLAN" in soap_res["summary_markdown"]

print("\n[TEST 20] get_fhir_bundle (HL7 FHIR R4 Ayushman Bharat Interoperability Bundle)", flush=True)
fhir_res = get_fhir_bundle_endpoint("UHID-982143")
print("FHIR Bundle Type:", fhir_res["resourceType"], "| Total Resources:", fhir_res["total"], flush=True)
assert fhir_res["resourceType"] == "Bundle"
assert fhir_res["total"] >= 4

print("\n[TEST 21] vitals_telemetry (Cardiac Vitals Logging & Anomaly Detection)", flush=True)
vitals_before = get_vitals_endpoint("UHID-982143")
print("Existing Vitals Entries:", len(vitals_before), flush=True)
assert len(vitals_before) >= 1

new_vital = record_vitals_endpoint("UHID-982143", RecordVitalsRequest(
    systolic_bp=146,
    diastolic_bp=94,
    heart_rate=104,
    spo2=94
))
print("New Vital Logged Status:", new_vital["vital_entry"]["status"], "| Alerts:", new_vital["vital_entry"]["alerts"], flush=True)
assert new_vital["status"] == "success"
assert new_vital["vital_entry"]["status"] == "URGENT" or new_vital["vital_entry"]["status"] == "WARNING"
assert len(new_vital["vital_entry"]["alerts"]) >= 2

print("\n[TEST 22] download_patient_audit_log (DPDP Act 2023 SHA-256 Tamper-Proof Ledger)", flush=True)
audit_download = download_patient_audit_log("UHID-982143")
assert audit_download.status_code == 200
assert "attachment; filename=PriviCare_DPDP_Audit_Log_UHID-982143.json" in audit_download.headers["Content-Disposition"]
import json
audit_json = json.loads(audit_download.body.decode("utf-8"))
print("Integrity Hash:", audit_json["integrity_hash"][:16], "... | Events:", len(audit_json["audit_trail_events"]), flush=True)
assert len(audit_json["integrity_hash"]) == 64
assert len(audit_json["audit_trail_events"]) >= 3

print("\n[TEST 23] download_patient_fhir_bundle (HL7 FHIR R4 Ayushman Bharat Download)", flush=True)
fhir_download = download_patient_fhir_bundle("UHID-982143")
assert fhir_download.status_code == 200
assert "attachment; filename=FHIR_R4_Bundle_UHID-982143.json" in fhir_download.headers["Content-Disposition"]
fhir_dl_json = json.loads(fhir_download.body.decode("utf-8"))
print("FHIR Bundle Downloaded Total Resources:", fhir_dl_json["total"], flush=True)
assert fhir_dl_json["total"] >= 4

print("\n>>> ALL 23 INTEGRATION TESTS PASSED PERFECTLY! <<<", flush=True)
