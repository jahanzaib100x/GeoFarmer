import requests
import json

def query_debug():
    url = "https://geofarmer-backend.onrender.com/api/debug/gemini"
    try:
        r = requests.get(url, timeout=15)
        print("Status code:", r.status_code)
        resp_json = r.json()
        
        with open("debug_out.json", "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)
        print("Wrote debug output to debug_out.json successfully.")
        
        # Safe printing of ASCII parts
        print("gemini_ready:", resp_json.get("gemini_ready"))
        err_msg = resp_json.get("gemini_last_error", "")
        print("gemini_last_error (first 100 chars):", err_msg[:100] if err_msg else "None")
        print("gemini_key_preview:", resp_json.get("gemini_key_preview"))
        
    except Exception as e:
        print("Failed to query debug endpoint:", e)

if __name__ == "__main__":
    query_debug()
