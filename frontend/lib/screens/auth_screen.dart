import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../theme/geokisan_theme.dart';
import '../main.dart' show GeoKisanHomePage; // To access GeoKisanHomePage

class GeoKisanAuthScreen extends StatefulWidget {
  final bool isUrdu;
  final bool isDarkMode;
  final String activeLanguage;
  final VoidCallback onToggleLanguage;
  final Function(String) onSetLanguage;
  final VoidCallback onToggleTheme;
  final VoidCallback onLoginSuccess;

  const GeoKisanAuthScreen({
    Key? key,
    required this.isUrdu,
    required this.isDarkMode,
    required this.activeLanguage,
    required this.onToggleLanguage,
    required this.onSetLanguage,
    required this.onToggleTheme,
    required this.onLoginSuccess,
  }) : super(key: key);

  @override
  _GeoKisanAuthScreenState createState() => _GeoKisanAuthScreenState();
}

class _GeoKisanAuthScreenState extends State<GeoKisanAuthScreen> {
  bool _isLogin = true;
  
  // Controllers
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  final _locationController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _submitAuth() async {
    setState(() {
      _errorMessage = '';
    });

    final phone = _phoneController.text.trim();
    final pass = _passwordController.text.trim();

    if (phone.isEmpty || pass.isEmpty) {
      setState(() {
        _errorMessage = widget.isUrdu ? 'فون نمبر اور پاس ورڈ درکار ہے' : 'Phone number and password are required';
      });
      return;
    }
    
    if (pass.length < 6) {
      setState(() {
        _errorMessage = widget.isUrdu ? 'پاس ورڈ کم از کم 6 حروف پر مشتمل ہونا چاہیے' : 'Password must be at least 6 characters';
      });
      return;
    }

    final prefs = await SharedPreferences.getInstance();

    if (!_isLogin) {
      final name = _nameController.text.trim();
      final confirmPass = _confirmPasswordController.text.trim();
      
      if (name.isEmpty) {
        setState(() {
          _errorMessage = widget.isUrdu ? 'نام درکار ہے' : 'Name is required';
        });
        return;
      }
      
      if (pass != confirmPass) {
        setState(() {
          _errorMessage = widget.isUrdu ? 'پاس ورڈ میل نہیں کھاتے' : 'Passwords do not match';
        });
        return;
      }

      // Check if user already exists
      final existingUser = prefs.getString('farmer_phone_$phone');
      if (existingUser != null) {
        setState(() {
          _errorMessage = widget.isUrdu ? 'یہ فون نمبر پہلے سے رجسٹرڈ ہے' : 'Phone number is already registered';
        });
        return;
      }
    } else {
      // Validate credentials on login
      final registeredPhone = prefs.getString('farmer_phone_$phone');
      final registeredPass = prefs.getString('farmer_pass_$phone');

      if (registeredPhone == null) {
        setState(() {
          _errorMessage = widget.isUrdu 
              ? 'یہ نمبر رجسٹرڈ نہیں ہے، پہلے اکاؤنٹ بنائیں' 
              : 'Phone number not registered. Please sign up first.';
        });
        return;
      }

      if (registeredPass != pass) {
        setState(() {
          _errorMessage = widget.isUrdu ? 'غلط پاس ورڈ' : 'Incorrect password.';
        });
        return;
      }
    }

    setState(() {
      _isLoading = true;
    });

    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    if (!_isLogin) {
      // Register new user credentials
      final name = _nameController.text.trim();
      final location = _locationController.text.trim();
      await prefs.setString('farmer_phone_$phone', phone);
      await prefs.setString('farmer_pass_$phone', pass);
      await prefs.setString('farmer_name_$phone', name);
      await prefs.setString('farmer_location_$phone', location);

      // Auto login
      await prefs.setString('auth_token', 'dummy_token_$phone');
      await prefs.setString('farmer_name', name);
      await prefs.setString('farmer_phone', phone);
      await prefs.setString('farmer_location', location);
    } else {
      // Log in existing user
      final name = prefs.getString('farmer_name_$phone') ?? '';
      final location = prefs.getString('farmer_location_$phone') ?? '';
      await prefs.setString('auth_token', 'dummy_token_$phone');
      await prefs.setString('farmer_name', name);
      await prefs.setString('farmer_phone', phone);
      await prefs.setString('farmer_location', location);
    }

    setState(() {
      _isLoading = false;
    });

    // Navigate to Home Dashboard and remove AuthScreen from stack
    widget.onLoginSuccess();
  }

