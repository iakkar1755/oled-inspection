#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/oled-inspection-repo"
APP="$HOME/oled-inspection-cloud"

cd "$REPO"
git pull --ff-only origin main

echo "Checking deployment files..."
test -f "$REPO/cloud/compose.yaml"
test -f "$REPO/cloud/api/main.py"
test -d "$APP/data"

echo "Checking code differences..."
diff -qr "$APP/api" "$REPO/cloud/api" || true
diff -u "$APP/compose.yaml" "$REPO/cloud/compose.yaml" || true

echo "Pre-deployment checks completed."
echo "No production files were changed."
