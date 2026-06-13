import os
import google.generativeai as genai
import time

# 1. Setup API
# Replace this with your actual API key!
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

import csv

# 2. Read the CSV data directly
print("Loading dataset...")
training_data = []
with open("../data/training_subset.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        training_data.append({
            "text_input": row["input"],
            "output": row["output"]
        })

print(f"Loaded {len(training_data)} examples.")

# 3. Start the Tuning Job
print("Starting fine-tuning job...")
try:
    operation = genai.create_tuned_model(
        display_name="my-auto-texter",
        source_model="models/gemini-1.5-flash-001-tuning",
        training_data=training_data,
        epoch_count=3,
        batch_size=4,
        learning_rate=0.001
    )

    print("Job started! Waiting for it to finish (this might take 30-60 minutes)...")

    # 4. Check status loop
    for status in operation.wait_bar():
        time.sleep(10)

    print("Finished!")
    result = operation.result()
    print(f"Your new custom Model ID is: {result.name}")
except Exception as e:
    print(f"An error occurred: {e}")
