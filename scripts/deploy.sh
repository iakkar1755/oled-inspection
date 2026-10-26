#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/oled-inspection-repo"
APP="$HOME/oled-inspection-cloud"

echo "1. Checking deployment files..."
test -f "$REPO/cloud/api/main.py"
test -f "$REPO/cloud/compose.yaml"
test -f "$APP/data/oled_inspection.db"

command -v rsync >/dev/null
sudo -n docker compose version >/dev/null

echo "2. Backing up current application code..."
mkdir -p "$HOME/oled-backups"
tar -czf "$HOME/oled-backups/pre-deploy-code.tar.gz" \
  -C "$APP" api compose.yaml

echo "3. Synchronizing application code..."
rsync -av --exclude='*.save' \
  "$REPO/cloud/api/" "$APP/api/"

cp "$REPO/cloud/compose.yaml" "$APP/compose.yaml"

echo "4. Rebuilding Docker API..."
cd "$APP"
sudo -n docker compose up -d --build api

echo "5. Checking API health..."
curl --fail --silent --show-error \
  --retry 15 --retry-delay 3 \
  --retry-connrefused \
  http://127.0.0.1:8000/api/health

echo
echo "Deployment completed successfully."