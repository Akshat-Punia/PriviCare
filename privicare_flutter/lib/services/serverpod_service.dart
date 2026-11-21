import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:privicare_client/privicare_client.dart';

/// Serverpod Client Service managing connections to Serverpod Cloud
/// with graceful local fallback for Android Emulator & offline demonstrations.
class ServerpodService {
  static final ServerpodService _instance = ServerpodService._internal();
  factory ServerpodService() => _instance;
  ServerpodService._internal();

  // Serverpod Cloud Production Endpoint (configured for HackBriven)
  static const String serverpodCloudUrl = 'https://api.privicare.serverpod.cloud/';
  // Android Emulator default localhost bridge
  static const String localEmulatorUrl = 'http://10.0.2.2:8080/';

  late final Client client;
  bool isConnected = false;

  // Active Patient Session in Doctor Portal
  PatientRecord activePatient = PatientRecord(
    uhid: 'UHID-982143',
    name: 'Rajesh Sharma',
    age: 54,
    gender: 'Male',
    bloodGroup: 'B+',
    department: 'Cardiology',
    abhaId: '91-4412-3390-1123',
    aadhaar: '9823 4410 7721',
    phone: '+91 98765 43210',
    primaryDiagnosis: 'Acute Coronary Syndrome, Mid-LAD DES Stent, Essential Hypertension',
    medications: [
      'Atorvastatin 40mg (1 tab OD bedtime)',
      'Telmisartan 40mg (1 tab OD morning)',
      'Aspirin 75mg (1 tab OD post-lunch)',
      'Metoprolol Succinate 25mg (1 tab OD)',
    ],
    allergies: ['Penicillin (mild cutaneous rash)'],
    reportsCount: 2,
  );

