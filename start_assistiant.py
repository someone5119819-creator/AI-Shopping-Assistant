"""
Unified Startup Script
Runs Flask API (port 8001) and Gemini Live WebSocket Server (port 8002) concurrently
"""
import subprocess
import sys
import os

def run_server(script_name, port_name):
    """Run a Python script in a subprocess"""
    python_path = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    return subprocess.Popen([python_path, script_path])

if __name__ == "__main__":
    print("🚀 Starting AI Assistant Stack...")
    
    # Start Flask API (assistant_api.py)
    flask_process = run_server("assistant_api.py", "8001")
    print("✅ Flask API started on port 8001")
    
    # Start Gemini Live WebSocket Server (gemini_live_handler.py)
    live_process = run_server("gemini_live_handler.py", "8002")
    print("✅ Gemini Live API started on port 8002 (WebSocket)")
    
    print("\n📡 Services Running:")
    print("   - REST API: http://localhost:8001")
    print("   - WebSocket: ws://localhost:8002")
    print("\nPress Ctrl+C to stop all services\n")
    
    try:
        # Wait for both processes
        flask_process.wait()
        live_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        flask_process.terminate()
        live_process.terminate()
        flask_process.wait()
        live_process.wait()
        print("✅ All services stopped")
