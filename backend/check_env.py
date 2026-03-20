from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL")

print(f"API_KEY is {'set' if api_key else 'not set'}")
if api_key:
    print(f"Key starts with: {api_key[:10]}...")
print(f"Model: {model}")
