import os
import sys

try:
    from google import genai
    from google.oauth2 import service_account
except ImportError:
    print("Error: Missing google-genai or google-auth libraries.")
    print("Please install them by running: pip install google-genai google-auth")
    sys.exit(1)

backend_dir = os.path.dirname(os.path.abspath(__file__))
sa_file = os.path.join(backend_dir, "geofarmer-v2-c591674c09dd.json")

if not os.path.exists(sa_file):
    print(f"Error: Service account file not found at: {sa_file}")
    sys.exit(1)

print(f"Using service account file: {os.path.basename(sa_file)}")
project_id = "geofarmer-v2"
location = "us-central1"

try:
    # Initialize the modern google-genai client with service account credentials and scopes
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    credentials = service_account.Credentials.from_service_account_file(sa_file, scopes=scopes)
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
        credentials=credentials
    )
    
    print("google-genai client initialized. Sending test prompt to gemini-1.5-flash on Vertex AI...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello! Please respond with exactly: 'google-genai Vertex AI is working perfectly!'"
    )
    
    if response and response.text:
        print("\n" + "="*50)
        print("Response:", response.text.strip())
        print("="*50)
        print("\nSuccess! google-genai Vertex AI is fully functional and ready.")
    else:
        print("Empty response from client.")
except Exception as e:
    print("\n[ERROR] google-genai call failed:")
    print(e)
