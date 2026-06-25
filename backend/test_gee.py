import requests
import json

def test_gee_endpoints():
    url_ndvi = "http://localhost:8000/api/ai/gee/ndvi"
    url_thermal = "http://localhost:8000/api/ai/gee/thermal"
    
    # Multan region polygon coordinates
    payload = {
        "polygon_coords": [
            {"lat": 30.150, "lng": 71.500},
            {"lat": 30.155, "lng": 71.500},
            {"lat": 30.155, "lng": 71.505},
            {"lat": 30.150, "lng": 71.505}
        ],
        "crop_name": "Wheat"
    }
    
    headers = {"Content-Type": "application/json"}
    
    print("Testing NDVI endpoint...")
    try:
        r_ndvi = requests.post(url_ndvi, headers=headers, json=payload, timeout=20)
        print("NDVI status:", r_ndvi.status_code)
        if r_ndvi.status_code == 200:
            print(json.dumps(r_ndvi.json(), indent=2))
        else:
            print(r_ndvi.text)
    except Exception as e:
        print("Error connecting to NDVI endpoint:", e)
        
    print("\nTesting Thermal endpoint...")
    try:
        r_thermal = requests.post(url_thermal, headers=headers, json=payload, timeout=20)
        print("Thermal status:", r_thermal.status_code)
        if r_thermal.status_code == 200:
            print(json.dumps(r_thermal.json(), indent=2))
        else:
            print(r_thermal.text)
    except Exception as e:
        print("Error connecting to Thermal endpoint:", e)

if __name__ == "__main__":
    test_gee_endpoints()
