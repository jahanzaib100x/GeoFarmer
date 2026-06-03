import requests
import json

def run_chat_test():
    """
    Test client script to verify the bilingual AI chatbot endpoint.
    Sends sample English and Urdu prompts to /api/ai/chat.
    """
    url = "http://localhost:8000/api/ai/chat"
    headers = {"Content-Type": "application/json"}
    
    # 1. Test Urdu agricultural query
    urdu_payload = {"prompt": "گندم کی اچھی پیداوار کے لیے کھاد ڈالنے کا بہترین طریقہ کیا ہے؟"}
    print("Sending Urdu agricultural query to chatbot...")
    try:
        response = requests.post(url, headers=headers, json=urdu_payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*50)
            print("URDU BOT RESPONSE (Source: {})".format(result.get("source")))
            print("="*50)
            # Safe print to handle potential terminal encoding limitations
            print(result["reply"].encode('ascii', errors='replace').decode('ascii'))
            print("="*50)
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Connection failure: {e}")
        
    print("\n" + "-"*50 + "\n")

    # 2. Test English query
    english_payload = {"prompt": "What should I do if my soil is dry and water is limited?"}
    print("Sending English query to chatbot...")
    try:
        response = requests.post(url, headers=headers, json=english_payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*50)
            print("ENGLISH BOT RESPONSE (Source: {})".format(result.get("source")))
            print("="*50)
            print(result["reply"])
            print("="*50)
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Connection failure: {e}")

if __name__ == "__main__":
    run_chat_test()
