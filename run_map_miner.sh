#!/bin/bash
echo "Starting Map Miner..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Start the Go backend server in the background
echo "Starting core map-miner server..."
go run main.go -web &
GO_PID=$!

# Wait a few seconds for Go server to start
sleep 3

# Activate virtual environment and start Turbo Dashboard
echo "Starting Turbo Dashboard..."
source venv/bin/activate
export PYTHONPATH=.

# Open browser if on macOS or Linux with xdg-open
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000
fi

python3 turbo/server.py

# When python server exits, kill the Go server
kill $GO_PID
