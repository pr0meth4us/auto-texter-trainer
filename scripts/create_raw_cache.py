import os
import json
import random
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

print("1. Stripping all JSON repetition and extracting raw chat history...")
with open('../data/dataset_test.jsonl', 'r') as f:
    lines = f.readlines()

random.seed(123)
random.shuffle(lines)

raw_conversations = []
total_bytes = 0
TARGET_BYTES = 3_000_000 # Aim for ~3MB of pure text, which is comfortably under 1M tokens.

for line in lines:
    data = json.loads(line)
    ctx = data['messages'][1]['content'].replace("Context: ", "")
    reply = data['messages'][2]['content']
    
    # Format as pure text, no JSON waste!
    raw_text = f"Context: {ctx}\nMy Reply: {reply}\n---\n"
    total_bytes += len(raw_text.encode('utf-8'))
    raw_conversations.append(raw_text)
    
    if total_bytes >= TARGET_BYTES:
        break

with open('../data/raw_history.txt', 'w') as f:
    f.writelines(raw_conversations)

print(f"✅ Extracted {len(raw_conversations)} pure conversations (approx {total_bytes / 1024 / 1024:.2f} MB of pure text).")

print("2. Uploading pure text dataset to Google...")
file = client.files.upload(
    file="../data/raw_history.txt",
    config=types.UploadFileConfig(display_name="Pure Raw Chat History", mime_type="text/plain")
)
print(f"✅ Uploaded successfully! File ID: {file.name}")

print("3. Pushing the pure dataset into Gemini 3.5 Flash's Context Cache...")
try:
    cache = client.caches.create(
        model="models/gemini-3.5-flash",
        config=types.CreateCachedContentConfig(
            system_instruction=[
                "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant.",
                "You are completely fluent in English, but you frequently mix in 'Latinized Khmer'.",
                "ALWAYS use all lowercase letters. Do not use punctuation like periods.",
                "Here is a massive dataset of my raw texting history. Read the Context and My Reply pairs. Clone my exact personality, vocabulary, and texting style perfectly:",
                file
            ],
            ttl="86400s",
            display_name="Max Capacity Auto-Texter"
        )
    )
    print(f"🎉 SUCCESS! Cache ID: {cache.name}")
except Exception as e:
    print("❌ Failed to create cache:", e)