  @override
  Widget build(BuildContext context) {
    final bgColor = widget.isDarkMode ? GeoKisanTheme.bgDarkSurface : GeoKisanTheme.surfaceCream;
    final textColor = widget.isDarkMode ? Colors.white : GeoKisanTheme.lightText;
    
    return Scaffold(
      backgroundColor: widget.isDarkMode ? const Color(0xFF1E1E1E) : const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: Text(widget.isUrdu ? 'لاگ ان / سائن اپ' : 'Login / Sign Up'),
        actions: [
          IconButton(
            icon: Icon(widget.isUrdu ? Icons.language : Icons.translate),
            onPressed: widget.onToggleLanguage,
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Container(
            padding: const EdgeInsets.all(24.0),
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: BorderRadius.circular(20),
              boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 5))],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.agriculture, size: 64, color: GeoKisanTheme.primaryGreen),
                const SizedBox(height: 16),
                Text(
                  _isLogin 
                      ? (widget.isUrdu ? "خوش آمدید" : "Welcome Back") 
                      : (widget.isUrdu ? "نیا اکاؤنٹ بنائیں" : "Create Account"),
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: GeoKisanTheme.primaryGreen,
                  ),
                ),
                const SizedBox(height: 24),
                if (!_isLogin) ...[
                  TextField(
                    controller: _nameController,
                    decoration: InputDecoration(
                      labelText: widget.isUrdu ? "پورا نام" : "Full Name",
                      prefixIcon: const Icon(Icons.person),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: InputDecoration(
                    labelText: widget.isUrdu ? "فون نمبر" : "Phone Number",
                    prefixIcon: const Icon(Icons.phone),
                    border: const OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                if (!_isLogin) ...[
                  TextField(
                    controller: _locationController,
                    decoration: InputDecoration(
                      labelText: widget.isUrdu ? "مقام / گاؤں / شہر" : "Location / Village / City",
                      prefixIcon: const Icon(Icons.location_on),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: InputDecoration(
                    labelText: widget.isUrdu ? "پاس ورڈ" : "Password",
                    prefixIcon: const Icon(Icons.lock),
                    border: const OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                if (!_isLogin) ...[
                  TextField(
                    controller: _confirmPasswordController,
                    obscureText: true,
                    decoration: InputDecoration(
                      labelText: widget.isUrdu ? "پاس ورڈ کی تصدیق کریں" : "Confirm Password",
                      prefixIcon: const Icon(Icons.lock_outline),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                if (_errorMessage.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: Text(
                      _errorMessage,
                      style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                    ),
                  ),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _submitAuth,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: GeoKisanTheme.primaryGreen,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : Text(
                            _isLogin 
                                ? (widget.isUrdu ? "لاگ ان کریں" : "Login") 
                                : (widget.isUrdu ? "سائن اپ کریں" : "Sign Up"),
                            style: const TextStyle(fontSize: 18, color: Colors.white, fontWeight: FontWeight.bold),
                          ),
                  ),
                ),
                const SizedBox(height: 16),
                if (_isLogin)
                  TextButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(widget.isUrdu ? "پاس ورڈ ری سیٹ لنک بھیج دیا گیا" : "Password reset link sent")),
                      );
                    },
                    child: Text(widget.isUrdu ? "پاس ورڈ بھول گئے؟" : "Forgot Password?"),
                  ),
                TextButton(
                  onPressed: () {
                    setState(() {
                      _isLogin = !_isLogin;
                      _errorMessage = '';
                    });
                  },
                  child: Text(
                    _isLogin 
                        ? (widget.isUrdu ? "اکاؤنٹ نہیں ہے؟ سائن اپ کریں" : "Don't have an account? Sign Up") 
                        : (widget.isUrdu ? "پہلے سے اکاؤنٹ ہے؟ لاگ ان کریں" : "Already have an account? Login"),
                    style: TextStyle(color: textColor),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
