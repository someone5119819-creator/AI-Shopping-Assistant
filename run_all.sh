#!/bin/bash

# --- CONFIGURATION ---
PROJECT_ROOT="/Users/tculesmba-3/.gemini/antigravity/scratch/shopify_rag"
FRONTEND_DIR="$PROJECT_ROOT/frontend_react"

# --- COOL ASCII ART ---
echo -e "\033[1;35m"
echo "    _    ____ ____     ___ ____ ____     _____ _____ _   _ _____ "
echo "   / \  / ___/ ___|   |_ _/ ___/ ___|   |_   _| ____| \ | |_   _|"
echo "  / _ \ \___ \___ \    | |\___ \___ \     | | |  _| |  \| | | |  "
echo " / ___ \ ___) |__) |   | | ___) |__) |    | | | |___| |\  | | |  "
echo "/_/   \_\____/____/   |___|____/____/     |_| |_____|_| \_| |_|  "
echo -e "\033[0m"
echo -e "\033[1;36m🚀 Starting Shopify RAG AI Assistant Suite...\033[0m"

# Function to kill process on a port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "⚠️ Killing existing process on port $port (PID: $pid)..."
        kill -9 $pid
    fi
}

# --- CLEANUP ---
kill_port 8000
kill_port 8001
kill_port 8080
kill_port 5173

# --- START SERVICES ---

# 1. Search API (Port 8000)
echo "📡 Starting Search API (Port 8000)..."
cd "$PROJECT_ROOT"
source venv/bin/activate
python api.py > /tmp/search_api.log 2>&1 &

# 2. Assistant API (Port 8001)
echo "🧠 Starting Assistant API (Port 8001)..."
python assistant_api.py > /tmp/assistant_api.log 2>&1 &

# 3. Hybrid Search UI (Port 8080)
echo "🔍 Starting Hybrid Search UI (Port 8080)..."
python3 -m http.server 8080 > /tmp/hybrid_ui.log 2>&1 &

# 4. AI Assistant UI (Port 5173)
echo "🌐 Starting AI Assistant UI (Port 5173)..."
cd "$FRONTEND_DIR"
npm run dev -- --port 5173 > /tmp/assistant_ui.log 2>&1 &

echo "------------------------------------------------"
echo -e "\033[1;32m✅ All systems go!\033[0m"
echo "------------------------------------------------"
echo "🔗 Hybrid Search UI: http://localhost:8080/frontend.html"
echo "🔗 AI Assistant UI:  http://localhost:5173"
echo "🔗 Search API Docs:  http://localhost:8000/docs"
echo "------------------------------------------------"
echo "📝 Logs are available in /tmp/ (search_api.log, assistant_api.log, etc.)"
