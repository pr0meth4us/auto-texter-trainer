import os
from google import genai
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Fetch the cache to see if it exposes token count
cache = client.caches.get(name=os.environ.get("GEMINI_CACHE_NAME"))
print(cache)
