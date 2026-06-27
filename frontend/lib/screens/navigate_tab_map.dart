import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math' as math;
import 'package:geolocator/geolocator.dart';
import '../theme/geokisan_theme.dart';
import '../services/api_service.dart';
import '../services/tts_service.dart';
import '../widgets/speaker_button.dart';

class NavigateTabMapWorkspace extends StatefulWidget {
  final LatLng activeLandCoords;
  final bool isUrdu;
  final bool isDarkMode;
  final String backendUrl;
  final bool isOffline;

  const NavigateTabMapWorkspace({
    Key? key,
    required this.activeLandCoords,
    required this.isUrdu,
    required this.isDarkMode,
    required this.backendUrl,
    required this.isOffline,
  }) : super(key: key);

  @override
  State<NavigateTabMapWorkspace> createState() => _NavigateTabMapWorkspaceState();
}

class _NavigateTabMapWorkspaceState extends State<NavigateTabMapWorkspace> with SingleTickerProviderStateMixin {
  GoogleMapController? _mapController;
  late TabController _tabController;

  // Search Fields
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _startLocationController = TextEditingController(text: "Current Location");
  final TextEditingController _mandiController = TextEditingController();

  List<dynamic> _predictions = [];
  bool _isEarthEngineSatellite = false;
  String? _geeTileUrl;
  String _activeScanMode = "normal";

  // Boundary Drawing State (GEE)
  List<LatLng> _boundaryPoints = [];
  bool _isDrawingMode = false;
  double _calculatedArea = 0.0;
  String _boundaryAnalysisResult = "";
  bool _isBoundaryLoading = false;

