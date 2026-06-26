import main

print("Testing direct call_gemini_api in main.py using Vertex AI...")
try:
    system_prompt = "You are a master agriculture expert."
    user_prompt = "Say 'The backend Vertex AI system is ready to grow!'"
    
    reply = main.call_gemini_api(system_prompt, user_prompt)
    
    print("\n" + "="*50)
    print("API Response:", reply)
    print("="*50)
    if "ready to grow" in reply.lower():
        print("\nSuccess! The backend main.py calls Vertex AI successfully.")
    else:
        print("\nFailed: Did not receive expected response content.")
except Exception as e:
    print("\n[ERROR] Direct call failed:")
    print(e)
