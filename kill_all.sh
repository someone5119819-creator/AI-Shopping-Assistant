#!/bin/bash

# --- CONFIGURATION ---
echo "🛑 Shutting down Shopify RAG AI Assistant Suite..."

# Function to kill process on a port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port)
    if [ ! -z "$pids" ]; then
        echo "⚠️ Killing processes on port $port..."
        # Use echo and xargs to handle multiple PIDs securely
        echo "$pids" | xargs kill -9 2>/dev/null
    fi
}

# --- KILL ALL SERVICES ---
kill_port 8000   # Search API
kill_port 8001   # Assistant API
kill_port 8080   # Hybrid UI (SimpleHTTPServer)
kill_port 5173   # Vite Dev Server

echo "✅ All servers stopped."
