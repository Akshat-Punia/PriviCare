class PatientRecord {
  final String uhid;
  final String name;
  final int age;
  final String gender;
  final String bloodGroup;
  final String department;
  final String? abhaId;
  final String? aadhaar;
  final String? phone;
  final String? primaryDiagnosis;
  final List<String> medications;
  final List<String> allergies;
  final int reportsCount;

  PatientRecord({
    required this.uhid,
    required this.name,
    required this.age,
    required this.gender,
    required this.bloodGroup,
    required this.department,
    this.abhaId,
    this.aadhaar,
    this.phone,
    this.primaryDiagnosis,
    this.medications = const [],
    this.allergies = const [],
    this.reportsCount = 0,
  });

  Map<String, dynamic> toJson() => {
        'uhid': uhid,
        'name': name,
        'age': age,
        'gender': gender,
        'bloodGroup': bloodGroup,
        'department': department,
        'abhaId': abhaId,
        'aadhaar': aadhaar,
        'phone': phone,
        'primaryDiagnosis': primaryDiagnosis,
        'medications': medications,
        'allergies': allergies,
        'reportsCount': reportsCount,
      };

  factory PatientRecord.fromJson(Map<String, dynamic> json) => PatientRecord(
        uhid: json['uhid'] as String,
        name: json['name'] as String,
        age: json['age'] as int? ?? 45,
        gender: json['gender'] as String? ?? 'Male',
        bloodGroup: json['bloodGroup'] as String? ?? 'B+',
        department: json['department'] as String? ?? 'General Medicine',
        abhaId: json['abhaId'] as String?,
        aadhaar: json['aadhaar'] as String?,
        phone: json['phone'] as String?,
        primaryDiagnosis: json['primaryDiagnosis'] as String?,
        medications: (json['medications'] as List<dynamic>?)?.cast<String>() ?? [],
        allergies: (json['allergies'] as List<dynamic>?)?.cast<String>() ?? [],
        reportsCount: json['reportsCount'] as int? ?? 0,
      );
}

class MedicalReport {
  final String id;
  final String uhid;
  final String filename;
  final String date;
  final String department;
  final String summary;
  final String scrubbedText;
  final List<String> scrubbedEntities;

  MedicalReport({
    required this.id,
    required this.uhid,
    required this.filename,
    required this.date,
    required this.department,
    required this.summary,
    required this.scrubbedText,
    this.scrubbedEntities = const [],
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'uhid': uhid,
        'filename': filename,
        'date': date,
        'department': department,
        'summary': summary,
        'scrubbedText': scrubbedText,
        'scrubbedEntities': scrubbedEntities,
      };
}

class VoiceNote {
  final String id;
  final String uhid;
  final String doctorId;
  final String transcript;
  final String scrubbedTranscript;
  final String clinicalTriage;
  final DateTime timestamp;
  bool reviewed;

  VoiceNote({
    required this.id,
    required this.uhid,
    required this.doctorId,
    required this.transcript,
    required this.scrubbedTranscript,
    required this.clinicalTriage,
    required this.timestamp,
    this.reviewed = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'uhid': uhid,
        'doctorId': doctorId,
        'transcript': transcript,
        'scrubbedTranscript': scrubbedTranscript,
        'clinicalTriage': clinicalTriage,
        'timestamp': timestamp.toIso8601String(),
        'reviewed': reviewed,
      };
}
