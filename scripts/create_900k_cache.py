import os
import json
import random
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

print("1. Sampling ~900k tokens from the massive dataset...")
with open('../data/dataset_test.jsonl', 'r') as f:
    lines = f.readlines()

random.seed(123)
random.shuffle(lines)

subset_lines = []
total_bytes = 0
# 900k tokens is roughly 3.2 to 3.5 MB of raw text. Let's aim for 3.3 MB.
TARGET_BYTES = 3_300_000 

for line in lines:
    data = json.loads(line)
    text = data['messages'][1]['content'] + " " + data['messages'][2]['content']
    total_bytes += len(text.encode('utf-8'))
    subset_lines.append(line)
    if total_bytes >= TARGET_BYTES:
        break

with open('../data/dataset_900k.jsonl', 'w') as f:
    f.writelines(subset_lines)

print(f"✅ Sampled {len(subset_lines)} conversations (approx {total_bytes / 1024 / 1024:.2f} MB of text).")

print("2. Uploading 900k token dataset to Google's servers...")
file = client.files.upload(
    file="../data/dataset_900k.jsonl",
    config=types.UploadFileConfig(display_name="900k Context Cache", mime_type="text/plain")
)
print(f"✅ Uploaded successfully! File ID: {file.name}")

print("3. Pushing the massive dataset into Gemini 3.5 Flash's Context Cache...")
try:
    cache = client.caches.create(
        model="models/gemini-3.5-flash",
        config=types.CreateCachedContentConfig(
            system_instruction=[
                "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant.",
                "You are completely fluent in English, but you frequently mix in 'Latinized Khmer'.",
                "ALWAYS use all lowercase letters. Do not use punctuation like periods.",
                "Here is my extensive texting history. Read it and clone my exact personality and texting style:",
                file
            ],
            ttl="86400s",
            display_name="900k Token Auto-Texter"
        )
    )
    print(f"🎉 SUCCESS! Cache ID: {cache.name}")
except Exception as e:
    print("❌ Failed to create cache:", e)
