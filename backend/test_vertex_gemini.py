import os
import sys

# Try to import vertexai. If missing, print instruction to install it.
try:
    import google.auth
    from google.oauth2 import service_account
    import vertexai
    from vertexai.generative_models import GenerativeModel
except ImportError:
    print("Error: Missing google-cloud-aiplatform library.")
    print("Please install it by running: pip install google-cloud-aiplatform google-auth")
    sys.exit(1)

backend_dir = os.path.dirname(os.path.abspath(__file__))
# Check for the service account file
sa_file = os.path.join(backend_dir, "geofarmer-498712-c28893c5b1e9.json")

if not os.path.exists(sa_file):
    print(f"Error: Service account file not found at: {sa_file}")
    sys.exit(1)

print(f"Using service account file: {os.path.basename(sa_file)}")
project_id = "geofarmer-498712"
location = "us-central1"  # standard location for Vertex AI Gemini models

try:
    # Set the credentials file in the environment for underlying clients to find
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_file
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    print("Vertex AI initialized successfully. Sending test prompt to gemini-1.5-flash...")
    # Load model
    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Hello! Please respond with exactly: 'Vertex AI Gemini is working perfectly!'")
    
    if response and response.text:
        print("\n" + "="*50)
        print("Response:", response.text.strip())
        print("="*50)
        print("\nSuccess! Vertex AI is working and will now consume your GCP credits.")
    else:
        print("Empty response from Vertex AI.")
except Exception as e:
    print("\n[ERROR] Vertex AI Gemini call failed:")
    print(e)
    print("\nIf it says API is not enabled, look for the enabling link in the error above or go to the Google Cloud Console, search for 'Vertex AI API' and enable it.")
