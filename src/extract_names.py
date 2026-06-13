import json
import os
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
client = genai.Client(api_key=api_key)

print("Loading 10k subset...")
with open("../data/subset_10k.txt", "r", encoding="utf-8") as f:
    history_text = f.read()

prompt = """
You are an expert data sanitization AI. 
Read the following raw chat history.
Your ONLY job is to identify every single proper name, nickname, or personal identifier (friends, family, coworkers, people) mentioned in the text.
The chat may contain informal slang, bilingual text, or phonetic spellings. Carefully analyze the context to distinguish between common nouns and actual names/nicknames.

Output a valid JSON array of strings containing all the unique names you found. Do not include honorifics or titles, just the base names. Convert them all to lowercase.
Example output: ["alex", "jordan", "taylor", "sam"]

Text History:
""" + history_text

print("Sending 250k token payload to Gemini for Name Extraction. This may take 30-60 seconds...")

try:
    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    # Save the output
    names = json.loads(response.text)
    
    with open("../data/blocklist.txt", "w", encoding="utf-8") as f:
        for name in names:
            f.write(name + "\n")
            
    print(f"✅ Successfully extracted {len(names)} unique names and saved them to blocklist.txt!")

except Exception as e:
    print("Error extracting names:", e)
