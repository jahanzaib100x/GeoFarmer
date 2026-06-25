import re

with open('frontend/lib/main.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# Add _geeTileUrl to state
content = content.replace('String _geeReportUr = "";', 'String _geeReportUr = "";\n  String _geeTileUrl = "";')

# Update _fetchGeeScan to capture tile_url
fetch_new = '''          setState(() {
            _geeReportUr = data["report_ur"] ?? "";
            _geeReportEn = data["report_en"] ?? "";
            _geeTileUrl = data["tile_url"] ?? "";
            _isLoadingGee = false;
          });'''
content = content.replace('''          setState(() {
            _geeReportUr = data["report_ur"] ?? "";
            _geeReportEn = data["report_en"] ?? "";
            _isLoadingGee = false;
          });''', fetch_new)

# Update GoogleMap to add tileOverlays
google_map_str = '''GoogleMap(
                    initialCameraPosition: CameraPosition(
                      target: LatLng(widget.activeLand.latitude, widget.activeLand.longitude),
                      zoom: 16.0,
                    ),
                    onMapCreated: (ctrl) => _mapController = ctrl,
                    onTap: (latLng) {
                      if (_isClosed) return;
                      setState(() {
                        _gpsPoints.add(latLng);
                        final Size size = const Size(350, 300);
                        _points.add(_latLngToPixel(latLng, size));
                      });
                    },
                    polygons: _gpsPoints.length >= 3
                        ? {
                            Polygon(
                              polygonId: const PolygonId("farm_boundary"),
                              points: _gpsPoints,
                              fillColor: _analysisType == "none" ? Colors.green.withOpacity(0.2) : Colors.transparent,
                              strokeColor: Colors.green,
                              strokeWidth: 3,
                            )
                          }
                        : {},
                    circles: _geeTileUrl.isEmpty ? _buildGoogleMapCircles() : {},
                    tileOverlays: _geeTileUrl.isNotEmpty
                        ? {
                            TileOverlay(
                              tileOverlayId: const TileOverlayId("gee_overlay"),
                              tileProvider: UrlTileProvider(
                                urlTemplate: _geeTileUrl,
                              ),
                              transparency: 0.1,
                            )
                          }
                        : {},
                    markers: _gpsPoints.asMap().entries.map((entry) {
                      int idx = entry.key;
                      LatLng latLng = entry.value;
                      return Marker(
                        markerId: MarkerId("m_$idx"),
                        position: latLng,
                        icon: BitmapDescriptor.defaultMarkerWithHue(idx == 0 ? BitmapDescriptor.hueGreen : BitmapDescriptor.hueOrange),
                      );
                    }).toSet(),
                  )'''

# We use regex to replace the GoogleMap block
pattern = re.compile(r'GoogleMap\(\s*initialCameraPosition:.*?\}\)\.toSet\(\),\s*\)', re.DOTALL)
content = pattern.sub(google_map_str, content)

# Clear _geeTileUrl when grid overlay is cleared or analysis type changes
clear_new = '''  void _triggerGridOverlay(String type) {
    _gridOverlayPoints.clear();
    if (_gpsPoints.length < 3) return;'''
content = content.replace(clear_new, clear_new + '\n    if (type == "none") _geeTileUrl = "";')

# Add tile_url to offline dummy response so it clears
offline_new = '''    setState(() {
      _isLoadingGee = false;
      _geeTileUrl = "";'''
content = content.replace('''    setState(() {
      _isLoadingGee = false;''', offline_new)

with open('frontend/lib/main.dart', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched flutter successfully!')
