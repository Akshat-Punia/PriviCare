import 'package:serverpod/serverpod.dart';
import '../models/models.dart';
import '../engine/pii_scrubber.dart';
import '../engine/pii_vault.dart';

/// Clinical Intelligence Endpoint providing patient management, report archiving,
/// and DPDP Act Section 12 Cryptographic Shredding.
class ClinicalEndpoint extends Endpoint {
  static final List<PatientRecord> _patients = [
    PatientRecord(
      uhid: 'UHID-982143',
      name: 'Rajesh Sharma',
      age: 54,
      gender: 'Male',
      bloodGroup: 'B+',
      department: 'Cardiology',
      abhaId: '91-4412-3390-1123',
      aadhaar: '9823 4410 7721',
      phone: '+91 98765 43210',
      primaryDiagnosis: 'Acute Coronary Syndrome, Mid-LAD Stent, Essential Hypertension',
      medications: [
        'Atorvastatin 40mg (1 tab OD bedtime)',
        'Telmisartan 40mg (1 tab OD morning)',
        'Aspirin 75mg (1 tab OD post-lunch)',
        'Metoprolol Succinate 25mg (1 tab OD)',
      ],
      allergies: ['Penicillin (cutaneous rash)'],
      reportsCount: 2,
    ),
    PatientRecord(
      uhid: 'UHID-447219',
      name: 'Priya Patel',
      age: 46,
      gender: 'Female',
      bloodGroup: 'O+',
      department: 'Oncology',
      abhaId: '91-8823-1104-5590',
      aadhaar: '4412 8890 2231',
      phone: '+91 98112 34567',
      primaryDiagnosis: 'Infiltrating Ductal Carcinoma (Grade II), ER/PR+, Post-Paclitaxel',
      medications: [
        'Paclitaxel 175mg/m2 IV q3w (Cycle 3/6)',
        'Dexamethasone 20mg premedication',
        'Ondansetron 8mg PO BID',
      ],
      allergies: ['Sulfa drugs (bronchospasm)'],
      reportsCount: 2,
    ),
    PatientRecord(
      uhid: 'UHID-551029',
      name: 'Amit Kumar',
      age: 62,
      gender: 'Male',
      bloodGroup: 'A+',
      department: 'Pulmonology',
      abhaId: '91-3310-7744-8891',
      aadhaar: '7721 3340 9912',
      phone: '+91 98223 45678',
      primaryDiagnosis: 'Severe COPD Exacerbation, Chronic Bronchitis, Type 2 Respiratory Failure',
      medications: [
        'Tiotropium Respimat 2.5mcg (2 puffs OD)',
        'Formoterol/Budesonide 400/12mcg DPI BID',
      ],
      allergies: ['No known drug allergies (NKDA)'],
      reportsCount: 1,
    ),
  ];

  static final List<MedicalReport> _reports = [
    MedicalReport(
      id: 'rep-001',
      uhid: 'UHID-982143',
      filename: 'Discharge_Summary_Fortis_Escorts.pdf',
      date: '2026-10-14',
      department: 'Cardiology',
      summary: 'Patient presented with typical angina. 90% stenosis in mid-LAD. Successful DES deployed. Post-procedure LVEF 52%.',
      scrubbedText: 'DISCHARGE SUMMARY\nPatient: [PATIENT_1] | UHID: [MRN_REDACTED] | Aadhaar: [AADHAAR_ANON_1]\nDiagnosis: Acute Coronary Syndrome. Mid-LAD 90% lesion stented.\nDischarge vitals stable: BP 128/82, HR 68 bpm.',
      scrubbedEntities: ['PERSON: Rajesh Sharma', 'AADHAAR: 9823 4410 7721', 'PHONE: +91 98765 43210'],
    ),
    MedicalReport(
      id: 'rep-002',
      uhid: 'UHID-447219',
      filename: 'Histopathology_Biopsy_AIIMS.pdf',
      date: '2026-10-28',
      department: 'Oncology',
      summary: 'Core needle biopsy right breast mass. Invasive Ductal Carcinoma Grade II. ER 85%, PR 70%, HER2 Negative.',
      scrubbedText: 'AIIMS HISTOPATHOLOGY\nPatient: [PATIENT_1] | ABHA: [ABHA_ANON_1]\nInfiltrating Ductal Carcinoma, Grade II. ER/PR Positive, HER2-neu Negative.',
      scrubbedEntities: ['PERSON: Priya Patel', 'ABHA: 91-8823-1104-5590'],
    ),
  ];

  /// Returns list of all enrolled patients.
  Future<List<PatientRecord>> getPatients(Session session) async {
    return _patients;
  }

  /// Real-time patient search filtering across multiple clinical and identity fields.
  Future<List<PatientRecord>> searchPatients(
    Session session, {
    required String query,
    String? department,
  }) async {
    final q = query.toLowerCase().trim();
    return _patients.where((p) {
      if (department != null &&
          department != 'ALL' &&
          p.department.toLowerCase() != department.toLowerCase()) {
        return false;
      }
      if (q.isEmpty) return true;

      return p.name.toLowerCase().contains(q) ||
          p.uhid.toLowerCase().contains(q) ||
          (p.abhaId?.toLowerCase().contains(q) ?? false) ||
          (p.aadhaar?.toLowerCase().contains(q) ?? false) ||
          (p.phone?.toLowerCase().contains(q) ?? false) ||
          (p.primaryDiagnosis?.toLowerCase().contains(q) ?? false) ||
          p.department.toLowerCase().contains(q);
    }).toList();
  }

  /// Retrieves full medical archive for a specific patient.
  Future<List<MedicalReport>> getPatientReports(
    Session session,
    String uhid,
  ) async {
    return _reports.where((r) => r.uhid == uhid).toList();
  }

  /// Ingests a new medical report (e.g. from Phone Camera OCR),
  /// executes PII scrubbing, vaults sensitive mappings, and saves the sanitized report.
  Future<MedicalReport> uploadReport(
    Session session, {
    required String uhid,
    required String filename,
    required String rawContent,
  }) async {
    // 1. Scrub PII (HIPAA Safe Harbor + India DPDP Act)
    final scrubResult = PiiScrubber.anonymize(rawContent);

    // 2. Vault mapping under user security context
    PiiVault.storeMapping(uhid, scrubResult.mapping);

    // 3. Create sanitized medical report
    final report = MedicalReport(
      id: 'rep-${DateTime.now().millisecondsSinceEpoch}',
      uhid: uhid,
      filename: filename,
      date: DateTime.now().toIso8601String().substring(0, 10),
      department: 'Clinical Ingestion',
      summary: 'Scanned document processed via Camera OCR & Dual Presidio scrubbing engine.',
      scrubbedText: scrubResult.scrubbedText,
      scrubbedEntities: scrubResult.entities.map((e) => '${e.entityType}: ${e.rawValue}').toList(),
    );

    _reports.insert(0, report);
    return report;
  }

  /// DPDP Act 2023 Section 12 Cryptographic Erasure:
  /// Shreds the patient's vault key and renders stored vector embeddings permanently un-linkable.
  Future<Map<String, dynamic>> cryptoShred(
    Session session,
    String uhid,
  ) async {
    return PiiVault.cryptoShred(uhid);
  }
}
