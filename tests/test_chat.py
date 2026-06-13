import os
import sys
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    print("🧠 Connecting to your 960,000 token persona clone...")
    chat = client.chats.create(
        model="models/gemini-3.5-flash",
        config=types.GenerateContentConfig(
            cached_content=os.environ.get("GEMINI_CACHE_NAME"),
            temperature=0.8 # A bit of randomness makes the texts feel natural
        )
    )
    print("✅ Connected! You can now chat with your clone.")
    print("Type 'quit' or 'exit' to stop.\n" + "="*50)
    
    while True:
        user_msg = input("Friend: ")
        if user_msg.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        # Send message to the clone
        response = chat.send_message(user_msg)
        print(f"Clone:  {response.text}\n")
        
except Exception as e:
    print("❌ Error connecting to clone:", e)
