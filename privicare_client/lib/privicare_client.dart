import 'dart:convert';
import 'package:serverpod_client/serverpod_client.dart';

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

  factory MedicalReport.fromJson(Map<String, dynamic> json) => MedicalReport(
        id: json['id'] as String,
        uhid: json['uhid'] as String,
        filename: json['filename'] as String,
        date: json['date'] as String,
        department: json['department'] as String,
        summary: json['summary'] as String,
        scrubbedText: json['scrubbedText'] as String,
        scrubbedEntities: (json['scrubbedEntities'] as List<dynamic>?)?.cast<String>() ?? [],
      );
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

  factory VoiceNote.fromJson(Map<String, dynamic> json) => VoiceNote(
        id: json['id'] as String,
        uhid: json['uhid'] as String,
        doctorId: json['doctorId'] as String,
        transcript: json['transcript'] as String,
        scrubbedTranscript: json['scrubbedTranscript'] as String,
        clinicalTriage: json['clinicalTriage'] as String,
        timestamp: DateTime.parse(json['timestamp'] as String),
        reviewed: json['reviewed'] as bool? ?? false,
      );
}

class EndpointClinical extends EndpointRef {
  EndpointClinical(super.caller);

  @override
  String get name => 'clinical';

  Future<List<PatientRecord>> getPatients() async {
    return caller.callServerEndpoint<List<PatientRecord>>(
      'clinical',
      'getPatients',
      {},
    );
  }

  Future<List<PatientRecord>> searchPatients(String query, {String? department}) async {
    return caller.callServerEndpoint<List<PatientRecord>>(
      'clinical',
      'searchPatients',
      {'query': query, 'department': department},
    );
  }

  Future<MedicalReport> uploadReport({
    required String uhid,
    required String filename,
    required String rawContent,
  }) async {
    return caller.callServerEndpoint<MedicalReport>(
      'clinical',
      'uploadReport',
      {'uhid': uhid, 'filename': filename, 'rawContent': rawContent},
    );
  }

  Future<Map<String, dynamic>> cryptoShred(String uhid) async {
    return caller.callServerEndpoint<Map<String, dynamic>>(
      'clinical',
      'cryptoShred',
      {'uhid': uhid},
    );
  }
}

class EndpointVoiceNote extends EndpointRef {
  EndpointVoiceNote(super.caller);

  @override
  String get name => 'voiceNote';

  Future<List<VoiceNote>> getVoiceNotes(String uhid) async {
    return caller.callServerEndpoint<List<VoiceNote>>(
      'voiceNote',
      'getVoiceNotes',
      {'uhid': uhid},
    );
  }

  Future<VoiceNote> submitVoiceNote({
    required String uhid,
    required String doctorId,
    required String rawTranscript,
  }) async {
    return caller.callServerEndpoint<VoiceNote>(
      'voiceNote',
      'submitVoiceNote',
      {'uhid': uhid, 'doctorId': doctorId, 'rawTranscript': rawTranscript},
    );
  }
}

class EndpointChat extends EndpointRef {
  EndpointChat(super.caller);

  @override
  String get name => 'chat';

  Future<Map<String, dynamic>> consultCopilot({
    required String uhid,
    required String query,
    required String doctorId,
  }) async {
    return caller.callServerEndpoint<Map<String, dynamic>>(
      'chat',
      'consultCopilot',
      {'uhid': uhid, 'query': query, 'doctorId': doctorId},
    );
  }
}

class EndpointAnonymization extends EndpointRef {
  EndpointAnonymization(super.caller);

  @override
  String get name => 'anonymization';

  Future<Map<String, dynamic>> scrubText(String text, {String? uhid}) async {
    return caller.callServerEndpoint<Map<String, dynamic>>(
      'anonymization',
      'scrubText',
      {'text': text, 'uhid': uhid},
    );
  }
}

class Client extends ServerpodClient {
  late final EndpointClinical clinical;
  late final EndpointVoiceNote voiceNote;
  late final EndpointChat chat;
  late final EndpointAnonymization anonymization;

  Client(
    String host, {
    SecurityContext? context,
    ServerpodClientErrorCallback? errorHandler,
    AuthenticationKeyManager? authenticationKeyManager,
  }) : super(
          host,
          Protocol(),
          securityContext: context,
          errorHandler: errorHandler,
          authenticationKeyManager: authenticationKeyManager,
        ) {
    clinical = EndpointClinical(this);
    voiceNote = EndpointVoiceNote(this);
    chat = EndpointChat(this);
    anonymization = EndpointAnonymization(this);
  }

  @override
  Map<String, EndpointRef> get endpointRefLookup => {
        'clinical': clinical,
        'voiceNote': voiceNote,
        'chat': chat,
        'anonymization': anonymization,
      };
}

class Protocol extends SerializationManager {
  @override
  Map<String, dynamic> serialize(dynamic object) => {};

  @override
  dynamic deserializeByClassName(Map<String, dynamic> data) => null;
}
