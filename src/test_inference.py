import os
import sys

# Add src to sys.path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import bifrost_config

import vertexai
from vertexai.generative_models import GenerativeModel

print("Setting up Vertex AI...")
project_id = bifrost_config.get_config("GCP_PROJECT_ID", "gen-lang-client-0429923800")
location = bifrost_config.get_config("GCP_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Endpoint ID for the successful tuning job "my-auto-texter"
# Model ID: projects/877283386153/locations/us-central1/models/4559437775631286272
model_resource_name = "projects/877283386153/locations/us-central1/endpoints/1484948177671946240"

print(f"Loading Tuned Model: {model_resource_name}")
model = GenerativeModel(model_resource_name)

print("\n" + "="*60)
print("🧪 TESTING MY-AUTO-TEXTER TUNED MODEL")
print("="*60 + "\n")

# Some sample contexts to test the model
test_messages = [
    "hey man, you going to the party tonight?",
    "did you finish the math homework?",
    "what's for lunch?",
    "have you seen the new movie yet?"
]

for i, msg in enumerate(test_messages):
    print(f"[{i+1}/{len(test_messages)}] SCENARIO:")
    print(f"Friend: {msg}")
    
    # Format the prompt exactly how it was in the training dataset (usually "Context: ...")
    prompt = f"Context: {msg}"
    
    try:
        response = model.generate_content(prompt)
        print(f"Clone: {response.text.strip()}")
    except Exception as e:
        print("Error getting reply:", e)
        
    print("-" * 60)
