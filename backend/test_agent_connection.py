import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-001")
base_url = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1")

print(f"Testing connection with model: {model}")
print(f"API Base: {base_url}")
print(f"Key loaded: {'Yes' if key else 'No'} (Starts with: {key[:10] if key else 'None'})")

if not key:
    print("Error: LLM_API_KEY not found in environment.")
    exit(1)

try:
    llm = ChatOpenAI(
        api_key=key,
        base_url=base_url,
        model=model,
    )
    
    print("Invoking LLM...")
    response = llm.invoke("Hello, are you online? Reply with 'Yes, I am online.'")
    print("\n--- Response from AI ---")
    print(response.content)
    print("------------------------")
    print("Success: Agent configuration is valid.")

except Exception as e:
    print(f"\nError: Connection failed. {e}")
