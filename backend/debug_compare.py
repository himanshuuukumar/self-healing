import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# 1. Pipeline simulation
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL")

print(f"Key: '{LLM_API_KEY}' (len={len(LLM_API_KEY) if LLM_API_KEY else 0})")
print(f"Base: '{LLM_API_BASE}'")
print(f"Model: '{LLM_MODEL}'")

url = f"{LLM_API_BASE}/chat/completions"
# Simulating the exact payload structure from pipeline
payload = {
    "model": LLM_MODEL,
    "temperature": 0.1,
    "response_format": {"type": "json_object"},
    "messages": [
        {"role": "system", "content": "You are Proctor."},
        {"role": "user", "content": json.dumps({"task": "test"})},
    ],
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LLM_API_KEY}",
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "Proctor",
}

print("--- Request Details ---")
print(f"URL: {url}")
print(f"Headers: {headers}")
# print(f"Payload: {payload}")

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        print(f"Success: {response.status}")
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"Failed: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
