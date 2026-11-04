#!/usr/bin/env python3
"""
Auto Git Activity Logger
Dipanggil otomatis di akhir setiap tugas oleh assistant.
Usage: python3 -m scripts.auto_git_activity "kategori" "deskripsi" "detail"
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/home/rafi_ansf/.hermes")
SCRIPT = REPO_ROOT / "scripts" / "git-activity.sh"

KATEGORI_VALID = {
    "feat", "fix", "docs", "config", "refactor", "chore",
    "backup", "security", "profile", "skill", "kanban", "script"
}

def log_activity(kategori: str, deskripsi: str, detail: str = "") -> bool:
    """Log aktivitas ke git. Return True jika berhasil."""
    if kategori not in KATEGORI_VALID:
        print(f"[WARN] Kategori '{kategori}' tidak valid. Gunakan: {', '.join(sorted(KATEGORI_VALID))}")
        return False

    if not SCRIPT.exists():
        print(f"[ERROR] Script tidak ditemukan: {SCRIPT}")
        return False

    try:
        cmd = [str(SCRIPT), kategori, deskripsi]
        if detail:
            cmd.append(detail)

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            # Ambil hash commit terakhir
            git_log = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=REPO_ROOT, capture_output=True, text=True
            )
            commit_hash = git_log.stdout.strip()
            print(f"[GIT] ✓ {commit_hash}")
            return True
        elif "Tidak ada perubahan" in result.stdout:
            print(f"[GIT] - Tidak ada perubahan untuk di-commit")
            return True
        else:
            print(f"[GIT] ✗ Gagal: {result.stderr.strip() or result.stdout.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("[GIT] ✗ Timeout (60s)")
        return False
    except Exception as e:
        print(f"[GIT] ✗ Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 -m scripts.auto_git_activity <kategori> <deskripsi> [detail]")
        sys.exit(1)

    kategori = sys.argv[1]
    deskripsi = sys.argv[2]
    detail = sys.argv[3] if len(sys.argv) > 3 else ""

    success = log_activity(kategori, deskripsi, detail)
    sys.exit(0 if success else 1)