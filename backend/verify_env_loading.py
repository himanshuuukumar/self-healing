import asyncio
import os
import sys

# Ensure we're running from backend root
sys.path.append(os.getcwd())

from app.pipeline import LLMClient, LLM_API_BASE, LLM_MODEL

async def verify():
    print(f"LLM_API_BASE: {LLM_API_BASE}")
    print(f"LLM_MODEL: {LLM_MODEL}")
    
    client = LLMClient()
    print(f"Client API Key Present: {bool(client.api_key)}")
    if client.api_key:
        print(f"Client API Key Prefix: {client.api_key[:8]}...")
    else:
        print("Client API Key is Missing/Empty")

    # Mock error for generation test
    from app.models import ErrorEntry
    import uuid
    
    error = ErrorEntry(
        id=str(uuid.uuid4()),
        timestamp="2024-01-01T00:00:00Z",
        level="ERROR",
        service="test",
        file="test.py",
        line=1,
        error="Test error",
        stack_trace="Traceback...",
        trace_id="test-trace"
    )
    
    chunks = [{"file": "test.py", "start_line": 1, "end_line": 1, "content": "print('hello')"}]
    
    print("Attempting generation...")
    try:
        plan = client.generate_plan(error, chunks)
        if plan:
            print("Plan generated successfully!")
        else:
            print("Plan generation returned None.")
    except Exception as e:
        print(f"Plan generation crashed: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(verify())
