import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import health_check
from routes.privacy import switch_role, SwitchRoleRequest, generate_erasure_report, ErasureRequest, vector_storage_xray, get_benchmark_results
from routes.chat import chat, ChatRequest
from routes.clinical import list_patients, get_patient, doctor_consult, DoctorConsultRequest

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

print("\n>>> ALL 11 INTEGRATION TESTS PASSED PERFECTLY! <<<", flush=True)
