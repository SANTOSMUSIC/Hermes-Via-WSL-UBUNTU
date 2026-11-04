#!/usr/bin/env bash
# sync-ubuntu-logs.sh - Sync Ubuntu/WSL system logs ke repo Hermes
# Dijalankan manual atau via cron

set -euo pipefail

REPO_ROOT="/home/rafi_ansf/.hermes"
UBUNTU_LOGS_DIR="$REPO_ROOT/logs/ubuntu"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

mkdir -p "$UBUNTU_LOGS_DIR"

echo "=== Sync Ubuntu logs ke $UBUNTU_LOGS_DIR ==="

# Log files yang ingin di-track (pilih yang relevan)
LOG_FILES=(
    "/var/log/syslog"
    "/var/log/auth.log"
    "/var/log/kern.log"
    "/var/log/dmesg"
    "/var/log/dpkg.log"
    "/var/log/apt/history.log"
    "/var/log/cloud-init.log"
    "/var/log/cloud-init-output.log"
)

for log in "${LOG_FILES[@]}"; do
    if [[ -f "$log" ]]; then
        basename_log=$(basename "$log")
        # Copy dengan timestamp untuk history, dan symlink latest
        cp "$log" "$UBUNTU_LOGS_DIR/${basename_log}.${TIMESTAMP}" 2>/dev/null || true
        ln -sf "${basename_log}.${TIMESTAMP}" "$UBUNTU_LOGS_DIR/${basename_log}.latest" 2>/dev/null || true
        echo "  ✓ $log -> ${basename_log}.${TIMESTAMP}"
    else
        echo "  - $log (tidak ditemukan)"
    fi
done

# Journalctl logs (systemd) - hanya boot terakhir
echo "  ✓ journalctl (boot terakhir)"
journalctl --no-pager -b -0 --since "1 hour ago" > "$UBUNTU_LOGS_DIR/journalctl-last-boot.${TIMESTAMP}" 2>/dev/null || true
ln -sf "journalctl-last-boot.${TIMESTAMP}" "$UBUNTU_LOGS_DIR/journalctl-last-boot.latest" 2>/dev/null || true

# Hapus file lama > 30 hari (keep repo size manageable)
find "$UBUNTU_LOGS_DIR" -name "*.${TIMESTAMP%_*}_*" -mtime +30 -delete 2>/dev/null || true

echo "=== Selesai sync ==="
ls -lh "$UBUNTU_LOGS_DIR"/*.latest 2>/dev/null | head -10