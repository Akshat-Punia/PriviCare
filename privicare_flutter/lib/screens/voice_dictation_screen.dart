import 'package:flutter/material.dart';
import '../services/serverpod_service.dart';

class VoiceDictationScreen extends StatefulWidget {
  const VoiceDictationScreen({super.key});

  @override
  State<VoiceDictationScreen> createState() => _VoiceDictationScreenState();
}

class _VoiceDictationScreenState extends State<VoiceDictationScreen> with SingleTickerProviderStateMixin {
  final _service = ServerpodService();
  bool _isRecording = false;
  bool _isSubmitting = false;
  String _currentTranscript = '';
  dynamic _savedVoiceNote;
  late final AnimationController _pulseController;

  final List<String> _quickSpeechPrompts = [
    'Patient Rajesh Sharma reported mild calf soreness after taking Atorvastatin 40mg.',
    'Follow-up post mid-LAD stent: Vitals stable BP 128/82, HR 68. Compliant with Aspirin.',
    'Patient complained of exertional chest tightness during morning walk. Recommended urgent ECG.',
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  void _toggleRecording() {
    if (_isRecording) {
      // Stop recording
      setState(() {
        _isRecording = false;
      });
      _submitVoiceNote();
    } else {
      // Start recording with speech simulation
      setState(() {
        _isRecording = true;
        _savedVoiceNote = null;
        _currentTranscript = _quickSpeechPrompts[0];
      });
    }
  }

  Future<void> _submitVoiceNote() async {
    if (_currentTranscript.isEmpty) return;
    setState(() {
      _isSubmitting = true;
    });

    final note = await _service.submitVoiceNote(
      uhid: _service.activePatient.uhid,
      doctorId: 'DR-SARAH-JOHNSON',
      rawTranscript: _currentTranscript,
    );

    setState(() {
      _isSubmitting = false;
      _savedVoiceNote = note;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF0F172A)),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Doctor Voice Dictation', style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold)),
            Text('Track 2: Phone Microphone + Gnani Integration', style: TextStyle(color: Color(0xFF64748B), fontSize: 10)),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Voice Microphone Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: const Offset(0, 4)),
                ],
              ),
              child: Column(
                children: [
                  GestureDetector(
                    onTap: _toggleRecording,
                    child: AnimatedBuilder(
                      animation: _pulseController,
                      builder: (context, child) {
                        return Container(
                          width: 88,
                          height: 88,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _isRecording ? const Color(0xFFDC2626) : const Color(0xFF7C3AED),
                            boxShadow: [
                              BoxShadow(
                                color: (_isRecording ? Colors.red : const Color(0xFF7C3AED)).withOpacity(_isRecording ? 0.3 + (_pulseController.value * 0.3) : 0.2),
                                blurRadius: _isRecording ? 20 + (_pulseController.value * 10) : 10,
                                spreadRadius: _isRecording ? 4 + (_pulseController.value * 6) : 0,
                              ),
                            ],
                          ),
                          child: Icon(
                            _isRecording ? Icons.stop : Icons.mic,
                            color: Colors.white,
                            size: 38,
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    _isRecording ? 'Listening via Phone Microphone...' : 'Tap to Dictate Clinical Note',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                      color: _isRecording ? const Color(0xFFDC2626) : const Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _isRecording ? 'Speak freely. Serverpod handles live PII redaction.' : 'Mandatory Gnani / Web Audio platform integration',
                    style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Speech Simulation Prompts
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Quick Clinical Dictation Samples:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _quickSpeechPrompts.map((prompt) {
                    return ActionChip(
                      backgroundColor: Colors.white,
                      side: const BorderSide(color: Color(0xFFE2E8F0)),
                      label: Text(
                        prompt.length > 36 ? '${prompt.substring(0, 36)}...' : prompt,
                        style: const TextStyle(fontSize: 11, color: Color(0xFF334155)),
                      ),
                      onPressed: () {
                        setState(() {
                          _currentTranscript = prompt;
                        });
                        _submitVoiceNote();
                      },
                    );
                  }).toList(),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Live PII Redaction & Triage Card
            if (_isSubmitting)
              const Padding(
                padding: EdgeInsets.all(24),
                child: Center(
                  child: Column(
                    children: [
                      CircularProgressIndicator(color: Color(0xFF7C3AED)),
                      SizedBox(height: 12),
                      Text('Running Presidio PII Scrub & Clinical Triage...', style: TextStyle(fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                ),
              )
            else if (_savedVoiceNote != null)
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Sanitized Voice Note', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0F172A))),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: _savedVoiceNote.clinicalTriage == 'URGENT_ATTENTION'
                                ? const Color(0xFFFEE2E2)
                                : const Color(0xFFFEF3C7),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            _savedVoiceNote.clinicalTriage,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: _savedVoiceNote.clinicalTriage == 'URGENT_ATTENTION' ? Colors.red.shade800 : Colors.amber.shade900,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                    const Text('Original Spoken Input:', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.grey)),
                    const SizedBox(height: 4),
                    Text(_savedVoiceNote.transcript, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                    const SizedBox(height: 12),
                    const Text('Scrubbed Output (Stored in Serverpod):', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF10B981))),
                    const SizedBox(height: 4),
                    Text(_savedVoiceNote.scrubbedTranscript, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
