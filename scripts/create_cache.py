import os
from google import genai
from google.genai import types

# Initialize with the new SDK!
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 1. Upload the ENTIRE dataset (not just the subset!)
# With Gemini 3.5 Flash, we can fit your entire 105,000 message history into its brain.
print("1. Uploading the full dataset_test.jsonl to Google's servers...")
document = client.files.upload(
    file="../data/dataset_test.jsonl",
    config=types.UploadFileConfig(
        display_name="Full Chat History",
        mime_type="text/plain"
    )
)
print(f"✅ Uploaded successfully! File ID: {document.name}")

# 2. Create the Context Cache
print("2. Pushing the dataset into Gemini 3.5 Flash's Context Cache...")
cache = client.caches.create(
    model="models/gemini-3.5-flash",
    config=types.CreateCachedContentConfig(
        system_instruction=[
            "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant.",
            "You are completely fluent in English, but you frequently mix in 'Latinized Khmer'.",
            "ALWAYS use all lowercase letters. Do not use punctuation like periods.",
            "Here is my entire texting history. Read it and clone my exact personality and texting style:",
            document
        ],
        ttl="86400s", # Keep the cache alive for 24 hours
        display_name="Auto-Texter Cache"
    )
)
print(f"✅ Cache created successfully! Cache ID: {cache.name}")

# 3. How to use it in your bot
print("\n" + "="*50)
print("🚀 READY TO USE IN YOUR TELEGRAM BOT!")
print("="*50)
print(f"""
To use this clone in your actual Python code, all you do is pass the cache name:

chat = client.chats.create(
    model="models/gemini-3.5-flash",
    config=types.GenerateContentConfig(
        cached_content="{cache.name}",
        temperature=0.8
    )
)

response = chat.send_message("Hey! Where did you go?")
print(response.text)
""")
