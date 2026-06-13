import re

print("Loading blocklist...")
with open("../data/blocklist.txt", "r", encoding="utf-8") as f:
    names = [line.strip().lower() for line in f if line.strip()]

# Sort by length descending so "so[REDACTED_NAME]" gets replaced before "[REDACTED_NAME]"
names.sort(key=len, reverse=True)

print("Loading dataset...")
with open("../data/subset_10k.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(f"Scrubbing {len(names)} names from the text...")
for name in names:
    # Only replace whole words to avoid accidentally replacing letters inside other words
    pattern = r'\b' + re.escape(name) + r'\b'
    text = re.sub(pattern, '[FRIEND]', text, flags=re.IGNORECASE)

print("Saving sanitized dataset...")
with open("../data/subset_10k_sanitized.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("✅ Data sanitization complete!")
