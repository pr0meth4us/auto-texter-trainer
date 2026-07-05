import sys
import os
from google.cloud import aiplatform_v1

project_id = "gen-lang-client-0429923800"
location = "us-central1"

client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
client = aiplatform_v1.GenAiTuningServiceClient(client_options=client_options)

parent = f"projects/{project_id}/locations/{location}"

try:
    print("Listing Tuning jobs...")
    request = aiplatform_v1.ListTuningJobsRequest(parent=parent)
    page_result = client.list_tuning_jobs(request=request)
    
    found = False
    for job in page_result:
        print(f"Job: {job.name}, State: {job.state.name}")
        if job.state.name in ("JOB_STATE_RUNNING", "JOB_STATE_PENDING"):
            print(f"Canceling job {job.name}...")
            cancel_req = aiplatform_v1.CancelTuningJobRequest(name=job.name)
            client.cancel_tuning_job(request=cancel_req)
            print("Canceled.")
            found = True
    if not found:
        print("No running tuning jobs found.")
except Exception as e:
    print(f"Error checking TuningJobs: {e}")

