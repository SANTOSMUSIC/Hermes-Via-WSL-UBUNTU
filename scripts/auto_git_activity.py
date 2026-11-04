#!/usr/bin/env python3
"""
Auto Git Activity Logger + Log Sync
Dipanggil otomatis di akhir setiap tugas oleh assistant.
Usage: python3 -m scripts.auto_git_activity "kategori" "deskripsi" "detail"
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/home/rafi_ansf/.hermes")
GIT_ACTIVITY_SCRIPT = REPO_ROOT / "scripts" / "git-activity.sh"
SYNC_UBUNTU_LOGS = REPO_ROOT / "scripts" / "sync-ubuntu-logs.sh"

KATEGORI_VALID = {
    "feat", "fix", "docs", "config", "refactor", "chore",
    "backup", "security", "profile", "skill", "kanban", "script"
}

def run_cmd(cmd, cwd=None, capture=True, timeout=60):
    """Run command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd or REPO_ROOT,
            capture_output=capture, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout ({timeout}s)"
    except Exception as e:
        return False, "", str(e)

def sync_ubuntu_logs() -> bool:
    """Sync Ubuntu/WSL system logs to repo."""
    if not SYNC_UBUNTU_LOGS.exists():
        return False
    success, stdout, stderr = run_cmd([str(SYNC_UBUNTU_LOGS)], timeout=30)
    if success:
        print(f"[SYNC] ✓ Ubuntu logs synced")
    else:
        print(f"[SYNC] ⚠ {stderr.strip() or stdout.strip()}")
    return success

def commit_log_changes() -> bool:
    """Commit any log file changes (Hermes + Ubuntu)."""
    # Check if there are log changes
    success, stdout, _ = run_cmd(["git", "status", "--porcelain", "logs/", "profiles/*/logs/"])
    if not success or not stdout.strip():
        return True  # No log changes

    # Add and commit log changes
    run_cmd(["git", "add", "logs/", "profiles/*/logs/"])
    msg = f"chore: auto-commit log updates\n\nTimestamp: $(date '+%Y-%m-%d %H:%M:%S WIB')\nAuto-committed after activity"
    success, stdout, stderr = run_cmd(["git", "commit", "-m", msg])
    if success:
        print(f"[GIT] ✓ Log changes committed")
    else:
        print(f"[GIT] ⚠ Log commit: {stderr.strip()}")
    return success

def log_activity(kategori: str, deskripsi: str, detail: str = "") -> bool:
    """Log aktivitas ke git + sync logs. Return True jika berhasil."""
    if kategori not in KATEGORI_VALID:
        print(f"[WARN] Kategori '{kategori}' tidak valid. Gunakan: {', '.join(sorted(KATEGORI_VALID))}")
        return False

    if not GIT_ACTIVITY_SCRIPT.exists():
        print(f"[ERROR] Script tidak ditemukan: {GIT_ACTIVITY_SCRIPT}")
        return False

    # 1. Sync Ubuntu logs first
    sync_ubuntu_logs()

    # 2. Run main git activity (commits config/skill/script changes)
    try:
        cmd = [str(GIT_ACTIVITY_SCRIPT), kategori, deskripsi]
        if detail:
            cmd.append(detail)

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            git_log = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=REPO_ROOT, capture_output=True, text=True
            )
            commit_hash = git_log.stdout.strip()
            print(f"[GIT] ✓ {commit_hash}")
        elif "Tidak ada perubahan" in result.stdout:
            print(f"[GIT] - Tidak ada perubahan untuk di-commit")
        else:
            print(f"[GIT] ✗ Gagal: {result.stderr.strip() or result.stdout.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("[GIT] ✗ Timeout (60s)")
        return False
    except Exception as e:
        print(f"[GIT] ✗ Error: {e}")
        return False

    # 3. Commit any log changes that happened during the activity
    commit_log_changes()

    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 -m scripts.auto_git_activity <kategori> <deskripsi> [detail]")
        sys.exit(1)

    kategori = sys.argv[1]
    deskripsi = sys.argv[2]
    detail = sys.argv[3] if len(sys.argv) > 3 else ""

    success = log_activity(kategori, deskripsi, detail)
    sys.exit(0 if success else 1)