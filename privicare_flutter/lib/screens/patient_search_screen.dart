import 'package:flutter/material.dart';
import '../services/serverpod_service.dart';

class PatientSearchScreen extends StatefulWidget {
  const PatientSearchScreen({super.key});

  @override
  State<PatientSearchScreen> createState() => _PatientSearchScreenState();
}

class _PatientSearchScreenState extends State<PatientSearchScreen> {
  final _service = ServerpodService();
  final TextEditingController _searchController = TextEditingController();
  String _selectedDept = 'ALL';
  List<dynamic> _patients = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadPatients();
  }

  Future<void> _loadPatients() async {
    setState(() => _isLoading = true);
    final results = await _service.searchPatients(
      _searchController.text,
      department: _selectedDept,
    );
    setState(() {
      _patients = results;
      _isLoading = false;
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
        title: const Text('Search Patient Directory', style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: Column(
        children: [
          // Search Input Bar
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: TextField(
              controller: _searchController,
              onChanged: (_) => _loadPatients(),
              decoration: InputDecoration(
                hintText: 'Search by Name, UHID, ABHA, Aadhaar, Diagnosis...',
                hintStyle: const TextStyle(fontSize: 12, color: Colors.grey),
                prefixIcon: const Icon(Icons.search, color: Color(0xFF2563EB)),
                filled: true,
                fillColor: const Color(0xFFF1F5F9),
                contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              ),
            ),
          ),

          // Department Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: ['ALL', 'Cardiology', 'Oncology', 'Pulmonology'].map((dept) {
                final isSelected = _selectedDept == dept;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(dept == 'ALL' ? 'All Departments' : dept),
                    selected: isSelected,
                    selectedColor: const Color(0xFF2563EB),
                    labelStyle: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? Colors.white : const Color(0xFF475569),
                    ),
                    backgroundColor: Colors.white,
                    side: BorderSide(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                    onSelected: (selected) {
                      setState(() {
                        _selectedDept = dept;
                      });
                      _loadPatients();
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          // Search Results List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _patients.isEmpty
                    ? const Center(
                        child: Text('No matching patient records found.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _patients.length,
                        itemBuilder: (context, index) {
                          final patient = _patients[index];
                          final isActive = patient.uhid == _service.activePatient.uhid;

                          return InkWell(
                            onTap: () {
                              _service.activePatient = patient;
                              Navigator.pop(context, patient);
                            },
                            child: Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: isActive ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0), width: isActive ? 1.5 : 1),
                              ),
                              child: Row(
                                children: [
                                  CircleAvatar(
                                    radius: 22,
                                    backgroundColor: isActive ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
                                    child: Text(
                                      patient.name.split(' ').map((w) => w[0]).take(2).join(),
                                      style: TextStyle(color: isActive ? Colors.white : const Color(0xFF334155), fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            Text(patient.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF0F172A))),
                                            const SizedBox(width: 8),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                              decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(4)),
                                              child: Text(patient.uhid, style: const TextStyle(fontSize: 10, color: Color(0xFF2563EB), fontWeight: FontWeight.bold)),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 4),
                                        Text('${patient.age} Yrs • ${patient.gender} • ${patient.department}', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                                        const SizedBox(height: 2),
                                        Text(patient.primaryDiagnosis ?? '', style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: Color(0xFF475569)), maxLines: 1, overflow: TextOverflow.ellipsis),
                                      ],
                                    ),
                                  ),
                                  if (isActive)
                                    const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 20),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
