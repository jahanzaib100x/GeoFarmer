import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../theme/geokisan_theme.dart';

class InteractiveGoogleMapSelector extends StatefulWidget {
  final double initialLat;
  final double initialLng;
  final Function(double lat, double lng) onLocationSelected;
  final bool isUrdu;

  const InteractiveGoogleMapSelector({
    Key? key,
    required this.initialLat,
    required this.initialLng,
    required this.onLocationSelected,
    required this.isUrdu,
  }) : super(key: key);

  @override
  State<InteractiveGoogleMapSelector> createState() => _InteractiveGoogleMapSelectorState();
}

class _InteractiveGoogleMapSelectorState extends State<InteractiveGoogleMapSelector> {
  GoogleMapController? _mapController;
  late double _currentLat;
  late double _currentLng;
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> _predictions = [];

  @override
  void initState() {
    super.initState();
    _currentLat = widget.initialLat != 0.0 ? widget.initialLat : 30.3753;
    _currentLng = widget.initialLng != 0.0 ? widget.initialLng : 69.3451;
  }

  Future<void> _searchPlaces(String input) async {
    if (input.isEmpty) {
      setState(() {
        _predictions = [];
      });
      return;
    }
    try {
      final key = "AIzaSyDfPBczkgH0rSxV9EDm8WM33yfN_FFfLF0";
      final url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${Uri.encodeComponent(input)}&key=$key&components=country:pk";
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _predictions = data["predictions"] ?? [];
        });
      }
    } catch (e) {
      print("Places autocomplete failed: $e");
    }
  }

  Future<void> _selectPlace(dynamic prediction) async {
    final placeId = prediction["place_id"];
    final key = "AIzaSyDfPBczkgH0rSxV9EDm8WM33yfN_FFfLF0";
    final url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=$placeId&key=$key";
    try {
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        final lat = data["result"]["geometry"]["location"]["lat"];
        final lng = data["result"]["geometry"]["location"]["lng"];
        setState(() {
          _currentLat = lat;
          _currentLng = lng;
          _predictions = [];
          _searchController.text = prediction["description"];
        });
        widget.onLocationSelected(lat, lng);
        _mapController?.animateCamera(CameraUpdate.newLatLngZoom(LatLng(lat, lng), 15));
      }
    } catch (e) {
      print("Place details failed: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: widget.isUrdu ? "مقام تلاش کریں..." : "Search location...",
            prefixIcon: const Icon(Icons.search),
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      _searchController.clear();
                      _searchPlaces("");
                    },
                  )
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
        Container(
          height: 180,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: GeoKisanTheme.primaryGreen, width: 2),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: Stack(
              children: [
                GoogleMap(
                  initialCameraPosition: CameraPosition(
                    target: LatLng(_currentLat, _currentLng),
                    zoom: widget.initialLat != 0.0 ? 14 : 5,
                  ),
                  myLocationEnabled: true,
                  myLocationButtonEnabled: true,
                  onMapCreated: (ctrl) => _mapController = ctrl,
                  onTap: (latLng) {
                    setState(() {
                      _currentLat = latLng.latitude;
                      _currentLng = latLng.longitude;
                    });
                    widget.onLocationSelected(latLng.latitude, latLng.longitude);
                  },
                  markers: {
                    Marker(
                      markerId: const MarkerId("selected_loc"),
                      position: LatLng(_currentLat, _currentLng),
                    ),
                  },
                ),
                Positioned(
                  right: 8,
                  top: 8,
                  child: FloatingActionButton.small(
                    heroTag: "fullscreen_btn_${widget.initialLat}_${widget.initialLng}",
                    backgroundColor: Colors.white,
                    child: const Icon(Icons.fullscreen, color: GeoKisanTheme.primaryGreen),
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => FullScreenMapPage(
                            initialLat: _currentLat,
                            initialLng: _currentLng,
                            isUrdu: widget.isUrdu,
                            onLocationSelected: (lat, lng) {
                              setState(() {
                                _currentLat = lat;
                                _currentLng = lng;
                              });
                              widget.onLocationSelected(lat, lng);
                              _mapController?.animateCamera(CameraUpdate.newLatLngZoom(LatLng(lat, lng), 15));
                            },
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
      ],
    );
  }
}

class FullScreenMapPage extends StatefulWidget {
  final double initialLat;
  final double initialLng;
  final bool isUrdu;
  final Function(double lat, double lng) onLocationSelected;

  const FullScreenMapPage({
    Key? key,
    required this.initialLat,
    required this.initialLng,
    required this.isUrdu,
    required this.onLocationSelected,
  }) : super(key: key);

  @override
  State<FullScreenMapPage> createState() => _FullScreenMapPageState();
}

class _FullScreenMapPageState extends State<FullScreenMapPage> {
  GoogleMapController? _mapController;
  late double _currentLat;
  late double _currentLng;

  @override
  void initState() {
    super.initState();
    _currentLat = widget.initialLat;
    _currentLng = widget.initialLng;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isUrdu ? "نقشہ" : "Fullscreen Map"),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: GoogleMap(
        initialCameraPosition: CameraPosition(
          target: LatLng(_currentLat, _currentLng),
          zoom: 15,
        ),
        myLocationEnabled: true,
        myLocationButtonEnabled: true,
        onMapCreated: (ctrl) => _mapController = ctrl,
        onTap: (latLng) {
          setState(() {
            _currentLat = latLng.latitude;
            _currentLng = latLng.longitude;
          });
          widget.onLocationSelected(latLng.latitude, latLng.longitude);
        },
        markers: {
          Marker(
            markerId: const MarkerId("selected_loc"),
            position: LatLng(_currentLat, _currentLng),
          ),
        },
      ),
    );
  }
}