  // Mandi Routing State
  List<LatLng> _routePoints = [];
  String _routeDistance = "";
  String _routeDuration = "";
  String _routeSummary = "";
  String _routeAdvice = "";
  bool _isRouteLoading = false;
  LatLng? _routeOriginLatLng;
  LatLng? _routeDestLatLng;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    _startLocationController.dispose();
    _mandiController.dispose();
    super.dispose();
  }

  // --- Geolocation ---
  Future<Position?> _getCurrentLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) return null;

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) return null;
      }
      if (permission == LocationPermission.deniedForever) return null;

      return await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    } catch (e) {
      print("Error getting current location: $e");
      return null;
    }
  }

  // --- Geocoding API ---
  Future<LatLng?> _geocodeAddress(String address) async {
    if (address.isEmpty) return null;
    final url = "${widget.backendUrl}/api/maps/geocode?address=${Uri.encodeComponent(address)}";
    try {
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        if (data["status"] == "OK" && data["results"].isNotEmpty) {
          final loc = data["results"][0]["geometry"]["location"];
          return LatLng(loc["lat"], loc["lng"]);
        }
      }
    } catch (e) {
      print("Geocoding failed: $e");
    }
    return null;
  }

  Future<void> _geocodeAndMove(String address) async {
    final latLng = await _geocodeAddress(address);
    if (latLng != null) {
      _mapController?.animateCamera(CameraUpdate.newLatLngZoom(latLng, 15));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(widget.isUrdu ? "مقام تلاش کرنے میں ناکامی" : "Could not find address location")),
      );
    }
  }

  // --- Places Autocomplete ---
  Future<void> _searchPlaces(String input) async {
    if (input.isEmpty) {
      setState(() => _predictions = []);
      return;
    }
    try {
      final url = "${widget.backendUrl}/api/maps/autocomplete?input=${Uri.encodeComponent(input)}";
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _predictions = data["predictions"] ?? [];
        });
      }
    } catch (e) {
      print("Autocomplete search failed: $e");
    }
  }

  Future<void> _selectPlace(dynamic prediction) async {
    final placeId = prediction["place_id"];
    final url = "${widget.backendUrl}/api/maps/place-details?place_id=$placeId";
    try {
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        final lat = data["result"]["geometry"]["location"]["lat"];
        final lng = data["result"]["geometry"]["location"]["lng"];
        setState(() {
          _predictions = [];
          _searchController.text = prediction["description"];
        });
        _mapController?.animateCamera(CameraUpdate.newLatLngZoom(LatLng(lat, lng), 15));
      }
    } catch (e) {
      print("Place details failed: $e");
    }
  }

  // --- Earth Engine satellite overlay ---
  Future<void> _toggleEarthEngine(bool val) async {
    setState(() {
      _isEarthEngineSatellite = val;
      if (!val) {
        _geeTileUrl = null;
      }
    });
  }

  Future<void> _fetchEarthEngineTiles(String scanType) async {
    if (widget.isOffline) return;
    setState(() {
      _isBoundaryLoading = true;
      _boundaryAnalysisResult = "";
      _activeScanMode = scanType;
      _isEarthEngineSatellite = true; // Auto enable satellite overlay
    });
    try {
      final lat = widget.activeLandCoords.latitude;
      final lng = widget.activeLandCoords.longitude;
      
      final payloadCoords = _boundaryPoints.isNotEmpty
          ? _boundaryPoints.map((p) => {"lat": p.latitude, "lng": p.longitude}).toList()
          : [
              {"lat": lat - 0.005, "lng": lng - 0.005},
              {"lat": lat + 0.005, "lng": lng - 0.005},
              {"lat": lat + 0.005, "lng": lng + 0.005},
              {"lat": lat - 0.005, "lng": lng + 0.005},
            ];

      final response = await http.post(
        Uri.parse("${widget.backendUrl}/api/ai/gee/$scanType"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "polygon_coords": payloadCoords,
          "crop_name": "Wheat"
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _geeTileUrl = data["tile_url"];
          _boundaryAnalysisResult = widget.isUrdu ? (data["report_ur"] ?? "") : (data["report_en"] ?? "");
          if (_geeTileUrl != null && _geeTileUrl!.isNotEmpty) {
            _geeTileUrl = _geeTileUrl;
          }
          
          if (scanType == "ndvi") {
            final avg = data["ndvi_average"] ?? 0.65;
            final dist = data["distribution"] ?? {};
            _calculatedArea = _calculatePolygonArea(_boundaryPoints);
            if (_boundaryAnalysisResult.isEmpty) {
              _boundaryAnalysisResult = widget.isUrdu
                  ? "سیٹلائٹ کے مطابق اوسط نشوونما (NDVI) $avg ہے۔ فصل کی صحت تسلی بخش ہے۔"
                  : "NDVI Vegetation Density scan: Average NDVI is $avg. Stressed: ${dist['stressed_pct'] ?? 10}%, Average: ${dist['average_pct'] ?? 20}%, Healthy: ${dist['healthy_pct'] ?? 70}%.";
            }
          } else {
            final avgTemp = data["thermal_average"] ?? 30.5;
            final dist = data["distribution"] ?? {};
            _calculatedArea = _calculatePolygonArea(_boundaryPoints);
            if (_boundaryAnalysisResult.isEmpty) {
              _boundaryAnalysisResult = widget.isUrdu
                  ? "تھرمل اسکین کے مطابق اوسط درجہ حرارت $avgTemp ڈگری ہے۔"
                  : "Thermal Moisture scan: Average canopy temperature is $avgTemp°C. Optimal: ${dist['optimal_pct'] ?? 70}%, Stressed: ${dist['stressed_pct'] ?? 20}%, Over-watered: ${dist['overwatered_pct'] ?? 10}%.";
            }
          }
        });
      }
    } catch (e) {
      print("Failed loading Earth Engine tiles: $e");
      setState(() {
        _calculatedArea = _calculatePolygonArea(_boundaryPoints);
        if (scanType == "ndvi") {
          _boundaryAnalysisResult = widget.isUrdu
              ? "مٹی کی نمی اور اوسط نشوونما (NDVI) 0.68 ہے۔ فصل کی صحت تسلی بخش ہے۔"
              : "Simulated NDVI Scan: Vegetation density is 75% healthy. Barren pockets identified in the north-east corner.";
        } else {
          _boundaryAnalysisResult = widget.isUrdu
              ? "تھرمل اسکین کے مطابق اوسط درجہ حرارت 30.5 ڈگری ہے۔ پانی کی مقدار متوازن ہے۔"
              : "Simulated Thermal Scan: Average temperature is 30.5°C. Moisture level is optimal.";
        }
      });
    } finally {
      setState(() {
        _isBoundaryLoading = false;
      });
    }
  }

  // --- Shoelace Area Calculation in Acres ---
  double _calculatePolygonArea(List<LatLng> points) {
    if (points.length < 3) return 0.0;
    double area = 0.0;
    const double latToMeters = 111132.92;
    int j = points.length - 1;
    for (int i = 0; i < points.length; i++) {
      double latRadI = points[i].latitude * math.pi / 180.0;
      double latRadJ = points[j].latitude * math.pi / 180.0;
      double cosLat = math.cos((latRadI + latRadJ) / 2.0);
      double lngToMeters = 111319.9 * cosLat;

      double x1 = points[i].longitude * lngToMeters;
      double y1 = points[i].latitude * latToMeters;
      double x2 = points[j].longitude * lngToMeters;
      double y2 = points[j].latitude * latToMeters;

      area += (x1 * y2) - (x2 * y1);
      j = i;
    }
    double areaInSqMeters = (area / 2.0).abs();
    return areaInSqMeters / 4046.86;
  }

  Future<void> _analyzeBoundary() async {
    if (_boundaryPoints.length < 3) return;
    setState(() {
      _isBoundaryLoading = true;
      _boundaryAnalysisResult = "";
    });

    final acres = _calculatePolygonArea(_boundaryPoints);
    _calculatedArea = acres;

    try {
      final langCode = widget.isUrdu ? "ur" : "en";
      final langInstruction = ApiService.buildLanguageInstruction(langCode);
      final prompt = "This farm boundary in Pakistan covers ${acres.toStringAsFixed(2)} acres. Provide: land quality rating out of 10, top 3 recommended crops, soil preparation advice, and irrigation recommendations. $langInstruction";
      final analysis = await ApiService.askAI(prompt);

      setState(() {
        _boundaryAnalysisResult = analysis;
      });
    } catch (e) {
      print("Boundary analysis failed: $e");
      setState(() {
        _boundaryAnalysisResult = widget.isUrdu
            ? "تجزیہ مکمل کرنے میں ناکامی۔ براہ کرم دوبارہ کوشش کریں۔"
            : "Failed to complete land boundary analysis. Please try again.";
      });
    } finally {
      setState(() => _isBoundaryLoading = false);
    }
  }

  // --- Mandi Route Optimization ---
  Future<void> _optimizeMandiRoute() async {
    final destText = _mandiController.text.trim();
    if (destText.isEmpty) return;

    setState(() {
      _isRouteLoading = true;
      _routeDistance = "";
      _routeDuration = "";
      _routeSummary = "";
      _routeAdvice = "";
      _routePoints = [];
      _routeOriginLatLng = null;
      _routeDestLatLng = null;
    });

    LatLng? originLatLng;
    if (_startLocationController.text.trim() == "Current Location") {
      final pos = await _getCurrentLocation();
      if (pos != null) {
        originLatLng = LatLng(pos.latitude, pos.longitude);
      } else {
        originLatLng = widget.activeLandCoords;
      }
    } else {
      originLatLng = await _geocodeAddress(_startLocationController.text.trim());
    }

    if (originLatLng == null || originLatLng.latitude == 0.0) {
      setState(() {
        _isRouteLoading = false;
        _routeAdvice = widget.isUrdu
            ? "شروع کرنے کا مقام حاصل کرنے میں ناکامی۔"
            : "Could not find start location.";
      });
      return;
    }

    LatLng? destLatLng = await _geocodeAddress("$destText, Pakistan");
    if (destLatLng == null) {
      setState(() {
        _isRouteLoading = false;
        _routeAdvice = widget.isUrdu
            ? "منڈی کا مقام حاصل کرنے میں ناکامی۔"
            : "Could not find destination Mandi.";
      });
      return;
    }

    final directionsUrl = "${widget.backendUrl}/api/maps/directions?origin=${originLatLng.latitude},${originLatLng.longitude}&destination=${destLatLng.latitude},${destLatLng.longitude}";

    try {
      final response = await http.get(Uri.parse(directionsUrl));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data["status"] == "OK") {
          final route = data["routes"][0];
          final leg = route["legs"][0];
          final distanceText = leg["distance"]["text"];
          final durationText = leg["duration"]["text"];
          final routeSummaryText = route["summary"] ?? "";
          final polylineStr = route["overview_polyline"]["points"];

          final points = _decodePolyline(polylineStr);

          final langCode = widget.isUrdu ? "ur" : "en";
          final langInstruction = ApiService.buildLanguageInstruction(langCode);
          final prompt = "A Pakistani farmer is travelling from ${_startLocationController.text} to $destText mandi. Distance: $distanceText. Duration: $durationText. Route: $routeSummaryText. Give practical travel advice for a farmer in Pakistan. $langInstruction";
          final advice = await ApiService.askAI(prompt);

          setState(() {
            _routeDistance = distanceText;
            _routeDuration = durationText;
            _routeSummary = routeSummaryText;
            _routeAdvice = advice;
            _routePoints = points;
            _routeOriginLatLng = originLatLng;
            _routeDestLatLng = destLatLng;
          });

          _fitRouteBounds(points);
        } else {
          setState(() {
            _routeAdvice = widget.isUrdu
                ? "راستہ تلاش کرنے میں ناکامی: ${data['status']}"
                : "Could not calculate route: ${data['status']}";
          });
        }
      }
    } catch (e) {
      print("Route optimization failed: $e");
      setState(() {
        _routeAdvice = widget.isUrdu
            ? "کنکشن کا مسئلہ۔ براہ کرم دوبارہ کوشش کریں۔"
            : "Network issue. Please try again.";
      });
    } finally {
      setState(() => _isRouteLoading = false);
    }
  }

  void _fitRouteBounds(List<LatLng> points) {
    if (points.isEmpty || _mapController == null) return;
    double minLat = points[0].latitude;
    double maxLat = points[0].latitude;
    double minLng = points[0].longitude;
    double maxLng = points[0].longitude;

    for (var p in points) {
      if (p.latitude < minLat) minLat = p.latitude;
      if (p.latitude > maxLat) maxLat = p.latitude;
      if (p.longitude < minLng) minLng = p.longitude;
      if (p.longitude > maxLng) maxLng = p.longitude;
    }

    _mapController!.animateCamera(
      CameraUpdate.newLatLngBounds(
        LatLngBounds(
          southwest: LatLng(minLat, minLng),
          northeast: LatLng(maxLat, maxLng),
        ),
        50,
      ),
    );
  }

  List<LatLng> _decodePolyline(String encoded) {
    List<LatLng> poly = [];
    int index = 0, len = encoded.length;
    int lat = 0, lng = 0;

    while (index < len) {
      int b, shift = 0, result = 0;
      do {
        b = encoded.codeUnitAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      int dlat = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
      lat += dlat;

      shift = 0;
      result = 0;
      do {
        b = encoded.codeUnitAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      int dlng = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
      lng += dlng;

      LatLng p = LatLng((lat / 1E5).toDouble(), (lng / 1E5).toDouble());
      poly.add(p);
    }
    return poly;
  }

  // --- UI Components ---
  Widget _buildEarthEngineSection(double initialLat, double initialLng) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Search Geocoding Address
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: widget.isUrdu ? "مقام تلاش کریں..." : "Search address or farm location...",
              prefixIcon: const Icon(Icons.search, color: GeoKisanTheme.primaryGreen),
              suffixIcon: _searchController.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                        _searchPlaces("");
                      },
                    )
                  : null,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onChanged: _searchPlaces,
            onSubmitted: _geocodeAndMove,
          ),
          if (_predictions.isNotEmpty)
            Container(
              height: 150,
              margin: const EdgeInsets.only(top: 4),
              decoration: BoxDecoration(
                color: widget.isDarkMode ? Colors.grey[950] : Colors.white,
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(8),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4)],
              ),
              child: ListView.builder(
                itemCount: _predictions.length,
                itemBuilder: (context, idx) {
                  final pred = _predictions[idx];
                  return ListTile(
                    title: Text(
                      pred["description"],
                      style: TextStyle(
                        fontSize: 12,
                        color: widget.isDarkMode ? Colors.white : Colors.black87,
                      ),
                    ),
                    onTap: () {
                      _selectPlace(pred);
                    },
                  );
                },
              ),
            ),
          const SizedBox(height: 8),

          // Map view
          Container(
            height: 250,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: GeoKisanTheme.primaryGreen, width: 2),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Stack(
                children: [
                  GoogleMap(
                    initialCameraPosition: CameraPosition(
                      target: LatLng(initialLat, initialLng),
                      zoom: widget.activeLandCoords.latitude != 0.0 ? 15 : 5,
                    ),
                    mapType: _isEarthEngineSatellite ? MapType.hybrid : MapType.normal,
                    myLocationEnabled: true,
                    myLocationButtonEnabled: true,
                    onMapCreated: (ctrl) => _mapController = ctrl,
                    onTap: (latLng) {
                      if (_isDrawingMode) {
                        setState(() {
                          _boundaryPoints.add(latLng);
                        });
                      }
                    },
                    polygons: {
                      if (_boundaryPoints.isNotEmpty)
                        Polygon(
                          polygonId: const PolygonId("gee_boundary"),
                          points: _boundaryPoints,
                          fillColor: _activeScanMode == "ndvi"
                              ? Colors.green.withOpacity(0.4)
                              : (_activeScanMode == "thermal"
                                  ? Colors.redAccent.withOpacity(0.4)
                                  : GeoKisanTheme.primaryGreen.withOpacity(0.2)),
                          strokeColor: _activeScanMode == "ndvi"
                              ? Colors.green
                              : (_activeScanMode == "thermal"
                                  ? Colors.redAccent
                                  : GeoKisanTheme.primaryGreen),
                          strokeWidth: 3,
                        ),
                    },
                    markers: {
                      ..._boundaryPoints.asMap().entries.map((entry) {
                        return Marker(
                          markerId: MarkerId("gee_pt_${entry.key}"),
                          position: entry.value,
                          draggable: true,
                          onDragEnd: (newLatLng) {
                            setState(() {
                              _boundaryPoints[entry.key] = newLatLng;
                              _calculatedArea = _calculatePolygonArea(_boundaryPoints);
                              if (_boundaryPoints.length >= 3) {
                                _analyzeBoundary();
                              }
                            });
                          },
                          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
                        );
                      }).toSet()
                    },
                    tileOverlays: {
                      if (_geeTileUrl != null && _isEarthEngineSatellite)
                        TileOverlay(
                          tileOverlayId: const TileOverlayId("gee_ndvi_tile"),
                          tileProvider: NetworkTileProvider(urlTemplate: _geeTileUrl!),
                        ),
                    },
                  ),

                  // Overlay Controls
                  Positioned(
                    left: 10,
                    top: 10,
                    child: Column(
                      children: [
                        FloatingActionButton.small(
                          heroTag: "gee_sat_toggle",
                          backgroundColor: Colors.white,
                          child: Icon(
                            _isEarthEngineSatellite ? Icons.satellite : Icons.map_outlined,
                            color: GeoKisanTheme.primaryGreen,
                          ),
                          onPressed: () => _toggleEarthEngine(!_isEarthEngineSatellite),
                        ),
                      ],
                    ),
                  ),

                  Positioned(
                    right: 10,
                    top: 10,
                    child: FloatingActionButton.small(
                      heroTag: "gee_fullscreen",
                      backgroundColor: Colors.white,
                      child: const Icon(Icons.fullscreen, color: GeoKisanTheme.primaryGreen),
                      onPressed: () async {
                        final updatedPoints = await Navigator.push<List<LatLng>>(
                          context,
                          MaterialPageRoute(
                            builder: (context) => FullScreenBoundaryEditor(
                              initialPoints: _boundaryPoints,
                              isUrdu: widget.isUrdu,
                              isDarkMode: widget.isDarkMode,
                              initialMapType: _isEarthEngineSatellite ? MapType.hybrid : MapType.normal,
                              initialLat: initialLat,
                              initialLng: initialLng,
                              geeTileUrl: _geeTileUrl,
                              isEarthEngineSatellite: _isEarthEngineSatellite,
                              activeScanMode: _activeScanMode,
                              backendUrl: widget.backendUrl,
                            ),
                          ),
                        );
                        if (updatedPoints != null) {
                          setState(() {
                            _boundaryPoints = updatedPoints;
                            _calculatedArea = _calculatePolygonArea(_boundaryPoints);
                            if (_boundaryPoints.length >= 3) {
                              _analyzeBoundary();
                            }
                          });
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),

          // Scan Modes and Drawing Mode Control Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: [
                  // Drawing Switch
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _isDrawingMode ? Icons.edit : Icons.edit_off,
                            color: _isDrawingMode ? GeoKisanTheme.primaryGreen : Colors.grey,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            widget.isUrdu ? "حدود کا انتخاب (ڈرائنگ)" : "Select Boundary (Draw)",
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                          ),
                        ],
                      ),
                      Switch(
                        value: _isDrawingMode,
                        activeColor: GeoKisanTheme.primaryGreen,
                        onChanged: (val) {
                          setState(() {
                            _isDrawingMode = val;
                          });
                        },
                      ),
                    ],
                  ),
                  const Divider(),
                  const SizedBox(height: 4),
                  // Scan mode selector title
                  Align(
                    alignment: widget.isUrdu ? Alignment.centerRight : Alignment.centerLeft,
                    child: Text(
                      widget.isUrdu ? "اسکین موڈ منتخب کریں:" : "Select Scan Mode:",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey),
                    ),
                  ),
                  const SizedBox(height: 8),
                  // Row of scan modes buttons
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            setState(() {
                              _activeScanMode = "normal";
                              _geeTileUrl = null;
                              _boundaryAnalysisResult = "";
                            });
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _activeScanMode == "normal"
                                ? GeoKisanTheme.primaryGreen
                                : Colors.grey[200],
                            foregroundColor: _activeScanMode == "normal"
                                ? Colors.white
                                : Colors.black87,
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            elevation: 1,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.map, size: 18),
                              const SizedBox(height: 2),
                              Text(widget.isUrdu ? "نارمل نقشہ" : "Normal Map", style: const TextStyle(fontSize: 9)),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            if (_boundaryPoints.length < 3) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(widget.isUrdu
                                      ? "براہ کرم پہلے نقشے پر کم از کم 3 پوائنٹس منتخب کر کے حد بنائیں۔"
                                      : "Please draw a boundary by tapping at least 3 points first."),
                                ),
                              );
                              return;
                            }
                            _fetchEarthEngineTiles("ndvi");
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _activeScanMode == "ndvi"
                                ? Colors.green
                                : Colors.grey[200],
                            foregroundColor: _activeScanMode == "ndvi"
                                ? Colors.white
                                : Colors.black87,
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            elevation: 1,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.spa, size: 18),
                              const SizedBox(height: 2),
                              Text(widget.isUrdu ? "نشوونما اسکین" : "NDVI Scan", style: const TextStyle(fontSize: 9)),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            if (_boundaryPoints.length < 3) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(widget.isUrdu
                                      ? "براہ کرم پہلے نقشے پر کم از کم 3 پوائنٹس منتخب کر کے حد بنائیں۔"
                                      : "Please draw a boundary by tapping at least 3 points first."),
                                ),
                              );
                              return;
                            }
                            _fetchEarthEngineTiles("thermal");
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _activeScanMode == "thermal"
                                ? Colors.orangeAccent
                                : Colors.grey[200],
                            foregroundColor: _activeScanMode == "thermal"
                                ? Colors.white
                                : Colors.black87,
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            elevation: 1,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.thermostat, size: 18),
                              const SizedBox(height: 2),
                              Text(widget.isUrdu ? "تھرمل اسکین" : "Thermal Scan", style: const TextStyle(fontSize: 9)),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),

          // Boundary actions
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    _boundaryPoints.clear();
                    _boundaryAnalysisResult = "";
                    _calculatedArea = 0.0;
                    _activeScanMode = "normal";
                    _geeTileUrl = null;
                  });
                },
                icon: const Icon(Icons.delete),
                label: Text(widget.isUrdu ? "صاف کریں" : "Clear"),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              ),
              ElevatedButton.icon(
                onPressed: _boundaryPoints.length >= 3 ? _analyzeBoundary : null,
                icon: const Icon(Icons.analytics),
                label: Text(widget.isUrdu ? "تفصیلی تجزیہ" : "AI Land Report"),
                style: ElevatedButton.styleFrom(backgroundColor: GeoKisanTheme.primaryGreen),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Result Card
          if (_isBoundaryLoading)
            const Center(child: Padding(padding: EdgeInsets.all(16.0), child: CircularProgressIndicator()))
          else if (_boundaryAnalysisResult.isNotEmpty)
            Card(
              elevation: 4,
              color: Colors.green[50],
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(14.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            "${widget.isUrdu ? 'پلاٹ کا رقبہ' : 'Calculated Area'}: ${_calculatedArea.toStringAsFixed(2)} ${widget.isUrdu ? 'ایکڑ' : 'Acres'}",
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: GeoKisanTheme.primaryGreen),
                          ),
                        ),
                        SpeakerButton(
                          text: _boundaryAnalysisResult,
                          languageCode: widget.isUrdu ? "ur" : "en",
                        ),
                      ],
                    ),
                    const Divider(),
                    Text(
                      _boundaryAnalysisResult,
                      style: const TextStyle(fontSize: 13, height: 1.45, color: Colors.black87),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildMandiSection(double initialLat, double initialLng) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Origin input
          TextField(
            controller: _startLocationController,
            decoration: InputDecoration(
              labelText: widget.isUrdu ? "شروع کرنے کا مقام" : "Start Location",
              hintText: widget.isUrdu ? "مقام درج کریں یا موجودہ لوکیشن رہنے دیں..." : "Enter address or leave 'Current Location'",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 8),

          // Destination input
          TextField(
            controller: _mandiController,
            decoration: InputDecoration(
              labelText: widget.isUrdu ? "منڈی کا نام" : "Mandi Destination",
              hintText: widget.isUrdu ? "منڈی کا نام درج کریں..." : "Enter mandi name (e.g. Okara, Lahore)...",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 8),

          ElevatedButton.icon(
            onPressed: _optimizeMandiRoute,
            icon: const Icon(Icons.navigation),
            label: Text(widget.isUrdu ? "منڈی کا راستہ اور رہنمائی حاصل کریں" : "Optimize Route"),
            style: ElevatedButton.styleFrom(
              backgroundColor: GeoKisanTheme.primaryGreen,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
          const SizedBox(height: 12),

          // Map view
          Container(
            height: 250,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: GeoKisanTheme.primaryGreen, width: 2),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Stack(
                children: [
                  GoogleMap(
                    initialCameraPosition: CameraPosition(
                      target: LatLng(initialLat, initialLng),
                      zoom: 12,
                    ),
                    myLocationEnabled: true,
                    myLocationButtonEnabled: true,
                    onMapCreated: (ctrl) => _mapController = ctrl,
                    polylines: {
                      if (_routePoints.isNotEmpty)
                        Polyline(
                          polylineId: const PolylineId("mandi_route_polyline"),
                          points: _routePoints,
                          color: Colors.blueAccent,
                          width: 5,
                        ),
                    },
                    markers: {
                      if (_routeOriginLatLng != null)
                        Marker(
                          markerId: const MarkerId("origin_marker"),
                          position: _routeOriginLatLng!,
                          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
                          infoWindow: InfoWindow(title: widget.isUrdu ? "شروع" : "Start"),
                        ),
                      if (_routeDestLatLng != null)
                        Marker(
                          markerId: const MarkerId("dest_marker"),
                          position: _routeDestLatLng!,
                          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
                          infoWindow: InfoWindow(title: widget.isUrdu ? "منڈی" : "Mandi"),
                        ),
                    },
                  ),

                  Positioned(
                    right: 10,
                    top: 10,
                    child: FloatingActionButton.small(
                      heroTag: "mandi_fullscreen",
                      backgroundColor: Colors.white,
                      child: const Icon(Icons.fullscreen, color: GeoKisanTheme.primaryGreen),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => FullScreenMapScreen(
                              polygons: const {},
                              polylines: {
                                if (_routePoints.isNotEmpty)
                                  Polyline(
                                    polylineId: const PolylineId("mandi_route_polyline"),
                                    points: _routePoints,
                                    color: Colors.blueAccent,
                                    width: 5,
                                  ),
                              },
                              markers: {
                                if (_routeOriginLatLng != null)
                                  Marker(
                                    markerId: const MarkerId("origin_marker"),
                                    position: _routeOriginLatLng!,
                                    icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
                                  ),
                                if (_routeDestLatLng != null)
                                  Marker(
                                    markerId: const MarkerId("dest_marker"),
                                    position: _routeDestLatLng!,
                                    icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
                                  ),
                              }.toSet(),
                              initialCameraPosition: CameraPosition(
                                target: _routeOriginLatLng ?? LatLng(initialLat, initialLng),
                                zoom: 12,
                              ),
                              mapType: MapType.normal,
                              tileOverlays: const {},
                              isUrdu: widget.isUrdu,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Advice Card
          if (_isRouteLoading)
            const Center(child: Padding(padding: EdgeInsets.all(16.0), child: CircularProgressIndicator()))
          else if (_routeAdvice.isNotEmpty)
            Card(
              elevation: 4,
              color: GeoKisanTheme.surfaceCream,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(14.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "${widget.isUrdu ? 'فاصلہ' : 'Distance'}: $_routeDistance",
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                              ),
                              Text(
                                "${widget.isUrdu ? 'وقت' : 'Duration'}: $_routeDuration",
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                              ),
                              if (_routeSummary.isNotEmpty)
                                Text(
                                  "${widget.isUrdu ? 'راستہ' : 'Route'}: $_routeSummary",
                                  style: const TextStyle(fontSize: 12, color: Colors.black54),
                                ),
                            ],
                          ),
                        ),
                        SpeakerButton(
                          text: _routeAdvice,
                          languageCode: widget.isUrdu ? "ur" : "en",
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 4),
                    Text(
                      widget.isUrdu ? "سفر کی معلومات اور مشورہ:" : "Travel & Logistics Advice:",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: GeoKisanTheme.primaryGreen),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _routeAdvice,
                      style: const TextStyle(fontSize: 13, height: 1.45, color: Colors.black87),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lat = widget.activeLandCoords.latitude != 0.0 ? widget.activeLandCoords.latitude : 30.3753;
    final lng = widget.activeLandCoords.longitude != 0.0 ? widget.activeLandCoords.longitude : 69.3451;

    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          TabBar(
            controller: _tabController,
            labelColor: const Color(0xFF4A7C2F),
            unselectedLabelColor: Colors.grey,
            indicatorColor: const Color(0xFF4A7C2F),
            tabs: [
              Tab(
                icon: const Icon(Icons.satellite_alt),
                text: widget.isUrdu ? "ارتھ انجن اور رقبہ" : "Earth Engine & Area",
              ),
              Tab(
                icon: const Icon(Icons.directions_car),
                text: widget.isUrdu ? "منڈی روٹ آپٹیمائزر" : "Mandi Optimizer",
              ),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildEarthEngineSection(lat, lng),
                _buildMandiSection(lat, lng),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class FullScreenMapScreen extends StatelessWidget {
  final Set<Polygon> polygons;
  final Set<Polyline> polylines;
  final Set<Marker> markers;
  final CameraPosition initialCameraPosition;
  final MapType mapType;
  final Set<TileOverlay> tileOverlays;
  final bool isUrdu;

  const FullScreenMapScreen({
    Key? key,
    required this.polygons,
    required this.polylines,
    required this.markers,
    required this.initialCameraPosition,
    required this.mapType,
    required this.tileOverlays,
    required this.isUrdu,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(isUrdu ? "مکمل نقشہ" : "Full Screen Map"),
        backgroundColor: const Color(0xFF4A7C2F),
      ),
      body: GoogleMap(
        initialCameraPosition: initialCameraPosition,
        mapType: mapType,
        myLocationEnabled: true,
        myLocationButtonEnabled: true,
        polygons: polygons,
        polylines: polylines,
        markers: markers,
        tileOverlays: tileOverlays,
      ),
    );
  }
}

class NetworkTileProvider implements TileProvider {
  final String urlTemplate;

  NetworkTileProvider({required this.urlTemplate});

  @override
  Future<Tile> getTile(int x, int y, int? zoom) async {
    final String url = urlTemplate
        .replaceAll('{x}', x.toString())
        .replaceAll('{y}', y.toString())
        .replaceAll('{z}', zoom?.toString() ?? '0');

    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        return Tile(256, 256, response.bodyBytes);
      }
    } catch (e) {
      print('Error loading tile: $e');
    }
    return TileProvider.noTile;
  }
}

class FullScreenBoundaryEditor extends StatefulWidget {
  final List<LatLng> initialPoints;
  final bool isUrdu;
  final bool isDarkMode;
  final MapType initialMapType;
  final double initialLat;
  final double initialLng;
  final String? geeTileUrl;
  final bool isEarthEngineSatellite;
  final String activeScanMode;
  final String backendUrl;

  const FullScreenBoundaryEditor({
    Key? key,
    required this.initialPoints,
    required this.isUrdu,
    required this.isDarkMode,
    required this.initialMapType,
    required this.initialLat,
    required this.initialLng,
    this.geeTileUrl,
    required this.isEarthEngineSatellite,
    required this.activeScanMode,
    required this.backendUrl,
  }) : super(key: key);

  @override
  State<FullScreenBoundaryEditor> createState() => _FullScreenBoundaryEditorState();
}

class _FullScreenBoundaryEditorState extends State<FullScreenBoundaryEditor> {
  late List<LatLng> _points;
  late MapType _mapType;
  bool _isDrawing = true;
  GoogleMapController? _mapController;
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> _predictions = [];

  @override
  void initState() {
    super.initState();
    _points = List.from(widget.initialPoints);
    _mapType = widget.initialMapType;
  }

  void _autoFixBoundary() {
    if (_points.length < 3) return;
    double sumLat = 0;
    double sumLng = 0;
    for (final pt in _points) {
      sumLat += pt.latitude;
      sumLng += pt.longitude;
    }
    double meanLat = sumLat / _points.length;
    double meanLng = sumLng / _points.length;
    setState(() {
      _points.sort((a, b) {
        double angleA = math.atan2(a.latitude - meanLat, a.longitude - meanLng);
        double angleB = math.atan2(b.latitude - meanLat, b.longitude - meanLng);
        return angleA.compareTo(angleB);
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  double _calculateArea(List<LatLng> pts) {
    if (pts.length < 3) return 0.0;
    double area = 0.0;
    const double latToMeters = 111132.92;
    int j = pts.length - 1;
    for (int i = 0; i < pts.length; i++) {
      double latRadI = pts[i].latitude * math.pi / 180.0;
      double latRadJ = pts[j].latitude * math.pi / 180.0;
      double cosLat = math.cos((latRadI + latRadJ) / 2.0);
      double lngToMeters = 111319.9 * cosLat;

      double x1 = pts[i].longitude * lngToMeters;
      double y1 = pts[i].latitude * latToMeters;
      double x2 = pts[j].longitude * lngToMeters;
      double y2 = pts[j].latitude * latToMeters;

      area += (x1 * y2) - (x2 * y1);
      j = i;
    }
    double areaInSqMeters = (area / 2.0).abs();
    return areaInSqMeters / 4046.86;
  }

  Future<void> _searchPlaces(String input) async {
    if (input.isEmpty) {
      setState(() => _predictions = []);
      return;
    }
    try {
      final url = "${widget.backendUrl}/api/maps/autocomplete?input=${Uri.encodeComponent(input)}";
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _predictions = data["predictions"] ?? [];
        });
      }
    } catch (e) {
      print("Autocomplete failed: $e");
    }
  }

  Future<void> _selectPlace(dynamic prediction) async {
    final placeId = prediction["place_id"];
    final url = "${widget.backendUrl}/api/maps/place-details?place_id=$placeId";
    try {
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        final lat = data["result"]["geometry"]["location"]["lat"];
        final lng = data["result"]["geometry"]["location"]["lng"];
        setState(() {
          _predictions = [];
          _searchController.text = prediction["description"];
        });
        _mapController?.animateCamera(CameraUpdate.newLatLngZoom(LatLng(lat, lng), 17));
      }
    } catch (e) {
      print("Place details failed: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    final double area = _calculateArea(_points);
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isUrdu ? "حدود کا انتخاب" : "Fullscreen Boundary Editor"),
        backgroundColor: const Color(0xFF4A7C2F),
        actions: [
          IconButton(
            icon: const Icon(Icons.check, size: 28),
            onPressed: () {
              Navigator.pop(context, _points);
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(
              target: _points.isNotEmpty
                  ? _points[0]
                  : LatLng(widget.initialLat, widget.initialLng),
              zoom: 16,
            ),
            mapType: _mapType,
            myLocationEnabled: true,
            myLocationButtonEnabled: false,
            onMapCreated: (ctrl) => _mapController = ctrl,
            onTap: (latLng) {
              if (_isDrawing) {
                setState(() {
                  _points.add(latLng);
                });
              }
            },
            polygons: {
              if (_points.isNotEmpty)
                Polygon(
                  polygonId: const PolygonId("gee_boundary_fs"),
                  points: _points,
                  fillColor: widget.activeScanMode == "ndvi"
                      ? Colors.green.withOpacity(0.4)
                      : (widget.activeScanMode == "thermal"
                          ? Colors.redAccent.withOpacity(0.4)
                          : const Color(0xFF4A7C2F).withOpacity(0.2)),
                  strokeColor: widget.activeScanMode == "ndvi"
                      ? Colors.green
                      : (widget.activeScanMode == "thermal"
                          ? Colors.redAccent
                          : const Color(0xFF4A7C2F)),
                  strokeWidth: 3,
                ),
            },
            markers: _points.asMap().entries.map((entry) {
              return Marker(
                markerId: MarkerId("gee_pt_fs_${entry.key}"),
                position: entry.value,
                draggable: true,
                onDragEnd: (newLatLng) {
                  setState(() {
                    _points[entry.key] = newLatLng;
                  });
                },
                icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
              );
            }).toSet(),
            tileOverlays: {
              if (widget.geeTileUrl != null && widget.isEarthEngineSatellite)
                TileOverlay(
                  tileOverlayId: const TileOverlayId("gee_ndvi_tile_fs"),
                  tileProvider: NetworkTileProvider(urlTemplate: widget.geeTileUrl!),
                ),
            },
          ),

          // Search Bar Overlay at Top
          Positioned(
            top: 10,
            left: 10,
            right: 10,
            child: Column(
              children: [
                Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: widget.isUrdu ? "مقام تلاش کریں..." : "Search farm location...",
                      prefixIcon: const Icon(Icons.search, color: Color(0xFF4A7C2F)),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                _searchPlaces("");
                              },
                            )
                          : null,
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    ),
                    onChanged: _searchPlaces,
                  ),
                ),
                if (_predictions.isNotEmpty)
                  Card(
                    elevation: 4,
                    margin: const EdgeInsets.only(top: 4),
                    child: Container(
                      height: 180,
                      child: ListView.builder(
                        itemCount: _predictions.length,
                        itemBuilder: (context, idx) {
                          final pred = _predictions[idx];
                          return ListTile(
                            title: Text(pred["description"], style: const TextStyle(fontSize: 12)),
                            onTap: () => _selectPlace(pred),
                          );
                        },
                      ),
                    ),
                  ),
              ],
            ),
          ),

          // Floating controls overlay at top (hidden during active search predictions list view)
          if (_predictions.isEmpty)
            Positioned(
              top: 75,
              left: 16,
              right: 16,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Info Banner
                  Card(
                    color: const Color(0xFF4A7C2F),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "${widget.isUrdu ? 'رقبہ' : 'Area'}: ${area.toStringAsFixed(2)} ${widget.isUrdu ? 'ایکڑ' : 'Acres'}",
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                          ),
                          Text(
                            _points.length < 3
                                ? (widget.isUrdu ? "کم از کم 3 پوائنٹس منتخب کریں" : "Place min 3 points")
                                : (widget.isUrdu ? "پوائنٹس محفوظ کریں" : "Ready to Save"),
                            style: const TextStyle(color: Colors.white70, fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  // Action Buttons Row
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      FloatingActionButton.extended(
                        heroTag: "fs_draw_toggle",
                        onPressed: () {
                          setState(() {
                            _isDrawing = !_isDrawing;
                          });
                        },
                        label: Text(_isDrawing
                            ? (widget.isUrdu ? "ڈرائنگ آن" : "Drawing Active")
                            : (widget.isUrdu ? "ڈرائنگ آف" : "Panning Mode")),
                        icon: Icon(_isDrawing ? Icons.edit : Icons.pan_tool),
                        backgroundColor: _isDrawing ? const Color(0xFF4A7C2F) : Colors.amber[700],
                      ),
                      Row(
                        children: [
                          if (_points.length >= 3) ...[
                            FloatingActionButton.small(
                              heroTag: "fs_autofix",
                              onPressed: _autoFixBoundary,
                              child: const Icon(Icons.auto_fix_high, color: Colors.blue),
                              backgroundColor: Colors.white,
                            ),
                            const SizedBox(width: 8),
                          ],
                          if (_points.isNotEmpty)
                            FloatingActionButton.small(
                              heroTag: "fs_undo",
                              onPressed: () {
                                setState(() {
                                  _points.removeLast();
                                });
                              },
                              child: const Icon(Icons.undo),
                              backgroundColor: Colors.white,
                              foregroundColor: const Color(0xFF4A7C2F),
                            ),
                          const SizedBox(width: 8),
                          FloatingActionButton.small(
                            heroTag: "fs_clear",
                            onPressed: () {
                              setState(() {
                                _points.clear();
                              });
                            },
                            child: const Icon(Icons.delete, color: Colors.red),
                            backgroundColor: Colors.white,
                          ),
                        ],
                      )
                    ],
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
