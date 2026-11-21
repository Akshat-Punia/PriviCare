import 'package:serverpod/serverpod.dart';
import '../lib/src/endpoints/clinical_endpoint.dart';
import '../lib/src/endpoints/anonymization_endpoint.dart';
import '../lib/src/endpoints/voice_note_endpoint.dart';
import '../lib/src/endpoints/chat_endpoint.dart';

void run(List<String> args) async {
  // Initialize and start Serverpod 4 server
  final pod = Serverpod(
    args,
    Protocol(),
    Endpoints(),
  );

  await pod.start();
}

void main(List<String> args) {
  run(args);
}

class Protocol extends SerializationManager {
  @override
  Map<String, dynamic> serialize(dynamic object) => {};

  @override
  dynamic deserializeByClassName(Map<String, dynamic> data) => null;
}

class Endpoints extends EndpointDispatch {
  @override
  void initializeEndpoints(Server server) {
    var endpoints = <String, Endpoint>{
      'clinical': ClinicalEndpoint(),
      'anonymization': AnonymizationEndpoint(),
      'voiceNote': VoiceNoteEndpoint(),
      'chat': ChatEndpoint(),
    };

    connectEndpoints(server, endpoints);
  }
}