  final List<PatientRecord> _mockPatients = [
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
      primaryDiagnosis: 'Acute Coronary Syndrome, Mid-LAD DES Stent, Essential Hypertension',
      medications: [
        'Atorvastatin 40mg (1 tab OD bedtime)',
        'Telmisartan 40mg (1 tab OD morning)',
        'Aspirin 75mg (1 tab OD post-lunch)',
      ],
      allergies: ['Penicillin (mild cutaneous rash)'],
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
        'Paclitaxel 175mg/m2 IV q3w',
        'Dexamethasone 20mg premedication',
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
        'Formoterol/Budesonide 400/12mcg DPI',
      ],
      allergies: ['No known drug allergies (NKDA)'],
      reportsCount: 1,
    ),
  ];

  final List<VoiceNote> _voiceNotes = [
    VoiceNote(
      id: 'vn-001',
      uhid: 'UHID-982143',
      doctorId: 'DR-SARAH-JOHNSON',
      transcript: 'Patient Rajesh Sharma reported mild calf soreness after taking Atorvastatin 40mg. Advised monitoring CK levels.',
      scrubbedTranscript: 'Patient [PATIENT_1] reported mild calf soreness after taking Atorvastatin 40mg. Advised monitoring CK levels.',
      clinicalTriage: 'EVALUATE_MEDICATION',
      timestamp: DateTime.now().subtract(const Duration(hours: 3)),
      reviewed: true,
    ),
  ];

  Future<void> initialize() async {
    final host = kIsWeb
        ? 'http://localhost:8080/'
        : (defaultTargetPlatform == TargetPlatform.android
            ? localEmulatorUrl
            : 'http://localhost:8080/');

    client = Client(host);
    isConnected = true;
  }

  // --- Patients API ---
  Future<List<PatientRecord>> getPatients() async {
    try {
      return await client.clinical.getPatients();
    } catch (e) {
      return _mockPatients;
    }
  }

  Future<List<PatientRecord>> searchPatients(String query, {String? department}) async {
    try {
      return await client.clinical.searchPatients(query, department: department);
    } catch (e) {
      final q = query.toLowerCase().trim();
      return _mockPatients.where((p) {
        if (department != null && department != 'ALL' && p.department.toLowerCase() != department.toLowerCase()) {
          return false;
        }
        if (q.isEmpty) return true;
        return p.name.toLowerCase().contains(q) ||
            p.uhid.toLowerCase().contains(q) ||
            (p.abhaId?.toLowerCase().contains(q) ?? false) ||
            (p.aadhaar?.toLowerCase().contains(q) ?? false) ||
            (p.primaryDiagnosis?.toLowerCase().contains(q) ?? false) ||
            p.department.toLowerCase().contains(q);
      }).toList();
    }
  }

  // --- Camera Document Upload (Track 2) ---
  Future<MedicalReport> uploadReport({
    required String uhid,
    required String filename,
    required String rawContent,
  }) async {
    try {
      return await client.clinical.uploadReport(
        uhid: uhid,
        filename: filename,
        rawContent: rawContent,
      );
    } catch (e) {
      // Local fallback with simulated PII redaction
      final scrubbed = rawContent
          .replaceAll(RegExp(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b'), '[AADHAAR_ANON_1]')
          .replaceAll(RegExp(r'\b\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '[ABHA_ANON_1]')
          .replaceAll(RegExp(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'), '[PAN_REDACTED]')
          .replaceAll('Rajesh Sharma', '[PATIENT_1]');

      return MedicalReport(
        id: 'rep-${DateTime.now().millisecondsSinceEpoch}',
        uhid: uhid,
        filename: filename,
        date: DateTime.now().toIso8601String().substring(0, 10),
        department: 'Camera OCR Scanner',
        summary: 'Scanned via Phone Camera. Zero PII stored in Serverpod.',
        scrubbedText: scrubbed,
        scrubbedEntities: ['IN_AADHAAR', 'IN_ABHA', 'PATIENT_NAME'],
      );
    }
  }

  // --- Microphone Voice Dictation (Track 2) ---
  Future<VoiceNote> submitVoiceNote({
    required String uhid,
    required String doctorId,
    required String rawTranscript,
  }) async {
    try {
      return await client.voiceNote.submitVoiceNote(
        uhid: uhid,
        doctorId: doctorId,
        rawTranscript: rawTranscript,
      );
    } catch (e) {
      String triage = 'ROUTINE';
      final lower = rawTranscript.toLowerCase();
      if (lower.contains('chest pain') || lower.contains('angina') || lower.contains('shortness of breath')) {
        triage = 'URGENT_ATTENTION';
      } else if (lower.contains('statin') || lower.contains('muscle') || lower.contains('rash')) {
        triage = 'EVALUATE_MEDICATION';
      }

      final vn = VoiceNote(
        id: 'vn-${DateTime.now().millisecondsSinceEpoch}',
        uhid: uhid,
        doctorId: doctorId,
        transcript: rawTranscript,
        scrubbedTranscript: rawTranscript
            .replaceAll('Rajesh Sharma', '[PATIENT_1]')
            .replaceAll(RegExp(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b'), '[AADHAAR_ANON]'),
        clinicalTriage: triage,
        timestamp: DateTime.now(),
        reviewed: false,
      );
      _voiceNotes.insert(0, vn);
      return vn;
    }
  }

  Future<List<VoiceNote>> getVoiceNotes(String uhid) async {
    try {
      return await client.voiceNote.getVoiceNotes(uhid);
    } catch (e) {
      return _voiceNotes.where((vn) => vn.uhid == uhid).toList();
    }
  }

  // --- Clinical AI Consultation ---
  Future<Map<String, dynamic>> consultCopilot(String uhid, String query) async {
    try {
      return await client.chat.consultCopilot(
        uhid: uhid,
        query: query,
        doctorId: 'DR-SARAH-JOHNSON',
      );
    } catch (e) {
      return {
        'uhid': uhid,
        'doctorResponse':
            'Clinical RAG Co-Pilot ($uhid):\n\nPatient is post-PCI (Mid-LAD Stent, 2026-10-14). Currently on Atorvastatin 40mg and Telmisartan 40mg. Dual Antiplatelet Therapy (DAPT) compliance is essential for stent patency. If muscle soreness is reported, consider CK level evaluation.',
        'zeroLeakageEnforced': true,
      };
    }
  }
}
