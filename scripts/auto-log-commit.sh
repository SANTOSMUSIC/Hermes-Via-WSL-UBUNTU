#!/usr/bin/env bash
# auto-log-commit.sh - Dijalankan via cron setiap 15 menit
# Sync Ubuntu logs + commit perubahan log Hermes

set -euo pipefail

REPO_ROOT="/home/rafi_ansf/.hermes"
cd "$REPO_ROOT"

# Load environment
export PATH="/home/rafi_ansf/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S WIB')

echo "=== [$TIMESTAMP] Auto log commit started ==="

# 1. Sync Ubuntu logs
if [[ -x scripts/sync-ubuntu-logs.sh ]]; then
    scripts/sync-ubuntu-logs.sh >/dev/null 2>&1 || true
fi

# 2. Check for any changes in logs
if git status --porcelain logs/ profiles/*/logs/ 2>/dev/null | grep -q .; then
    echo "  Log changes detected, committing..."
    git add logs/ profiles/*/logs/
    git commit -m "chore: auto-commit log updates

Timestamp: $TIMESTAMP
Auto-committed by cron job" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1 || true
    echo "  ✓ Log changes pushed"
else
    echo "  No log changes"
fi

echo "=== [$TIMESTAMP] Auto log commit finished ==="