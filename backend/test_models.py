import os
import sys

try:
    from google import genai
    from google.oauth2 import service_account
except ImportError:
    print("Error: Missing google-genai or google-auth libraries.")
    sys.exit(1)

backend_dir = os.path.dirname(os.path.abspath(__file__))
sa_file = os.path.join(backend_dir, "geofarmer-v2-c591674c09dd.json")

if not os.path.exists(sa_file):
    print(f"Error: Service account file not found at: {sa_file}")
    sys.exit(1)

project_id = "geofarmer-v2"
scopes = ["https://www.googleapis.com/auth/cloud-platform"]
credentials = service_account.Credentials.from_service_account_file(sa_file, scopes=scopes)

# Try different regions and models to see what works
test_cases = [
    {"region": "us-central1", "model": "gemini-1.5-flash"},
    {"region": "us-central1", "model": "gemini-1.5-flash-002"},
    {"region": "us-central1", "model": "gemini-2.5-flash"},
    {"region": "us-east4", "model": "gemini-1.5-flash"},
    {"region": "us-central1", "model": "gemini-1.0-pro"}
]

print("Starting diagnostic test of models/regions on Vertex AI...")

for case in test_cases:
    region = case["region"]
    model_name = case["model"]
    print(f"\nTrying model '{model_name}' in region '{region}'...")
    try:
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=region,
            credentials=credentials
        )
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Success'"
        )
        if response and response.text:
            print(f"-> SUCCESS! Model '{model_name}' in '{region}' responded: {response.text.strip()}")
            # If it succeeded, we can stop here
            break
        else:
            print(f"-> Failed: Empty response")
    except Exception as e:
        print(f"-> Failed: {e}")
