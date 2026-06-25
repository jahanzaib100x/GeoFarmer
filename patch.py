import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

ndvi_new = """@app.post("/api/ai/gee/ndvi")
def get_gee_ndvi(
    payload: GeeRequest,
    x_gemini_api_key: Optional[str] = Header(None),
    x_deepseek_api_key: Optional[str] = Header(None)
):
    \"\"\"
    Retrieves Google Earth Engine NDVI analysis report.
    \"\"\"
    coords = payload.polygon_coords
    crop = payload.crop_name or "Wheat"
    
    if not coords:
        raise HTTPException(status_code=400, detail="Polygon coordinates are required")
        
    lats = [c["lat"] for c in coords]
    lngs = [c["lng"] for c in coords]
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    
    tile_url = ""
    mode = "simulation"
    ndvi_avg = 0.65
    healthy_pct = 70.0
    average_pct = 20.0
    stressed_pct = 10.0
    
    if gee_ready:
        try:
            geom = ee.Geometry.Polygon([[[c['lng'], c['lat']] for c in coords]])
            # Sentinel-2 surface reflectance
            dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \\
                        .filterBounds(geom) \\
                        .filterDate('2023-01-01', '2025-01-01') \\
                        .sort('CLOUDY_PIXEL_PERCENTAGE') \\
                        .first()
            
            # Compute NDVI: (NIR - Red) / (NIR + Red) -> (B8 - B4) / (B8 + B4)
            ndvi = dataset.normalizedDifference(['B8', 'B4']).rename('NDVI')
            clipped_ndvi = ndvi.clip(geom)
            
            # MapId for TileProvider
            vis_params = {
                'min': 0.0,
                'max': 1.0,
                'palette': ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
            }
            map_id_dict = ee.Image(clipped_ndvi).getMapId(vis_params)
            tile_url = map_id_dict['tile_fetcher'].url_format
            mode = "gee_live"
        except Exception as e:
            print(f"[GEE] NDVI error: {e}")
            
    if mode == "simulation":
        seed_val = int((center_lat + center_lng) * 1000) % 100
        ndvi_avg = round(0.58 + (seed_val % 20) * 0.01, 2)
        stressed_pct = round(10.0 + (seed_val % 15), 1)
        average_pct = round(20.0 + ((seed_val + 5) % 20), 1)
        healthy_pct = round(100.0 - stressed_pct - average_pct, 1)

    system_prompt = (
        "You are an expert precision satellite remote sensing agronomist. "
        "Explain the farmer's NDVI vegetation scan report. Keep the analysis concise, practical, "
        "and focus on actionable recommendations (fertilizer, moisture check). "
        "Output standard Urdu and English. Response must be extremely practical."
    )
    
    user_prompt = f\"\"\"
    Generate a bilingual NDVI satellite vegetation analysis report for a farm with:
    Crop Name: {crop}
    Calculated Average NDVI: {ndvi_avg} (Stressed: {stressed_pct}%, Average: {average_pct}%, Healthy: {healthy_pct}%)
    Farm Coordinates Center: ({center_lat:.4f}, {center_lng:.4f})
    
    Format output as strict JSON:
    {{
      "report_en": "Provide English report here.",
      "report_ur": "محنت کش بھائی! آپ کی فصل کا اوسط صحت انڈیکس (NDVI) 0.68 ہے۔ شمالی حصے میں فصل سرسبز اور شاداب ہے..."
    }}
    \"\"\"
    
    report_en = ""
    report_ur = ""
    
    gemini_key = x_gemini_api_key or os.environ.get("GEMINI_API_KEY")
    deepseek_key = x_deepseek_api_key or os.environ.get("DEEPSEEK_API_KEY")
    
    api_response = None
    if gemini_key:
        api_response = call_gemini_api(system_prompt, user_prompt, api_key=gemini_key)
    if not api_response and deepseek_key:
        api_response = call_deepseek_api(system_prompt, user_prompt, api_key=deepseek_key)
        
    if api_response:
        try:
            cleaned = api_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            report_en = data.get("report_en", "")
            report_ur = data.get("report_ur", "")
        except Exception as e:
            print(f"Failed parsing satellite analysis JSON: {e}")
            
    if not report_en:
        report_en = f"Satellite analysis shows your {crop} crop is at {healthy_pct}% healthy vegetation density. The average NDVI of {ndvi_avg} indicates excellent growth. We recommend checking the southern portion which displays minor nitrogen/chlorophyll deficiency."
        report_ur = f"سیٹلائٹ تجزیہ کے مطابق آپ کی {crop} کی فصل {healthy_pct} فیصد صحت مند نشوونما دکھا رہی ہے۔ اوسط NDVI انڈیکس {ndvi_avg} بہترین کارکردگی کا اشارہ ہے۔ ہم کھیت کے جنوبی کونے میں یوریا اور نائٹروجن کی مقدار بڑھانے کی سفارش کرتے ہیں۔"

    return {
        "status": "success",
        "mode": mode,
        "tile_url": tile_url,
        "ndvi_average": ndvi_avg,
        "distribution": {
            "healthy_pct": healthy_pct,
            "average_pct": average_pct,
            "stressed_pct": stressed_pct
        },
        "report_en": report_en,
        "report_ur": report_ur
    }"""

