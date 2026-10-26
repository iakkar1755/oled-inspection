#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/oled-inspection-repo"
APP="$HOME/oled-inspection-cloud"

echo "1. Updating repository..."
cd "$REPO"
git pull --ff-only origin main

echo "2. Checking production data..."
test -d "$APP/data"
test -f "$APP/data/oled_inspection.db"

echo "3. Synchronizing application code..."
rsync -av --exclude='*.save' "$REPO/cloud/api/" "$APP/api/"
cp "$REPO/cloud/compose.yaml" "$APP/compose.yaml"

echo "4. Rebuilding API container..."
cd "$APP"
sudo docker compose up -d --build api

echo "5. Checking API health..."
curl --fail --retry 10 --retry-delay 3 \
  http://127.0.0.1:8000/api/health

echo
echo "Deployment completed successfully."