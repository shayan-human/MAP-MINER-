#!/bin/bash
# Unified Startup Script for Map Miner

echo "Stopping any existing Map Miner processes..."
pkill -f "go run main.go -web" || true
pkill -f "python3 turbo/server.py" || true

mkdir -p .tmp

echo "Starting Go Backend (Port 8080) in background..."
go run main.go -web > .tmp/backend.log 2>&1 &

echo "Waiting for backend initialization..."
sleep 5

echo "Starting Turbo Dashboard (Port 8000)..."
PYTHONPATH=. python3 turbo/server.py
