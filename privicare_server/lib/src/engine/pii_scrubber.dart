import 'verhoeff.dart';

class DetectedEntity {
  final String entityType;
  final String rawValue;
  final int start;
  final int end;
  final double confidence;

  DetectedEntity({
    required this.entityType,
    required this.rawValue,
    required this.start,
    required this.end,
    this.confidence = 0.95,
  });

  Map<String, dynamic> toJson() => {
        'entityType': entityType,
        'rawValue': rawValue,
        'start': start,
        'end': end,
        'confidence': confidence,
      };
}

/// Dual-Compliance PII & PHI Scrubber (HIPAA Safe Harbor + India DPDP Act 2023)
/// Engineered to execute natively inside Serverpod on Serverpod Cloud.
class PiiScrubber {
  // Regex Patterns for Indian Identifiers & HIPAA
  static final RegExp _aadhaarRegex = RegExp(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b');
  static final RegExp _abhaRegex = RegExp(r'\b\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b');
  static final RegExp _panRegex = RegExp(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b');
  static final RegExp _phoneRegex = RegExp(r'(?:\+?91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b');
  static final RegExp _emailRegex = RegExp(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b');
  static final RegExp _uhidRegex = RegExp(r'\b(?:UHID|MRN|PATIENT-ID)[-:\s]*([A-Z0-9\-]+)\b', caseSensitive: false);
  static final RegExp _doctorNameRegex = RegExp(r'\b(?:Dr\.|Doctor|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b');
  static final RegExp _patientNameRegex = RegExp(r'\b(?:Patient|Name|Pt\.?):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', caseSensitive: false);

  /// Analyzes text and returns all detected PII entities.
  static List<DetectedEntity> detectEntities(String text) {
    final List<DetectedEntity> entities = [];

    // 1. Aadhaar with Verhoeff Checksum
    for (final match in _aadhaarRegex.allMatches(text)) {
      final raw = match.group(0)!;
      if (Verhoeff.validate(raw)) {
        entities.add(DetectedEntity(
          entityType: 'IN_AADHAAR',
          rawValue: raw,
          start: match.start,
          end: match.end,
          confidence: 0.99,
        ));
      }
    }

    // 2. ABDM ABHA ID (14 digits)
    for (final match in _abhaRegex.allMatches(text)) {
      final raw = match.group(0)!;
      final digits = raw.replaceAll(RegExp(r'\D'), '');
      if (digits.length == 14) {
        entities.add(DetectedEntity(
          entityType: 'IN_ABHA',
          rawValue: raw,
          start: match.start,
          end: match.end,
          confidence: 0.98,
        ));
      }
    }

    // 3. Indian PAN
    for (final match in _panRegex.allMatches(text)) {
      entities.add(DetectedEntity(
        entityType: 'IN_PAN',
        rawValue: match.group(0)!,
        start: match.start,
        end: match.end,
        confidence: 0.95,
      ));
    }

    // 4. Phone Numbers
    for (final match in _phoneRegex.allMatches(text)) {
      entities.add(DetectedEntity(
        entityType: 'PHONE_NUMBER',
        rawValue: match.group(0)!,
        start: match.start,
        end: match.end,
        confidence: 0.92,
      ));
    }

    // 5. Emails
    for (final match in _emailRegex.allMatches(text)) {
      entities.add(DetectedEntity(
        entityType: 'EMAIL_ADDRESS',
        rawValue: match.group(0)!,
        start: match.start,
        end: match.end,
        confidence: 0.99,
      ));
    }

    // 6. UHID / Hospital MRN
    for (final match in _uhidRegex.allMatches(text)) {
      entities.add(DetectedEntity(
        entityType: 'MEDICAL_RECORD_NUMBER',
        rawValue: match.group(0)!,
        start: match.start,
        end: match.end,
        confidence: 0.95,
      ));
    }

    // 7. Doctor Names
    for (final match in _doctorNameRegex.allMatches(text)) {
      entities.add(DetectedEntity(
        entityType: 'DOCTOR_NAME',
        rawValue: match.group(0)!,
        start: match.start,
        end: match.end,
        confidence: 0.90,
      ));
    }

    // 8. Patient Names
    for (final match in _patientNameRegex.allMatches(text)) {
      entities.add(DetectedEntity(
        entityType: 'PATIENT_NAME',
        rawValue: match.group(0)!,
        start: match.start,
        end: match.end,
        confidence: 0.90,
      ));
    }

    // Sort by start index ascending
    entities.sort((a, b) => a.start.compareTo(b.start));
    return entities;
  }

  /// Scrubs detected PII from raw text and returns anonymized string with replacement mapping.
  static ScrubResult anonymize(String text, {Map<String, String>? pseudonymMap}) {
    final entities = detectEntities(text);
    if (entities.isEmpty) {
      return ScrubResult(scrubbedText: text, entities: [], mapping: {});
    }

    final mapping = pseudonymMap ?? <String, String>{};
    final buffer = StringBuffer();
    int lastEnd = 0;

    int aadhaarIndex = 1;
    int abhaIndex = 1;
    int personIndex = 1;
    int phoneIndex = 1;

    for (final entity in entities) {
      if (entity.start < lastEnd) continue; // Skip overlaps

      buffer.write(text.substring(lastEnd, entity.start));

      String placeholder;
      if (mapping.containsKey(entity.rawValue)) {
        placeholder = mapping[entity.rawValue]!;
      } else {
        switch (entity.entityType) {
          case 'IN_AADHAAR':
            placeholder = '[AADHAAR_ANON_${aadhaarIndex++}]';
            break;
          case 'IN_ABHA':
            placeholder = '[ABHA_ANON_${abhaIndex++}]';
            break;
          case 'IN_PAN':
            placeholder = '[PAN_REDACTED]';
            break;
          case 'PHONE_NUMBER':
            placeholder = '[PHONE_ANON_${phoneIndex++}]';
            break;
          case 'EMAIL_ADDRESS':
            placeholder = '[EMAIL_REDACTED]';
            break;
          case 'DOCTOR_NAME':
            placeholder = '[ATTENDING_PHYSICIAN]';
            break;
          case 'PATIENT_NAME':
            placeholder = '[PATIENT_${personIndex++}]';
            break;
          default:
            placeholder = '[${entity.entityType}_REDACTED]';
        }
        mapping[entity.rawValue] = placeholder;
      }

      buffer.write(placeholder);
      lastEnd = entity.end;
    }

    if (lastEnd < text.length) {
      buffer.write(text.substring(lastEnd));
    }

    return ScrubResult(
      scrubbedText: buffer.toString(),
      entities: entities,
      mapping: mapping,
    );
  }
}

class ScrubResult {
  final String scrubbedText;
  final List<DetectedEntity> entities;
  final Map<String, String> mapping;

  ScrubResult({
    required this.scrubbedText,
    required this.entities,
    required this.mapping,
  });
}