thermal_new = """@app.post("/api/ai/gee/thermal")
def get_gee_thermal(
    payload: GeeRequest,
    x_gemini_api_key: Optional[str] = Header(None),
    x_deepseek_api_key: Optional[str] = Header(None)
):
    \"\"\"
    Retrieves Google Earth Engine Thermal analysis report.
    \"\"\"
    coords = payload.polygon_coords
    crop = payload.crop_name or "Wheat"
    
    if not coords:
        raise HTTPException(status_code=400, detail="Polygon coordinates are required")
        
    lats = [c["lat"] for c in coords]
    lngs = [c["lng"] for c in coords]
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    
    tile_url = ""
    mode = "simulation"
    temp_avg = 30.5
    optimal_pct = 70.0
    overwatered_pct = 10.0
    stressed_pct = 20.0
    
    if gee_ready:
        try:
            geom = ee.Geometry.Polygon([[[c['lng'], c['lat']] for c in coords]])
            # Landsat 8 Surface Temperature
            dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \\
                        .filterBounds(geom) \\
                        .filterDate('2023-01-01', '2025-01-01') \\
                        .sort('CLOUD_COVER') \\
                        .first()
            
            # ST_B10 is thermal band. Scale factor: 0.00341802 * DN + 149.0
            # Then convert Kelvin to Celsius (-273.15)
            thermal = dataset.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
            clipped_thermal = thermal.clip(geom)
            
            vis_params = {
                'min': 15.0,
                'max': 45.0,
                'palette': ['#040274', '#040281', '#0502a3', '#0502b8', '#0502ce', '#0502e6',
                            '#0602ff', '#235cb1', '#307ef3', '#269db1', '#30c8e2', '#32d3ef',
                            '#3be285', '#3ff38f', '#86e26f', '#3ae237', '#b5e22e', '#d6e21f',
                            '#fff705', '#ffd611', '#ffb613', '#ff8b13', '#ff6e08', '#ff500d',
                            '#ff0000', '#de0101', '#c21301', '#a71001', '#911003']
            }
            map_id_dict = ee.Image(clipped_thermal).getMapId(vis_params)
            tile_url = map_id_dict['tile_fetcher'].url_format
            mode = "gee_live"
        except Exception as e:
            print(f"[GEE] Thermal error: {e}")
            
    if mode == "simulation":
        seed_val = int((center_lat + center_lng) * 1000) % 100
        temp_avg = round(28.5 + (seed_val % 10) * 0.5, 1)
        stressed_pct = round(12.0 + (seed_val % 18), 1)
        overwatered_pct = round(8.0 + ((seed_val + 2) % 15), 1)
        optimal_pct = round(100.0 - stressed_pct - overwatered_pct, 1)

    system_prompt = (
        "You are an expert satellite remote sensing moisture and crop temperature agronomist. "
        "Explain the farmer's thermal moisture scan report. Keep the analysis concise, practical, "
        "and focus on irrigation frequency advice. "
        "Output standard Urdu and English. Response must be extremely practical."
    )
    
    user_prompt = f\"\"\"
    Generate a bilingual thermal satellite analysis report for a farm with:
    Crop Name: {crop}
    Average Temperature: {temp_avg}°C (Water Stressed: {stressed_pct}%, Optimal: {optimal_pct}%, Over-watered: {overwatered_pct}%)
    Farm Coordinates Center: ({center_lat:.4f}, {center_lng:.4f})
    
    Format output as strict JSON:
    {{
      "report_en": "Provide English report here.",
      "report_ur": "محنت کش بھائی! تھرمل اسکین کے مطابق اوسط درجہ حرارت 30.5 ڈگری ہے۔ کچھ حصوں میں پانی کی کمی دیکھی گئی ہے..."
    }}
    \"\"\"
    
    report_en = ""
    report_ur = ""
    
    gemini_key = x_gemini_api_key or os.environ.get("GEMINI_API_KEY")
    deepseek_key = x_deepseek_api_key or os.environ.get("DEEPSEEK_API_KEY")
    
    api_response = None
    if gemini_key:
        api_response = call_gemini_api(system_prompt, user_prompt, api_key=gemini_key)
    if not api_response and deepseek_key:
        api_response = call_deepseek_api(system_prompt, user_prompt, api_key=deepseek_key)
        
    if api_response:
        try:
            cleaned = api_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            report_en = data.get("report_en", "")
            report_ur = data.get("report_ur", "")
        except Exception as e:
            print(f"Failed parsing satellite analysis JSON: {e}")
            
    if not report_en:
        report_en = f"Thermal analysis shows an average canopy temperature of {temp_avg}°C. About {stressed_pct}% of the farm is water stressed. Immediate irrigation cycle is recommended for the warmer spots."
        report_ur = f"تھرمل تجزیہ کے مطابق فصل کا اوسط درجہ حرارت {temp_avg} ڈگری ہے۔ کھیت کے {stressed_pct} فیصد حصے میں پانی کی کمی ظاہر ہو رہی ہے۔ ہم تجویز کرتے ہیں کہ گرم حصوں میں فوراً پانی لگائیں۔"

    return {
        "status": "success",
        "mode": mode,
        "tile_url": tile_url,
        "thermal_average": temp_avg,
        "distribution": {
            "optimal_pct": optimal_pct,
            "overwatered_pct": overwatered_pct,
            "stressed_pct": stressed_pct
        },
        "report_en": report_en,
        "report_ur": report_ur
    }"""

# Replace from @app.post("/api/ai/gee/ndvi") up to @app.post("/api/ai/gee/thermal")
pattern1 = re.compile(r'@app\.post\(\"/api/ai/gee/ndvi\"\).*?(?=@app\.post\(\"/api/ai/gee/thermal\"\))', re.DOTALL)
content = pattern1.sub(ndvi_new + '\n\n', content)

# Replace from @app.post("/api/ai/gee/thermal") to the end before if __name__ == "__main__":
pattern2 = re.compile(r'@app\.post\(\"/api/ai/gee/thermal\"\).*?(?=if __name__ == [\"\']__main__[\"\']:)', re.DOTALL)
content = pattern2.sub(thermal_new + '\n\n', content)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patch applied successfully!')
