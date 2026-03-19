import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from dataclasses import dataclass

# Manually mock the environment
os.environ["LLM_API_KEY"] = "AIzaSyDUamuH6Bdwe-KkBa6dMT4rQnbVAYXvrQ8"
os.environ["LLM_API_BASE"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
os.environ["LLM_MODEL"] = "gemini-2.0-flash"
os.environ["LLM_TIMEOUT_SECONDS"] = "30"

LLM_API_BASE = os.environ["LLM_API_BASE"]
LLM_MODEL = os.environ["LLM_MODEL"]
LLM_TIMEOUT_SECONDS = int(os.environ["LLM_TIMEOUT_SECONDS"])

@dataclass
class ErrorEntry:
    id: str
    timestamp: str
    level: str
    service: str
    file: str
    line: int
    error: str
    stack_trace: str
    trace_id: str

class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("LLM_API_KEY")

    def enabled(self) -> bool:
        return bool(self.api_key)

    def generate_plan(self, error: ErrorEntry, chunks: List[Dict]) -> Optional[Dict]:
        if not self.enabled():
            print("LLM not enabled")
            return None

        condensed_chunks = []
        for chunk in chunks[:3]:
            condensed_chunks.append(
                {
                    "file": chunk["file"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"][:2200],
                }
            )

        system = (
            "You are a senior debugging agent. Diagnose root cause from logs and code chunks. "
            "Operate in Observe & Recommend mode: identify issue, where it occurs, and recommended fix steps. "
            "Return strict JSON with fields: issue_summary, root_cause, affected_file, affected_line, "
            "before, after, solution_steps(array of strings), confidence(0-100)."
        )
        user_prompt = {
            "error": {
                "message": error.error,
                "file": error.file,
                "line": error.line,
                "stack_trace": error.stack_trace,
                "service": error.service,
            },
            "chunks": condensed_chunks,
            "task": "Find the likely bug location and produce a minimal, safe fix recommendation.",
        }
        
        # Ensure base URL creates a valid path
        base_url = LLM_API_BASE.rstrip("/")
        
        payload = {
            "model": LLM_MODEL,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
        }
        
        url = f"{base_url}/chat/completions"
        print(f"Requesting URL: {url}")
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as response:
                body = response.read().decode("utf-8")
                print(f"Response status: {response.status}")
                print(f"Response body: {body[:200]}...") # Print first 200 chars

            parsed = json.loads(body)
            content = parsed["choices"][0]["message"]["content"]
            
            # Clean markdown code blocks from response
            if content.strip().startswith("```"):
                content = content.strip().split("\n", 1)[1]
                if content.strip().endswith("```"):
                    content = content.strip()[:-3]
            
            plan = json.loads(content)
            return plan
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} {e.reason}")
            print(f"Error body: {e.read().decode('utf-8')}")
            raise
        except Exception as e:
            print(f"General Error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    client = LLMClient()
    
    # Debug: List models
    print("Listing models...")
    base_url = LLM_API_BASE.rstrip("/")
    req = urllib.request.Request(
        f"{base_url}/models",
        headers={"Authorization": f"Bearer {client.api_key}"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to list models: {e}")

    # Mock error from logs
    error = ErrorEntry(
        id="test-id",
        timestamp="2023-01-01T00:00:00Z",
        level="ERROR",
        service="order-service",
        file="services/order-service/controllers/orderController.py",
        line=34,
        error="'NoneType' object is not subscriptable",
        stack_trace="Traceback ... delivery_pincode = user['address']['pincode']",
        trace_id="trace-1"
    )
    
    # Mock chunk
    chunks = [{
        "file": "services/order-service/controllers/orderController.py",
        "start_line": 30,
        "end_line": 40,
        "content": "def create_order(user):\n    delivery_pincode = user['address']['pincode']\n    return delivery_pincode"
    }]
    
    print("Running LLM test...")
    plan = client.generate_plan(error, chunks)
    print("Plan generated successfully:")
    print(json.dumps(plan, indent=2))
