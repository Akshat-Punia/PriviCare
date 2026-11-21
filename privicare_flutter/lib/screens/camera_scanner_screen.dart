import 'package:flutter/material.dart';
import '../services/serverpod_service.dart';

class CameraScannerScreen extends StatefulWidget {
  const CameraScannerScreen({super.key});

  @override
  State<CameraScannerScreen> createState() => _CameraScannerScreenState();
}

class _CameraScannerScreenState extends State<CameraScannerScreen> {
  final _service = ServerpodService();
  bool _isProcessing = false;
  String? _rawScannedText;
  String? _scrubbedResult;
  List<String> _detectedEntities = [];

  // Realistic sample clinical discharge summary for demonstration
  static const String _sampleClinicalScan = '''
FORTIS ESCORTS HEART INSTITUTE
Discharge Summary - Department of Cardiology
Patient Name: Rajesh Sharma | Age: 54 | Sex: Male
UHID: UHID-982143 | ABHA ID: 91-4412-3390-1123
Aadhaar: 9823 4410 7721 | Phone: +91 98765 43210
Attending Physician: Dr. Sarah Johnson

Clinical Course:
Patient presented with acute coronary syndrome. Coronary angiogram showed 90% stenosis in mid-LAD. Successful deployment of Drug-Eluting Stent (DES) achieved. Post-procedure LVEF: 52%. Discharge medications include Atorvastatin 40mg OD and Telmisartan 40mg.
''';

  Future<void> _captureAndProcessDocument() async {
    setState(() {
      _isProcessing = true;
    });

    // Simulate OCR text extraction from camera image
    await Future.delayed(const Duration(milliseconds: 900));

    // Upload to Serverpod backend for PII scrubbing & cryptographic vaulting
    final report = await _service.uploadReport(
      uhid: _service.activePatient.uhid,
      filename: 'Camera_Scan_${DateTime.now().millisecondsSinceEpoch}.pdf',
      rawContent: _sampleClinicalScan,
    );

    setState(() {
      _isProcessing = false;
      _rawScannedText = _sampleClinicalScan;
      _scrubbedResult = report.scrubbedText;
      _detectedEntities = report.scrubbedEntities;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Camera Document Scanner', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
            Text('Track 2: Phone Camera OCR & Serverpod PII Scrub', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10)),
          ],
        ),
      ),
      body: Column(
        children: [
          // Simulated / Live Camera Viewfinder Area
          Expanded(
            flex: _scrubbedResult == null ? 3 : 2,
            child: Container(
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF3B82F6), width: 2),
              ),
              child: Stack(
                children: [
                  // Camera Viewfinder Background Simulation
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.document_scanner, size: 64, color: Colors.blue.withOpacity(0.5)),
                        const SizedBox(height: 12),
                        const Text(
                          'Align Prescription or Medical Report',
                          style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w500),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Dual-compliance Presidio & ABDM lens active',
                          style: TextStyle(color: Colors.white38, fontSize: 11),
                        ),
                      ],
                    ),
                  ),

                  // Bounding guide corners
                  Positioned(
                    top: 20,
                    left: 20,
                    child: _buildCorner(isTop: true, isLeft: true),
                  ),
                  Positioned(
                    top: 20,
                    right: 20,
                    child: _buildCorner(isTop: true, isLeft: false),
                  ),
                  Positioned(
                    bottom: 20,
                    left: 20,
                    child: _buildCorner(isTop: false, isLeft: true),
                  ),
                  Positioned(
                    bottom: 20,
                    right: 20,
                    child: _buildCorner(isTop: false, isLeft: false),
                  ),

                  if (_isProcessing)
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(color: Color(0xFF3B82F6)),
                            SizedBox(height: 16),
                            Text('Running OCR & Serverpod PII Scrub...', style: TextStyle(color: Colors.white, fontSize: 13)),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),

          // Side-by-Side PII Redaction Diff View
          if (_scrubbedResult != null)
            Expanded(
              flex: 3,
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.shield_check, color: Color(0xFF10B981), size: 18),
                            SizedBox(width: 8),
                            Text('Zero-Leakage Sanitized Output', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: const Color(0xFF065F46),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text('Serverpod Indexed', style: TextStyle(color: Color(0xFFA7F3D0), fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Expanded(
                      child: SingleChildScrollView(
                        child: Text(
                          _scrubbedResult!,
                          style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 11, fontFamily: 'monospace', height: 1.4),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // Bottom Action Control Bar
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    icon: const Icon(Icons.camera),
                    label: Text(
                      _scrubbedResult == null ? 'Capture & Ingest Report' : 'Scan Another Document',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    onPressed: _isProcessing ? null : _captureAndProcessDocument,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCorner({required bool isTop, required bool isLeft}) {
    return Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        border: Border(
          top: isTop ? const BorderSide(color: Color(0xFF3B82F6), width: 3) : BorderSide.none,
          bottom: !isTop ? const BorderSide(color: Color(0xFF3B82F6), width: 3) : BorderSide.none,
          left: isLeft ? const BorderSide(color: Color(0xFF3B82F6), width: 3) : BorderSide.none,
          right: !isLeft ? const BorderSide(color: Color(0xFF3B82F6), width: 3) : BorderSide.none,
        ),
      ),
    );
  }
}
