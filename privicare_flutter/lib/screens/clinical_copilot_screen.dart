import 'package:flutter/material.dart';
import '../services/serverpod_service.dart';

class ClinicalCopilotScreen extends StatefulWidget {
  const ClinicalCopilotScreen({super.key});

  @override
  State<ClinicalCopilotScreen> createState() => _ClinicalCopilotScreenState();
}

class _ClinicalCopilotScreenState extends State<ClinicalCopilotScreen> {
  final _service = ServerpodService();
  final TextEditingController _queryController = TextEditingController();
  final List<Map<String, String>> _messages = [
    {
      'role': 'assistant',
      'text':
          'Welcome Dr. Sarah Johnson. I am your PriviCare Clinical Co-Pilot backed by Serverpod 4. You are reviewing the medical archive of Rajesh Sharma (UHID-982143). Ask any clinical question regarding previous stent procedures, lab panels, or medication interactions. All queries are scrubbed for PII before processing.',
    },
  ];
  bool _isLoading = false;

  Future<void> _sendQuery([String? predefinedText]) async {
    final text = predefinedText ?? _queryController.text;
    if (text.trim().isEmpty || _isLoading) return;

    setState(() {
      _messages.add({'role': 'user', 'text': text});
      _isLoading = true;
    });
    _queryController.clear();

    final response = await _service.consultCopilot(
      _service.activePatient.uhid,
      text,
    );

    setState(() {
      _isLoading = false;
      _messages.add({
        'role': 'assistant',
        'text': response['doctorResponse'] as String? ?? 'No response generated.',
      });
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
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Clinical AI Co-Pilot', style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold)),
            Text('Active: ${_service.activePatient.name} (${_service.activePatient.uhid})', style: const TextStyle(color: Color(0xFF2563EB), fontSize: 10, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
      body: Column(
        children: [
          // Suggested Quick Clinical Queries
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.white,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildPromptChip('Cardiology & Stent Summary'),
                  _buildPromptChip('Evaluate Statin Myalgia'),
                  _buildPromptChip('Check DAPT Drug Interactions'),
                ],
              ),
            ),
          ),

          // Messages List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg['role'] == 'user';

                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(14),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.82),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF2563EB) : Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: isUser ? null : Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: Text(
                      msg['text']!,
                      style: TextStyle(
                        fontSize: 12.5,
                        color: isUser ? Colors.white : const Color(0xFF1E293B),
                        height: 1.4,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2)),
                  SizedBox(width: 10),
                  Text('Synthesizing clinical response from Serverpod...', style: TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
            ),

          // Message Input Field
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.white,
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _queryController,
                      decoration: InputDecoration(
                        hintText: 'Ask clinical question regarding this patient...',
                        hintStyle: const TextStyle(fontSize: 12, color: Colors.grey),
                        filled: true,
                        fillColor: const Color(0xFFF1F5F9),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(20), borderSide: BorderSide.none),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.send, color: Color(0xFF2563EB)),
                    onPressed: () => _sendQuery(),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPromptChip(String text) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ActionChip(
        label: Text(text, style: const TextStyle(fontSize: 11, color: Color(0xFF334155))),
        backgroundColor: const Color(0xFFF8FAFC),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
        onPressed: () => _sendQuery(text),
      ),
    );
  }
}
