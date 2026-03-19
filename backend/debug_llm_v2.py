import urllib.request
import json

# Exact copy of the key that worked before
key = "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"
model = "google/gemini-2.0-flash-001"
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    # "HTTP-Referer": "http://localhost:3000", # Commenting out to see if it matters
    # "X-Title": "Proctor"
}

data = {
    "model": model,
    "messages": [{"role": "user", "content": "Hello"}],
}

print(f"Key used: {key}")
print(f"Key len: {len(key)}")

try:
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req) as response:
        print(f"Success! Status: {response.status}")
        print(response.read().decode())
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())
