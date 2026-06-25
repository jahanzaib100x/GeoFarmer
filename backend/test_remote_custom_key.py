import requests
from PIL import Image
import io
import json

def generate_leaf_image():
    img = Image.new("RGB", (640, 640), (45, 120, 70))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_remote():
    print("Uploading with custom fake header key...")
    img_bytes = generate_leaf_image()
    
    headers = {
        'x-gemini-api-key': 'AIzaSyFakeKey1234567890_TestSuffix'
    }
    files = {
        'image': ('simulated_leaf.png', img_bytes, 'image/png')
    }
    data = {
        'crop_name': 'wheat'
    }
    
    try:
        r = requests.post("https://geofarmer-backend.onrender.com/detect", headers=headers, files=files, data=data, timeout=30)
        print("Status code:", r.status_code)
        resp_json = r.json()
        print("Response JSON keys:", list(resp_json.keys()))
        
        # Now query debug to verify if the key was logged correctly
        r_debug = requests.get("https://geofarmer-backend.onrender.com/api/debug/gemini", timeout=15)
        debug_json = r_debug.json()
        print("Debug gemini_key_preview:", debug_json.get("gemini_key_preview"))
        print("Debug last error (first 100 chars):", debug_json.get("gemini_last_error", "")[:100])
    except Exception as e:
        print("Request failed:", e)

if __name__ == "__main__":
    test_remote()
