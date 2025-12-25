import sys
if sys.version_info < (3, 10):
    try:
        import importlib.metadata
        import importlib_metadata
        if not hasattr(importlib.metadata, "packages_distributions"):
            importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
    except ImportError:
        pass

from agent_graph import graph
from langchain_core.messages import HumanMessage
import uuid
import os

# Mock API Key if not present (though it should be in env), 
# or we expect it to fail if key missing, which captures the error.
if not os.getenv("GEMINI_API_KEY"):
    print("Warning: GEMINI_API_KEY not set in env")

try:
    print("Graph compiled successfully.")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("Invoking graph with 'Hello'...")
    inputs = {"messages": [HumanMessage(content="Hello")]}
    result = graph.invoke(inputs, config=config)
    
    print("Graph Result:")
    print(result['messages'][-1].content)
    
    print("\nTest passed.")
except Exception as e:
    print(f"Graph verification failed: {e}")
