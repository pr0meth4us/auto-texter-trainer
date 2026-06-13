import os
import json
import random
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Read the file directly into a Python string (NO Google File API involved!)
with open("../data/subset_10k.txt", "r", encoding="utf-8") as f:
    history_text = f.read()

print("File loaded into memory successfully.")

with open('../data/dataset_test.jsonl', 'r') as f:
    lines = f.readlines()

random.seed(123)
random.shuffle(lines)
test_lines = lines[33426:33426+5] 

print("\n" + "="*60)
print("🧪 AUTOMATED HOLD-OUT EVALUATION")
print("="*60 + "\n")

for i, line in enumerate(test_lines):
    data = json.loads(line)
    ctx = data['messages'][1]['content'].replace("Context: ", "")
    actual_reply = data['messages'][2]['content']
    
    print(f"[{i+1}/5] SCENARIO:")
    print(f"Friend: {ctx}")
    print(f"\n✅ What you ACTUALLY texted back:")
    print(f"You: {actual_reply}")
    print(f"\n🤖 What your CLONE texts back:")
    
    try:
        response = client.models.generate_content(
            model="models/gemini-3.5-flash",
            contents=ctx,
            config=types.GenerateContentConfig(
                system_instruction=[
                    "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant.",
                    "You are completely fluent in English, but you frequently mix in 'Latinized Khmer'.",
                    "ALWAYS use all lowercase letters. Do not use punctuation like periods.",
                    "Here is a history of my texting. Clone my exact personality perfectly:\n\n",
                    history_text
                ],
                temperature=0.8
            )
        )
        print(f"Clone: {response.text}")
    except Exception as e:
        print("Error getting reply:", e)
        
    print("\n" + "-"*60 + "\n")
