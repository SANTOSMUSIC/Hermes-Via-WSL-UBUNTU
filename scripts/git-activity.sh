#!/usr/bin/env bash
# git-activity.sh - Helper untuk commit & push dengan log aktivitas terstruktur
# Usage: git-activity.sh "kategori" "deskripsi singkat" ["detail tambahan"]

set -euo pipefail

REPO_ROOT="/home/rafi_ansf/.hermes"
cd "$REPO_ROOT"

KATEGORI="${1:-chore}"
DESKRIPSI="${2:-update}"
DETAIL="${3:-}"

# Validasi kategori
case "$KATEGORI" in
  feat|fix|docs|config|refactor|chore|backup|security|profile|skill|kanban|script) ;;
  *) echo "Kategori tidak dikenal. Gunakan: feat|fix|docs|config|refactor|chore|backup|security|profile|skill|kanban|script"; exit 1 ;;
esac

# Cek apakah ada perubahan
if git diff --quiet && git diff --cached --quiet; then
  echo "Tidak ada perubahan untuk di-commit."
  exit 0
fi

# Tampilkan file yang berubah
echo "=== File yang berubah ==="
git status --short

# Buat pesan commit
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S WIB')
COMMIT_MSG="${KATEGORI}: ${DESKRIPSI}

Timestamp: ${TIMESTAMP}
Profile: $(basename "$(git config user.email 2>/dev/null || echo 'unknown')")"

if [[ -n "$DETAIL" ]]; then
  COMMIT_MSG="${COMMIT_MSG}

Detail:
${DETAIL}"
fi

# Commit
git add -A
git commit -m "$COMMIT_MSG"

# Push
echo "=== Push ke origin/main ==="
git push origin main

echo "=== Selesai ==="
git log --oneline -1