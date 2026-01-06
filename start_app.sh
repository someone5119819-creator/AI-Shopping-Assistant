#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $(jobs -p)
    exit
}

trap cleanup SIGINT SIGTERM

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: No virtual environment found at ./venv"
fi

echo "Starting Search API (FastAPI) on port 8000..."
python api.py &
SEARCH_PID=$!

echo "Starting Assistant API (Flask) on port 8001..."
python assistant_api.py &
ASSISTANT_PID=$!

echo "Starting Frontend (Vite)..."
cd frontend_react
npm run dev -- --open &
FRONTEND_PID=$!

echo "All services started. Press Ctrl+C to stop."
wait
