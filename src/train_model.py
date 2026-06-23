import os
import sys
import time

# Add src to sys.path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import bifrost_config

import vertexai
from vertexai.tuning import sft

print("Setting up Vertex AI Tuning...")

project_id = bifrost_config.get_config("GCP_PROJECT_ID", "gen-lang-client-0429923800")
location = bifrost_config.get_config("GCP_LOCATION", "us-central1")

vertexai.init(project=project_id, location=location)

print("Starting supervised fine-tuning (SFT) job on Vertex AI...")

try:
    sft_tuning_job = sft.train(
        source_model="gemini-2.5-flash",
        train_dataset="gs://auto-texter-trainer-data-1781715368/dataset_10k_vertex.jsonl",
        tuned_model_display_name="my-auto-texter"
    )

    print("Job started! Wait for it to finish in the Google Cloud Console.")
    print(f"Tuning job name: {sft_tuning_job.name}")
    
except Exception as e:
    print(f"An error occurred: {e}")
