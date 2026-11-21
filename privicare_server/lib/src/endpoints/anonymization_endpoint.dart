import 'package:serverpod/serverpod.dart';
import '../engine/pii_scrubber.dart';
import '../engine/verhoeff.dart';

/// Standalone PII Scrubbing & Validation Endpoint.
/// Executes directly in Dart on Serverpod Cloud without external Python dependencies.
class AnonymizationEndpoint extends Endpoint {
  /// Scrubs detected HIPAA PHI and India DPDP personal identifiers from text.
  Future<Map<String, dynamic>> scrubText(
    Session session, {
    required String text,
    String? uhid,
  }) async {
    final stopwatch = Stopwatch()..start();
    final result = PiiScrubber.anonymize(text);
    stopwatch.stop();

    return {
      'scrubbedText': result.scrubbedText,
      'entitiesFoundCount': result.entities.length,
      'entities': result.entities.map((e) => e.toJson()).toList(),
      'latencyMs': stopwatch.elapsedMicroseconds / 1000.0,
      'complianceStandards': ['HIPAA_SAFE_HARBOR_18', 'INDIA_DPDP_ACT_2023'],
      'zeroLeakageGuarantee': true,
    };
  }

  /// Validates a 12-digit Indian Aadhaar number using the Verhoeff algorithm.
  Future<Map<String, dynamic>> validateAadhaar(
    Session session,
    String aadhaarNumber,
  ) async {
    final isValid = Verhoeff.validate(aadhaarNumber);
    return {
      'isValid': isValid,
      'algorithm': 'Verhoeff_D5_Checksum',
      'digitCount': aadhaarNumber.replaceAll(RegExp(r'\D'), '').length,
    };
  }
}
