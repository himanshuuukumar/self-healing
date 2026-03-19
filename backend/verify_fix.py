import asyncio
import json
import uuid
import sys
import os
from typing import Dict, List, Optional
from app.models import ErrorEntry, DiagnosisResult
from app.pipeline import LLMClient

# Ensure environment variables are set
os.environ["LLM_API_KEY"] = "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"
os.environ["LLM_MODEL"] = "google/gemini-2.0-flash-001"
os.environ["LLM_API_BASE"] = "https://openrouter.ai/api/v1"

async def test_generation():
    client = LLMClient()
    error = ErrorEntry(
        id=str(uuid.uuid4()),
        timestamp="2024-01-01T00:00:00Z",
        level="ERROR",
        service="order-service",
        file="services/order-service/controllers/orderController.py",
        line=34,
        error="'NoneType' object is not subscriptable",
        stack_trace="Traceback (most recent call last):\n  File \"orderController.py\", line 34, in create_order\n    user_id = payload['user']['id']\nTypeError: 'NoneType' object is not subscriptable",
        trace_id="test-trace"
    )
    
    chunks = [
        {
            "file": "services/order-service/controllers/orderController.py",
            "start_line": 30,
            "end_line": 40,
            "content": "def create_order(payload):\n    # Extract user info\n    user_id = payload['user']['id']\n    return user_id"
        }
    ]
    
    print("Generating plan...")
    plan = client.generate_plan(error, chunks)
    
    if plan:
        print("Success! Plan generated:")
        print(json.dumps(plan, indent=2))
    else:
        print("Plan generation failed (returned None). Check logs above.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_generation())
