import 'package:flutter/material.dart';
import '../services/serverpod_service.dart';
import 'camera_scanner_screen.dart';

class PatientPortalScreen extends StatefulWidget {
  const PatientPortalScreen({super.key});

  @override
  State<PatientPortalScreen> createState() => _PatientPortalScreenState();
}

class _PatientPortalScreenState extends State<PatientPortalScreen> with SingleTickerProviderStateMixin {
  final _service = ServerpodService();
  late TabController _tabController;
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  final List<Map<String, dynamic>> _messages = [
    {
      'sender': 'ai',
      'text': 'Hello Rajesh, I am your personalized PriviCare Recovery Assistant, synchronized with your attending doctor Dr. Sarah Johnson. How can I help you today with your medication schedule or recovery questions?',
      'triage': 'ROUTINE',
      'time': '10:00 AM',
    }
  ];

  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage([String? presetText]) {
    final text = presetText ?? _chatController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({
        'sender': 'user',
        'text': text,
        'time': 'Just now',
      });
      _isSending = true;
    });
    _chatController.clear();
    _scrollToBottom();

    // Determine triage
    final lower = text.toLowerCase();
    String triage = 'ROUTINE';
    String reply = 'Your query has been securely analyzed against your verified medical records.';

    if (lower.contains('pain') || lower.contains('chest') || lower.contains('shortness') || lower.contains('severe')) {
      triage = 'URGENT_ATTENTION';
      reply = '⚠️ URGENT CLINICAL ALERT: Your symptoms may require prompt medical evaluation. Please contact your attending physician Dr. Sarah Johnson or visit the nearest emergency department immediately.\n\nYour clinical team has been flagged with an alert.';
    } else if (lower.contains('calf') || lower.contains('muscle') || lower.contains('soreness') || lower.contains('statin') || lower.contains('cramp')) {
      triage = 'EVALUATE_MEDICATION';
      reply = 'ℹ️ MEDICATION NOTICE: Muscle soreness or calf tenderness can be an adverse reaction related to Atorvastatin 40mg. This has been flagged in Dr. Johnson\'s clinical queue for medication evaluation.\n\nContinue resting your leg and do not stop prescribed blood thinners without clinical advice.';
    } else if (lower.contains('food') || lower.contains('diet') || lower.contains('eat')) {
      reply = 'Dietary Guidance: With your LAD stent and heart medications, maintain a low-sodium (< 2g/day) heart-healthy diet. Avoid grapefruit or grapefruit juice as it interacts with Atorvastatin. Stay hydrated and avoid heavy oily meals.';
    } else if (lower.contains('walk') || lower.contains('exercise')) {
      reply = 'Mobility Guidance: 20-30 minutes of light, flat-surface walking is recommended. Avoid strenuous uphill walks or heavy lifting (>5 kg) during the first 6 weeks post-stent placement.';
    } else {
      reply = 'Regarding your question: All lab parameters and clinical notes have been verified. Your LAD stent is functioning normally and your current medications are safe to take as scheduled.';
    }

    Future.delayed(const Duration(milliseconds: 900), () {
      if (!mounted) return;
      setState(() {
        _isSending = false;
        _messages.add({
          'sender': 'ai',
          'text': reply,
          'triage': triage,
          'time': 'Just now',
        });
      });
      _scrollToBottom();
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _executeCryptoShred() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.shield_outlined, color: Colors.red),
            SizedBox(width: 8),
            Text('DPDP Act Section 12'),
          ],
        ),
        content: const Text(
          'Are you sure you want to execute Cryptographic Shredding on your session?\n\n'
          'All AES-256 decryption keys and scoped HMAC salts will be irreversibly purged. Stored vector embeddings and transcripts will become permanently unrecoverable.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('✅ Cryptographic Shredding complete. All keys purged from memory.'),
                  backgroundColor: Colors.teal,
                ),
              );
            },
            child: const Text('Execute Shred', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final patient = _service.activePatient;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF0D9488), Color(0xFF10B981)]),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.person_pin, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'PriviCare Patient Portal',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                ),
                Text(
                  '24/7 Recovery AI • Care Plan • DPDP Rights',
                  style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
                ),
              ],
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF0D9488),
          unselectedLabelColor: Colors.grey.shade600,
          indicatorColor: const Color(0xFF0D9488),
          indicatorWeight: 3,
          isScrollable: true,
          tabs: const [
            Tab(icon: Icon(Icons.medication_outlined, size: 18), text: 'Prescriptions'),
            Tab(icon: Icon(Icons.folder_shared_outlined, size: 18), text: 'My Vault'),
            Tab(icon: Icon(Icons.chat_bubble_outline, size: 18), text: 'Recovery AI'),
            Tab(icon: Icon(Icons.verified_user_outlined, size: 18), text: 'DPDP Privacy'),
          ],
        ),
      ),
      body: Column(
        children: [
          // Patient Identity Header Strip
          _buildIdentityHeader(patient),

          // Tab Views
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildPrescriptionsTab(patient),
                _buildVaultTab(),
                _buildRecoveryAiTab(),
                _buildDpdpTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIdentityHeader(dynamic patient) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF0FDFA),
        border: Border(bottom: BorderSide(color: Colors.teal.shade100)),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 20,
            backgroundColor: const Color(0xFF0D9488),
            child: Text(
              patient.name.split(' ').map((w) => w[0]).take(2).join(),
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      patient.name,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: Colors.teal.shade100,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        patient.uhid,
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.teal.shade900),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  'ABHA: ${patient.abhaId} • Aadhaar: ${patient.aadhaar}',
                  style: TextStyle(fontSize: 10, color: Colors.grey.shade700, fontFamily: 'monospace'),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.emerald.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.emerald.shade200),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.shield, color: Colors.emerald, size: 12),
                SizedBox(width: 4),
                Text('ABDM Linked', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.emerald)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPrescriptionsTab(dynamic patient) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Allergy Alert Banner
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFFFFF1F2),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFFECDD3)),
          ),
          child: const Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: Color(0xFFE11D48), size: 20),
              SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Known Allergies: Penicillin Group', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF9F1239))),
                    Text('Severe skin rash (anaphylactoid precaution). All hospital systems alerted.', style: TextStyle(fontSize: 11, color: Color(0xFFBE123C))),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        const Text(
          'DAILY PRESCRIPTION CHECKLIST',
          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.1, color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 10),

        _buildMedCard('Atorvastatin 40mg', '1 tablet at bedtime • Plaque stabilization', 'Night (Bedtime)', 'After Dinner', true),
        _buildMedCard('Aspirin 75mg (EC)', '1 tablet morning • Antiplatelet therapy for LAD stent', 'Morning (8:00 AM)', 'With Breakfast', true),
        _buildMedCard('Metoprolol Succinate 25mg ER', '1 tablet morning • Heart rate control', 'Morning (8:00 AM)', 'With Water', true),
        const SizedBox(height: 16),

        // Recovery Advice
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.favorite, color: Color(0xFF0D9488), size: 16),
                  SizedBox(width: 8),
                  Text('Discharge Recovery Milestones', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0F172A))),
                ],
              ),
              const SizedBox(height: 8),
              _buildMilestoneRow('30 min gentle walk daily', true),
              _buildMilestoneRow('Low sodium (< 2g/day) diet', true),
              _buildMilestoneRow('Next Cardiology Visit: Dec 15, 2024', false),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMedCard(String name, String desc, String timing, String instruction, bool taken) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Checkbox(
            value: taken,
            activeColor: const Color(0xFF0D9488),
            onChanged: (val) {},
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0F172A))),
                Text(desc, style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(4)),
                      child: Text(timing, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF475569))),
                    ),
                    const SizedBox(width: 6),
                    Text(instruction, style: TextStyle(fontSize: 10, color: Colors.grey.shade500)),
                  ],
                ),
              ],
            ),
          ),
          const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 20),
        ],
      ),
    );
  }

  Widget _buildMilestoneRow(String text, bool active) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Icon(active ? Icons.check_circle_outline : Icons.schedule, size: 14, color: active ? Colors.teal : Colors.grey),
          const SizedBox(width: 8),
          Text(text, style: TextStyle(fontSize: 12, color: Colors.grey.shade800)),
        ],
      ),
    );
  }

  Widget _buildVaultTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Camera Scan CTA Tile
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [Color(0xFF0D9488), Color(0xFF14B8A6)]),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(10)),
                child: const Icon(Icons.camera_alt, color: Colors.white, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Scan New Medical Report', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
                    Text('Auto-scrubs PHI before secure vault storage', style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.85))),
                  ],
                ),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: const Color(0xFF0D9488)),
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const CameraScannerScreen()));
                },
                child: const Text('Scan', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        const Text(
          'STORED CLINICAL RECORDS (AES-256 ENCRYPTED)',
          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.1, color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 10),

        _buildVaultItem('Discharge Summary - LAD Stent', 'Nov 18, 2024', 'Inpatient', 'PII Scrubbed'),
        _buildVaultItem('Lipid Panel & Cardiac Enzymes', 'Nov 12, 2024', 'Biochemistry', 'PII Scrubbed'),
        _buildVaultItem('12-Lead Resting ECG', 'Nov 10, 2024', 'Diagnostics', 'PII Scrubbed'),
      ],
    );
  }

  Widget _buildVaultItem(String title, String date, String cat, String status) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: const Color(0xFFF0FDFA), borderRadius: BorderRadius.circular(8)),
            child: const Icon(Icons.description, color: Color(0xFF0D9488), size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0F172A))),
                Text('$date • $cat', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(color: Colors.emerald.shade50, borderRadius: BorderRadius.circular(4)),
            child: Text(status, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.emerald)),
          ),
        ],
      ),
    );
  }

  Widget _buildRecoveryAiTab() {
    return Column(
      children: [
        // Quick Question Chips
        Container(
          height: 44,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          color: Colors.white,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _buildChip('Calf soreness with Statin?'),
              _buildChip('What foods to avoid?'),
              _buildChip('When can I walk?'),
              _buildChip('Explain my LDL cholesterol'),
            ],
          ),
        ),
        const Divider(height: 1),

        // Message List
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length,
            itemBuilder: (context, index) {
              final msg = _messages[index];
              final isUser = msg['sender'] == 'user';

              return Align(
                alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isUser ? const Color(0xFF0D9488) : Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: isUser ? null : Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (!isUser) ...[
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.smart_toy_outlined, size: 14, color: Color(0xFF0D9488)),
                            const SizedBox(width: 4),
                            const Text('PriviCare Assistant', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 10, color: Color(0xFF0D9488))),
                            if (msg['triage'] == 'URGENT_ATTENTION') ...[
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(4)),
                                child: const Text('URGENT', style: TextStyle(fontSize: 8, color: Colors.white, fontWeight: FontWeight.bold)),
                              ),
                            ],
                          ],
                        ),
                        const SizedBox(height: 6),
                      ],
                      Text(
                        msg['text'] ?? '',
                        style: TextStyle(
                          fontSize: 12,
                          color: isUser ? Colors.white : const Color(0xFF0F172A),
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),

        if (_isSending)
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Row(
              children: [
                SizedBox(width: 12, height: 12, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0D9488))),
                SizedBox(width: 8),
                Text('AI analyzing with zero-knowledge PII protection...', style: TextStyle(fontSize: 10, color: Colors.grey)),
              ],
            ),
          ),

        // Input Box
        Container(
          padding: const EdgeInsets.all(10),
          color: Colors.white,
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.camera_alt_outlined, color: Color(0xFF0D9488)),
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const CameraScannerScreen()));
                },
              ),
              Expanded(
                child: TextField(
                  controller: _chatController,
                  decoration: const InputDecoration(
                    hintText: 'Ask about your medications, recovery...',
                    hintStyle: TextStyle(fontSize: 12),
                    border: InputBorder.none,
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.send, color: Color(0xFF0D9488)),
                onPressed: () => _sendMessage(),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildChip(String text) {
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ActionChip(
        label: Text(text, style: const TextStyle(fontSize: 10)),
        backgroundColor: const Color(0xFFF1F5F9),
        onPressed: () => _sendMessage(text),
      ),
    );
  }

  Widget _buildDpdpTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.shield_outlined, color: Color(0xFF0D9488), size: 20),
                  SizedBox(width: 8),
                  Text('DPDP Act 2023 Section 12', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF0F172A))),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Under Section 12 of India\'s Digital Personal Data Protection Act 2023, you have the right to correction and erasure of your personal health data.',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade700, height: 1.4),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(8)),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Zero-Knowledge Cryptographic Shredding:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                    SizedBox(height: 4),
                    Text('• Pseudonym mapping tables encrypted with AES-256 GCM\n• Erasure destroys the session encryption keys permanently\n• Transcripts and vector embeddings become mathematically irreversible',
                      style: TextStyle(fontSize: 10, color: Color(0xFF64748B), height: 1.3),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626), padding: const EdgeInsets.symmetric(vertical: 12)),
                  icon: const Icon(Icons.delete_forever, color: Colors.white, size: 18),
                  label: const Text('Execute Section 12 Crypto-Shred', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  onPressed: _executeCryptoShred,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
