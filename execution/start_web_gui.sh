#!/bin/bash
# Start Map Miner Web UI using Docker

DATA_FOLDER="$PWD/gmapsdata"
mkdir -p "$DATA_FOLDER"

# Stop and remove existing container if it exists
docker stop gmaps-web 2>/dev/null
docker rm gmaps-web 2>/dev/null

echo "Starting Map Miner Web UI on port 8080..."
docker run -d \
  --name gmaps-web \
  -v "$DATA_FOLDER:/gmapsdata" \
  -p 8080:8080 \
  google-maps-scraper \
  -web -data-folder /gmapsdata

echo "Web UI is starting. It will be available at http://localhost:8080"
echo "Note: Results may take a few minutes to appear initially."
