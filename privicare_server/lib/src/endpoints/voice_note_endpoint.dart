import 'package:serverpod/serverpod.dart';
import '../models/models.dart';
import '../engine/pii_scrubber.dart';
import '../engine/pii_vault.dart';

/// Voice Note Endpoint — Track 2: Superpowers in Your Pocket.
/// Integrates phone microphone dictation (with Gnani / speech recognition integration)
/// and Serverpod-backed PII scrubbing and automated clinical triage.
class VoiceNoteEndpoint extends Endpoint {
  static final List<VoiceNote> _voiceNotes = [
    VoiceNote(
      id: 'vn-001',
      uhid: 'UHID-982143',
      doctorId: 'DR-SARAH-JOHNSON',
      transcript: 'Patient Rajesh Sharma reported mild calf soreness after taking Atorvastatin 40mg. Advised monitoring CK levels and hydration.',
      scrubbedTranscript: 'Patient [PATIENT_1] reported mild calf soreness after taking Atorvastatin 40mg. Advised monitoring CK levels and hydration.',
      clinicalTriage: 'EVALUATE_MEDICATION',
      timestamp: DateTime.now().subtract(const Duration(hours: 4)),
      reviewed: true,
    ),
  ];

  /// Retrieves voice notes recorded for a patient.
  Future<List<VoiceNote>> getVoiceNotes(
    Session session,
    String uhid,
  ) async {
    return _voiceNotes.where((vn) => vn.uhid == uhid).toList();
  }

  /// Ingests a doctor voice note recorded via phone microphone,
  /// executes PII scrubbing, detects clinical triage flags, and attaches to record.
  Future<VoiceNote> submitVoiceNote(
    Session session, {
    required String uhid,
    required String doctorId,
    required String rawTranscript,
  }) async {
    // 1. Scrub PII from audio transcript
    final scrubResult = PiiScrubber.anonymize(rawTranscript);

    // 2. Vault mapping under patient UHID
    PiiVault.storeMapping(uhid, scrubResult.mapping);

    // 3. Clinical Symptom Triage Analysis
    String triage = 'ROUTINE';
    final lower = rawTranscript.toLowerCase();
    if (lower.contains('chest pain') ||
        lower.contains('angina') ||
        lower.contains('shortness of breath') ||
        lower.contains('neuropathy') ||
        lower.contains('numbness') ||
        lower.contains('bleeding')) {
      triage = 'URGENT_ATTENTION';
    } else if (lower.contains('statin') ||
        lower.contains('muscle pain') ||
        lower.contains('myalgia') ||
        lower.contains('rash') ||
        lower.contains('allergy')) {
      triage = 'EVALUATE_MEDICATION';
    }

    final voiceNote = VoiceNote(
      id: 'vn-${DateTime.now().millisecondsSinceEpoch}',
      uhid: uhid,
      doctorId: doctorId,
      transcript: rawTranscript,
      scrubbedTranscript: scrubResult.scrubbedText,
      clinicalTriage: triage,
      timestamp: DateTime.now(),
      reviewed: false,
    );

    _voiceNotes.insert(0, voiceNote);
    return voiceNote;
  }
}
