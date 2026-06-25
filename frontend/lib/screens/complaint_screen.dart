import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme/geokisan_theme.dart';
import '../widgets/speaker_button.dart';

class ComplaintScreen extends StatefulWidget {
  final bool isUrdu;

  const ComplaintScreen({Key? key, required this.isUrdu}) : super(key: key);

  @override
  State<ComplaintScreen> createState() => _ComplaintScreenState();
}

class _ComplaintScreenState extends State<ComplaintScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _cnicController = TextEditingController();
  final _districtController = TextEditingController();
  final _descriptionController = TextEditingController();

  String _category = "Water Theft";
  File? _evidenceFile;
  final ImagePicker _picker = ImagePicker();

  final List<String> _categoriesEn = [
    "Water Theft",
    "Canal Blockage",
    "Seed Fraud",
    "Fertilizer Black Marketing",
    "Other"
  ];

  final Map<String, String> _categoriesUr = {
    "Water Theft": "نہر کے پانی کی چوری (Water Theft)",
    "Canal Blockage": "نہری رکاوٹ (Canal Blockage)",
    "Seed Fraud": "ناقص بیج کا فراڈ (Seed Fraud)",
    "Fertilizer Black Marketing": "کھاد کی بلیک مارکیٹنگ",
    "Other": "دیگر (Other)"
  };

  @override
  void dispose() {
    _nameController.dispose();
    _cnicController.dispose();
    _districtController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickEvidence() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.camera);
      if (image != null) {
        setState(() {
          _evidenceFile = File(image.path);
        });
      }
    } catch (e) {
      print("Error picking evidence: $e");
    }
  }

  String? _encodeQueryParameters(Map<String, String> params) {
    return params.entries
        .map((MapEntry<String, String> e) =>
            '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value)}')
        .join('&');
  }

  Future<void> _submitComplaint() async {
    if (_formKey.currentState!.validate()) {
      final name = _nameController.text.trim();
      final cnic = _cnicController.text.trim();
      final district = _districtController.text.trim();
      final desc = _descriptionController.text.trim();
      
      final subject = "Citizen Complaint - $_category - $district";
      final body = "Citizen Name: $name\n"
          "CNIC: $cnic\n"
          "District/Tehsil: $district\n"
          "Category: $_category\n\n"
          "Details:\n$desc";

      final Uri emailLaunchUri = Uri(
        scheme: 'mailto',
        path: 'complaints@pakistan.gov.pk',
        query: _encodeQueryParameters(<String, String>{
          'subject': subject,
          'body': body,
        }),
      );

      try {
        await launchUrl(emailLaunchUri, mode: LaunchMode.externalApplication);
      } catch (e) {
        print("Failed to launch email app: $e");
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            widget.isUrdu
                ? "آپ کی شکایت کامیابی کے ساتھ درج کر لی گئی ہے اور complaints@pakistan.gov.pk پر بھیج دی گئی ہے۔"
                : "Your complaint has been successfully registered and forwarded to complaints@pakistan.gov.pk.",
          ),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 3),
        ),
      );

      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          Navigator.pop(context);
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final instructions = widget.isUrdu
        ? "سٹیزن شکایت ڈیسک کے ذریعے آپ نہر کے پانی کی چوری، ناقص بیج اور کھاد کی بلیک مارکیٹنگ کی براہ راست حکومت پاکستان کو رپورٹ درج کروا سکتے ہیں۔ تمام معلومات درست فراہم کریں۔"
        : "Through the Citizen Complaint Desk, you can report canal water theft, seed fraud, and fertilizer black marketing directly to the Government of Pakistan. Please fill in accurate details.";

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isUrdu ? "سٹیزن شکایت ڈیسک" : "Citizen Complaint Desk"),
        backgroundColor: GeoKisanTheme.primaryGreen,
        foregroundColor: Colors.white,
      ),
      backgroundColor: Colors.grey[50],
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                color: Colors.green[50],
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.info, color: GeoKisanTheme.primaryGreen),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          instructions,
                          style: const TextStyle(fontSize: 13, height: 1.4, color: Colors.black87),
                        ),
                      ),
                      const SizedBox(width: 8),
                      SpeakerButton(
                        text: instructions,
                        languageCode: widget.isUrdu ? 'ur' : 'en',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: widget.isUrdu ? "پورا نام" : "Full Name",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.person, color: GeoKisanTheme.primaryGreen),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return widget.isUrdu ? "براہ کرم اپنا نام درج کریں" : "Please enter your name";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _cnicController,
                decoration: InputDecoration(
                  labelText: widget.isUrdu ? "شناختی کارڈ نمبر" : "CNIC Number",
                  hintText: "35201-1234567-1",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.badge, color: GeoKisanTheme.primaryGreen),
                ),
                keyboardType: TextInputType.number,
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return widget.isUrdu ? "شناختی کارڈ نمبر درج کریں" : "Please enter CNIC number";
                  }
                  final reg = RegExp(r'^\d{5}-\d{7}-\d{1}$');
                  if (!reg.hasMatch(val.trim())) {
                    return widget.isUrdu
                        ? "درست فارمیٹ: 1-1234567-35201"
                        : "Format: 35201-1234567-1";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _districtController,
                decoration: InputDecoration(
                  labelText: widget.isUrdu ? "ضلع اور تحصیل" : "District & Tehsil",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.location_city, color: GeoKisanTheme.primaryGreen),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return widget.isUrdu ? "تحصیل یا ضلع درج کریں" : "Please enter District & Tehsil";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _category,
                decoration: InputDecoration(
                  labelText: widget.isUrdu ? "شکایت کا زمرہ" : "Complaint Category",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.category, color: GeoKisanTheme.primaryGreen),
                ),
                items: _categoriesEn.map((cat) {
                  return DropdownMenuItem<String>(
                    value: cat,
                    child: Text(widget.isUrdu ? (_categoriesUr[cat] ?? cat) : cat),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _category = val;
                    });
                  }
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _descriptionController,
                maxLines: 4,
                decoration: InputDecoration(
                  labelText: widget.isUrdu ? "تفصیلی شکایت" : "Detailed Complaint Description",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.edit_note, color: GeoKisanTheme.primaryGreen),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return widget.isUrdu ? "تفصیل درج کریں" : "Please enter complaint details";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              Card(
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: Colors.grey[300]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
                  child: Row(
                    children: [
                      ElevatedButton.icon(
                        onPressed: _pickEvidence,
                        icon: const Icon(Icons.camera_alt, color: Colors.white, size: 18),
                        label: Text(widget.isUrdu ? "تصویر منسلک کریں" : "Attach Photo"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: GeoKisanTheme.aiGold,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _evidenceFile != null
                              ? (widget.isUrdu ? "تصویر منسلک ہو گئی ہے" : "Photo Attached: ${_evidenceFile!.path.split('/').last}")
                              : (widget.isUrdu ? "کوئی تصویر منسلک نہیں" : "No photo attached"),
                          style: TextStyle(
                            fontSize: 12,
                            color: _evidenceFile != null ? Colors.green[700] : Colors.grey[600],
                            fontWeight: _evidenceFile != null ? FontWeight.bold : FontWeight.normal,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _submitComplaint,
                style: ElevatedButton.styleFrom(
                  backgroundColor: GeoKisanTheme.primaryGreen,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: Text(
                  widget.isUrdu ? "شکایت درج کریں (ای میل بھیجیں)" : "Submit Complaint (Send Email)",
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
