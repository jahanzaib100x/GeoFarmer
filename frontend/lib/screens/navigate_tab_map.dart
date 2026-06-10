import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math' as math;
import '../theme/geokisan_theme.dart';
import '../services/ai_service.dart';
import '../services/voice_service.dart';

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

class _NavigateTabMapWorkspaceState extends State<NavigateTabMapWorkspace> {
  GoogleMapController? _mapController;
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _mandiController = TextEditingController();
  final VoiceService _voiceService = VoiceService();

  List<dynamic> _predictions = [];
  bool _isEarthEngineSatellite = false;
  String? _geeTileUrl;

  // Boundary Drawing State
  List<LatLng> _boundaryPoints = [];
  bool _isDrawingMode = false;
  double _calculatedArea = 0.0;
  String _boundaryAnalysisResult = "";
  bool _isBoundaryLoading = false;

  // Mandi Routing State
  List<LatLng> _routePoints = [];
  String _routeDistance = "";
  String _routeDuration = "";
  List<String> _routeKeyRoads = [];
  String _routeAdviceEn = "";
  String _routeAdviceUr = "";
  bool _isRouteLoading = false;

  @override
  void initState() {
    super.initState();
  }

  // --- Places Autocomplete & Navigation ---
  Future<void> _searchPlaces(String input) async {
    if (input.isEmpty) {
      setState(() => _predictions = []);
      return;
    }
    try {
      const key = "AIzaSyDfPBczkgH0rSxV9EDm8WM33yfN_FFfLF0";
      final url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${Uri.encodeComponent(input)}&key=$key&components=country:pk";
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
    const key = "AIzaSyDfPBczkgH0rSxV9EDm8WM33yfN_FFfLF0";
    final url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=$placeId&key=$key";
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

  // --- Google Earth Engine Satellite Tiles Loading ---
  Future<void> _toggleEarthEngine(bool val) async {
    setState(() {
      _isEarthEngineSatellite = val;
      if (val) {
        _fetchEarthEngineTiles();
      } else {
        _geeTileUrl = null;
      }
    });
  }

  Future<void> _fetchEarthEngineTiles() async {
    if (widget.isOffline) return;
    try {
      // call NDVI or Thermal endpoint with standard polygon surrounding active land to get satellite tiles
      final lat = widget.activeLandCoords.latitude;
      final lng = widget.activeLandCoords.longitude;
      final response = await http.post(
        Uri.parse("${widget.backendUrl}/api/ai/gee/ndvi"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "polygon_coords": [
            {"lat": lat - 0.005, "lng": lng - 0.005},
            {"lat": lat + 0.005, "lng": lng - 0.005},
            {"lat": lat + 0.005, "lng": lng + 0.005},
            {"lat": lat - 0.005, "lng": lng + 0.005},
          ]
        }),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _geeTileUrl = data["tile_url"];
        });
      }
    } catch (e) {
      print("Failed loading Earth Engine tiles: $e");
    }
  }

  // --- Mandi Route Optimization ---
  Future<void> _optimizeMandiRoute() async {
    final dest = _mandiController.text.trim();
    if (dest.isEmpty) return;

    setState(() {
      _isRouteLoading = true;
      _routeKeyRoads = [];
      _routeAdviceEn = "";
      _routeAdviceUr = "";
      _routePoints = [];
    });

    final originLat = widget.activeLandCoords.latitude;
    final originLng = widget.activeLandCoords.longitude;
    const mapsKey = "AIzaSyDfPBczkgH0rSxV9EDm8WM33yfN_FFfLF0";
    final directionsUrl = "https://maps.googleapis.com/maps/api/directions/json?origin=$originLat,$originLng&destination=${Uri.encodeComponent(dest)}&key=$mapsKey";

    try {
      final response = await http.get(Uri.parse(directionsUrl));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data["status"] == "OK") {
          final route = data["routes"][0];
          final leg = route["legs"][0];
          final distanceText = leg["distance"]["text"];
          final durationText = leg["duration"]["text"];
          final polylineStr = route["overview_polyline"]["points"];

          // Decode Polyline points
          final points = _decodePolyline(polylineStr);

          // Get AI Advice
          final prompt = "Generate travel and logistics advice for a farmer transporting crops in Pakistan from coordinates ($originLat, $originLng) to mandi: '$dest'. Route distance: $distanceText, duration: $durationText. Suggest highway routes, bypasses, safety tips, and estimated fuel load requirements. You MUST respond with a raw JSON object containing exactly these fields: "
              "{"
              "  \"key_roads\": [\"Road Name 1\", \"Road Name 2\"],"
              "  \"advice_en\": \"Detailed English logistics and routing advice...\","
              "  \"advice_ur\": \"منڈی تک جانے کا تفصیلی مشورہ اور رہنمائی...\""
              "} "
              "Do not use markdown wrappers or code block decorators.";
          final advice = await AIService.generateContent(prompt);

          String cleanAdvice = advice.trim();
          if (cleanAdvice.startsWith("```json")) {
            cleanAdvice = cleanAdvice.substring(7);
          }
          if (cleanAdvice.endsWith("```")) {
            cleanAdvice = cleanAdvice.substring(0, cleanAdvice.length - 3);
          }
          cleanAdvice = cleanAdvice.trim();

          List<String> roads = [];
          String adviceEn = advice;
          String adviceUr = advice;

          try {
            final parsedJson = json.decode(cleanAdvice);
            roads = List<String>.from(parsedJson["key_roads"] ?? []);
            adviceEn = parsedJson["advice_en"] ?? advice;
            adviceUr = parsedJson["advice_ur"] ?? advice;
          } catch (e) {
            print("Failed to decode JSON advice: $e");
          }

          setState(() {
            _routeDistance = distanceText;
            _routeDuration = durationText;
            _routeKeyRoads = roads;
            _routeAdviceEn = adviceEn;
            _routeAdviceUr = adviceUr;
            _routePoints = points;
          });

          // Auto-play TTS advice
          final speakText = widget.isUrdu ? adviceUr : adviceEn;
          _voiceService.speak(speakText, widget.isUrdu ? "ur" : "en");

          // Fit bounds to show route
          _fitRouteBounds(points);
        } else {
          setState(() {
            _routeAdviceEn = "Could not calculate route: ${data['status']}";
            _routeAdviceUr = "راستہ تلاش کرنے میں ناکامی: ${data['status']}";
          });
        }
      }
    } catch (e) {
      print("Route optimization failed: $e");
      setState(() {
        _routeAdviceEn = "Failed fetching route. Try again.";
        _routeAdviceUr = "راستہ تلاش کرنے میں ناکامی۔ دوبارہ کوشش کریں۔";
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

  List<LatLng> _decodePolyline(String poly) {
    var list = poly.codeUnits;
    var lList = <double>[];
    int index = 0;
    int len = poly.length;
    int c = 0;
    int lat = 0;
    int lng = 0;
    while (index < len) {
      int shift = 0;
      int result = 0;
      while (true) {
        c = list[index++] - 63;
        result |= (c & 0x1F) << shift;
        shift += 5;
        if (c < 0x20) break;
      }
      int dlat = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
      lat += dlat;
      shift = 0;
      result = 0;
      while (true) {
        c = list[index++] - 63;
        result |= (c & 0x1F) << shift;
        shift += 5;
        if (c < 0x20) break;
      }
      int dlng = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
      lng += dlng;
      lList.add(lat / 1E5);
      lList.add(lng / 1E5);
    }
    List<LatLng> points = [];
    for (int i = 0; i < lList.length; i += 2) {
      points.add(LatLng(lList[i], lList[i + 1]));
    }
    return points;
  }

  // --- Draw Boundary & NDVI Analysis ---
  double _calculatePolygonArea(List<LatLng> points) {
    if (points.length < 3) return 0.0;
    double area = 0.0;
    int j = points.length - 1;
    for (int i = 0; i < points.length; i++) {
      double x1 = points[i].longitude * 111320.0 * math.cos(points[i].latitude * math.pi / 180.0);
      double y1 = points[i].latitude * 110540.0;
      double x2 = points[j].longitude * 111320.0 * math.cos(points[j].latitude * math.pi / 180.0);
      double y2 = points[j].latitude * 110540.0;
      area += (x2 + x1) * (y2 - y1);
      j = i;
    }
    double areaInSqMeters = (area / 2.0).abs();
    return areaInSqMeters / 4046.86; // convert to acres
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
      double ndviAvg = 0.62;
      // Get live NDVI from GEE
      if (!widget.isOffline) {
        final res = await http.post(
          Uri.parse("${widget.backendUrl}/api/ai/gee/ndvi"),
          headers: {"Content-Type": "application/json"},
          body: json.encode({
            "polygon_coords": _boundaryPoints.map((p) => {"lat": p.latitude, "lng": p.longitude}).toList(),
            "crop_name": "Wheat"
          }),
        );
        if (res.statusCode == 200) {
          final data = json.decode(res.body);
          ndviAvg = data["ndvi_average"] ?? 0.62;
        }
      }

      // Query Gemini/DeepSeek
      final prompt = "Assess land quality for a Pakistan farm of ${acres.toStringAsFixed(2)} acres with average NDVI index of $ndviAvg. Suggest 3 best crops, soil enrichment tips, and preparation calendar. Keep response practical and concise.";
      final analysis = await AIService.generateContent(prompt);

      setState(() {
        _boundaryAnalysisResult = analysis;
      });

      // Auto-play TTS
      _voiceService.speak(analysis, widget.isUrdu ? "ur" : "en");
    } catch (e) {
      print("Boundary analysis failed: $e");
      setState(() {
        _boundaryAnalysisResult = "Failed to run NDVI analysis. Standard land quality estimated at moderate value.";
      });
    } finally {
      setState(() => _isBoundaryLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final lat = widget.activeLandCoords.latitude != 0.0 ? widget.activeLandCoords.latitude : 30.3753;
    final lng = widget.activeLandCoords.longitude != 0.0 ? widget.activeLandCoords.longitude : 69.3451;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Places Search Autocomplete
        TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: widget.isUrdu ? "مقام تلاش کریں..." : "Search places/farms...",
            prefixIcon: const Icon(Icons.search, color: GeoKisanTheme.primaryGreen),
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(icon: const Icon(Icons.clear), onPressed: () { _searchController.clear(); _searchPlaces(""); })
                : null,
            border: const OutlineInputBorder(),
          ),
          onChanged: _searchPlaces,
        ),
        if (_predictions.isNotEmpty)
          Container(
            height: 150,
            margin: const EdgeInsets.only(top: 4),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: Colors.grey[300]!),
              borderRadius: BorderRadius.circular(4),
            ),
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
        const SizedBox(height: 8),

        // Map workspace
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
                    target: LatLng(lat, lng),
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
                    if (_boundaryPoints.length >= 3)
                      Polygon(
                        polygonId: const PolygonId("drawn_boundary"),
                        points: _boundaryPoints,
                        fillColor: GeoKisanTheme.primaryGreen.withOpacity(0.18),
                        strokeColor: GeoKisanTheme.primaryGreen,
                        strokeWidth: 3,
                      ),
                  },
                  polylines: {
                    if (_routePoints.isNotEmpty)
                      Polyline(
                        polylineId: const PolylineId("mandi_route"),
                        points: _routePoints,
                        color: Colors.blueAccent,
                        width: 5,
                      ),
                  },
                  markers: {
                    Marker(
                      markerId: const MarkerId("center_marker"),
                      position: LatLng(lat, lng),
                      icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
                    ),
                    ..._boundaryPoints.asMap().entries.map((entry) {
                      return Marker(
                        markerId: MarkerId("b_point_${entry.key}"),
                        position: entry.value,
                        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange),
                      );
                    }).toSet()
                  },
                  tileOverlays: {
                    if (_geeTileUrl != null && _isEarthEngineSatellite)
                      TileOverlay(
                        tileOverlayId: const TileOverlayId("gee_ndvi_overlay"),
                        tileProvider: NetworkTileProvider(urlTemplate: _geeTileUrl!),
                      ),
                  },
                ),

                // Controls overlaid on Map
                Positioned(
                  left: 10,
                  top: 10,
                  child: Column(
                    children: [
                      FloatingActionButton.small(
                        heroTag: "satellite_toggle",
                        backgroundColor: Colors.white,
                        child: Icon(
                          _isEarthEngineSatellite ? Icons.satellite : Icons.map_outlined,
                          color: GeoKisanTheme.primaryGreen,
                        ),
                        onPressed: () => _toggleEarthEngine(!_isEarthEngineSatellite),
                      ),
                      const SizedBox(height: 6),
                      FloatingActionButton.small(
                        heroTag: "draw_mode_toggle",
                        backgroundColor: _isDrawingMode ? GeoKisanTheme.primaryGreen : Colors.white,
                        child: Icon(
                          Icons.edit,
                          color: _isDrawingMode ? Colors.white : GeoKisanTheme.primaryGreen,
                        ),
                        onPressed: () {
                          setState(() {
                            _isDrawingMode = !_isDrawingMode;
                            if (!_isDrawingMode) {
                              _analyzeBoundary();
                            }
                          });
                        },
                      ),
                    ],
                  ),
                ),
                Positioned(
                  right: 10,
                  top: 10,
                  child: FloatingActionButton.small(
                    heroTag: "fullscreen_toggle_navigate",
                    backgroundColor: Colors.white,
                    child: const Icon(Icons.fullscreen, color: GeoKisanTheme.primaryGreen),
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => Scaffold(
                            appBar: AppBar(
                              title: Text(widget.isUrdu ? "تفصیلی نقشہ" : "Geospatial Workspace"),
                              leading: IconButton(
                                icon: const Icon(Icons.arrow_back),
                                onPressed: () => Navigator.pop(context),
                              ),
                            ),
                            body: NavigateTabMapWorkspace(
                              activeLandCoords: widget.activeLandCoords,
                              isUrdu: widget.isUrdu,
                              isDarkMode: widget.isDarkMode,
                              backendUrl: widget.backendUrl,
                              isOffline: widget.isOffline,
                            ),
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

        // Mandi Route Optimizer Card
        Card(
          elevation: 3,
          color: GeoKisanTheme.surfaceCream,
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  widget.isUrdu ? "منڈی روٹ آپٹیمائزر" : "Mandi Route Optimizer",
                  style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _mandiController,
                        decoration: InputDecoration(
                          hintText: widget.isUrdu ? "منڈی کا نام درج کریں..." : "Enter destination Mandi name...",
                          border: const OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: GeoKisanTheme.primaryGreen),
                      onPressed: _optimizeMandiRoute,
                      child: Text(widget.isUrdu ? "راستہ تلاش کریں" : "Get Route"),
                    ),
                  ],
                ),
                if (_isRouteLoading)
                  const Padding(padding: EdgeInsets.all(8.0), child: Center(child: CircularProgressIndicator()))
                else if (_routeAdviceEn.isNotEmpty || _routeAdviceUr.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "${widget.isUrdu ? 'فاصلہ' : 'Distance'}: $_routeDistance | ${widget.isUrdu ? 'وقت' : 'Duration'}: $_routeDuration",
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                      IconButton(
                        icon: const Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen),
                        onPressed: () {
                          final speakText = widget.isUrdu ? _routeAdviceUr : _routeAdviceEn;
                          _voiceService.speak(speakText, widget.isUrdu ? "ur" : "en");
                        },
                      ),
                    ],
                  ),
                  if (_routeKeyRoads.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      widget.isUrdu ? "اہم شاہراہیں / سڑکیں:" : "Key Roads & Bypasses:",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: GeoKisanTheme.primaryGreen),
                    ),
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: _routeKeyRoads.map((road) => Chip(
                        label: Text(road, style: const TextStyle(fontSize: 11)),
                        backgroundColor: GeoKisanTheme.primaryGreen.withOpacity(0.08),
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      )).toList(),
                    ),
                  ],
                  const SizedBox(height: 10),
                  Text(
                    widget.isUrdu ? _routeAdviceUr : _routeAdviceEn,
                    style: const TextStyle(fontSize: 12, height: 1.45),
                  ),
                ]
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Boundary Drawing details
        if (_isBoundaryLoading)
          const Center(child: CircularProgressIndicator())
        else if (_boundaryAnalysisResult.isNotEmpty)
          Card(
            elevation: 3,
            color: Colors.green[50],
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "${widget.isUrdu ? 'پلاٹ کی پیمائش' : 'Drawn Plot Area'}: ${_calculatedArea.toStringAsFixed(2)} ${widget.isUrdu ? 'ایکڑ' : 'Acres'}",
                        style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen),
                      ),
                      IconButton(
                        icon: const Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen),
                        onPressed: () => _voiceService.speak(_boundaryAnalysisResult, widget.isUrdu ? "ur" : "en"),
                      ),
                    ],
                  ),
                  const Divider(),
                  Text(_boundaryAnalysisResult, style: const TextStyle(fontSize: 12, height: 1.4)),
                ],
              ),
            ),
          ),
      ],
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
