import os
import json
import urllib.request

# Configuration
key = "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"
model = "google/gemini-2.0-flash-001"
url = "https://openrouter.ai/api/v1/chat/completions"

# Prompt setup (simplified from pipeline.py)
system = "You are a debugging assistant. Return valid JSON."
user_prompt = {"task": "test", "content": "test"}

payload = {
    "model": model,
    "temperature": 0.1,
    "response_format": {"type": "json_object"},
    "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user_prompt)},
    ],
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}",
    "HTTP-Referer": "http://localhost:3000", # OpenRouter often asks for this
    "X-Title": "Proctor",
}

print(f"Sending request to {model}...")

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
