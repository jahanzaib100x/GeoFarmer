import os
import requests
import json

def run_diagnostic_test():
    """
    Utility script to test the GeoKisan / detect leaf disease diagnosis API.
    Generates a temporary dummy image asset and sends it via multipart form POST,
    printing the statistical disease classification results and severity rankings.
    """
    server_url = "http://localhost:8000/detect"
    temp_img_name = "test_wheat_rust_leaf.jpg"
    
    print(f"Creating mock wheat crop leaf image asset: {temp_img_name}...")
    with open(temp_img_name, "wb") as f:
        f.write(b"\x00" * 1024)
        
    print(f"Uploading image to FastAPI server at: {server_url}...")
    try:
        with open(temp_img_name, "rb") as img_file:
            files = {"image": (temp_img_name, img_file, "image/jpeg")}
            response = requests.post(server_url, files=files, timeout=5)
            
        if response.status_code == 200:
            result_data = response.json()
            print("\n" + "="*50)
            print("AI DIAGNOSTIC REPORT RECEIVED SUCCESSFULLY")
            print("="*50)
            # Ensure printed dictionary does not trigger codec errors
            formatted_json = json.dumps(result_data, indent=4)
            # Encode and decode as ascii back, replacing unknown chars
            print(formatted_json.encode('ascii', errors='replace').decode('ascii'))
            print("="*50)
        else:
            print(f"[ERROR] API server returned response code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[CONNECTION ERROR] Failed to connect to local server: {e}")
        print("Make sure your FastAPI server is running on port 8000.")
        
    finally:
        # Clean up mock file asset
        if os.path.exists(temp_img_name):
            os.remove(temp_img_name)
            print(f"\nTemporary file {temp_img_name} removed.")

if __name__ == "__main__":
    run_diagnostic_test()
