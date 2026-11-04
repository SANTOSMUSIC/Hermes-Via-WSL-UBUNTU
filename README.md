# Hermes-Via-WSL-UBUNTU

Repository konfigurasi **Hermes Agent** yang dijalankan di **WSL2 (Ubuntu)** dengan 7 profil, auto-commit log ke Git + Git LFS, dan sinkronisasi log sistem Ubuntu.

> **Repositori ini hanya berisi konfigurasi, script otomatisasi, dan log aktivitas.**
> Binary Hermes, database, dan secret (API key) **tidak termasuk** — harus di-setup manual setelah clone.

---

## 📦 Isi Repository

| Folder/File | Deskripsi |
|-------------|-----------|
| `config.yaml` | Konfigurasi root Hermes (provider, model, gateway, dll) |
| `SOUL.md` | Definisi "soul" / identitas agent |
| `scripts/` | Script otomatisasi Git + log sync |
| `logs/` | Log Hermes root + log sistem Ubuntu (via Git LFS) |
| `profiles/*/logs/` | Log 7 profil: backend, frontend, qa, researcher, reviewer, supermaster, writer (via Git LFS) |
| `.gitignore` | Aturan ignore (secret, db, cache, runtime) |
| `.gitattributes` | Konfigurasi Git LFS untuk file log besar |
| `skills/` | Skill global (jika ada) |

---

## 🚀 Quick Start (Clone & Setup)

### 1. Prasyarat
- **WSL2 + Ubuntu** (atau Linux native)
- **Git** + **Git LFS**
- **Hermes Agent** (install terlebih dahulu)

### 2. Install Hermes Agent
```bash
# Install binary, Python terisolasi, gateway
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Verifikasi
hermes --version
```

### 3. Clone Repository Ini
```bash
# Clone ke lokasi default Hermes (~/.hermes)
git clone https://github.com/SANTOSMUSIC/Hermes-Via-WSL-UBUNTU.git ~/.hermes
cd ~/.hermes

# Setup Git LFS (WAJIB untuk log files)
git lfs install
git lfs pull
```

### 4. Konfigurasi Secret (TIDAK di-track Git)
```bash
# Buat file .env dari template atau manual
cat > .env << 'EOF'
# Provider API Keys (isi sendiri)
NVIDIA_API_KEY=your_nvidia_nim_key
OPENROUTER_API_KEY=your_openrouter_key
# TAMBAHKAN KEY LAIN SESUAI KEBUTUHAN
EOF

# Atau copy dari backup sendiri
# cp /path/to/your/.env ~/.hermes/.env
```

### 5. Login Provider & Auth
```bash
# Login ke provider yang dipakai (NVIDIA NIM, OpenRouter, dll)
hermes auth login
# Ikuti instruksi browser/CLI
```

### 6. Perbaiki Path di config.yaml (WAJIB)
`config.yaml` mengandung path absolut `/home/rafi_ansf/.hermes/...`. **Ganti ke home directory Anda:**

```bash
# Otomatis (sed)
sed -i "s|/home/rafi_ansf|$HOME|g" config.yaml

# Atau manual edit config.yaml, cari dan ganti semua:
# /home/rafi_ansf/.hermes  →  /home/<USER_ANDA>/.hermes
```

### 7. Buat Profil (Sesuai Kebutuhan)
Repo ini punya 7 profil. Buat yang Anda butuhkan:

```bash
# Contoh: buat profil supermaster
hermes profile create supermaster

# Lainnya: backend, frontend, qa, researcher, reviewer, writer
hermes profile create backend
hermes profile create frontend
# ... dst
```

### 8. Sync Skill (Opsional)
Jika ingin skill dari profil supermaster ke profil lain:
```bash
hermes skill sync --from supermaster --to backend,frontend,qa,researcher,reviewer,writer
```

### 9. Pasang Cron Job Auto-Log (Opsional tapi Direkomendasikan)
```bash
# Setiap 15 menit: sync Ubuntu logs + commit log changes ke Git
(crontab -l 2>/dev/null; echo "*/15 * * * * $HOME/.hermes/scripts/auto-log-commit.sh >> $HOME/.hermes/logs/auto-log-commit.cron.log 2>&1") | crontab -

# Verifikasi
crontab -l
```

### 10. Start Gateway & Test
```bash
# Start gateway daemon
hermes gateway start

# Test chat
hermes chat -p supermaster "Hello, apakah Hermes berjalan?"
```

---

## 📜 Script Otomatisasi (Di `scripts/`)

| Script | Fungsi | Cara Pakai |
|--------|--------|------------|
| `git-activity.sh` | Commit + push dengan format log terstruktur | `./scripts/git-activity.sh "config" "ubah model" "ganti ke kimi-k2.6"` |
| `auto_git_activity.py` | Wrapper Python (dipanggil assistant otomatis) | `python3 -m scripts.auto_git_activity "feat" "tambah fitur" "detail"` |
| `sync-ubuntu-logs.sh` | Sync log sistem Ubuntu (`/var/log/*`) ke `logs/ubuntu/` | `./scripts/sync-ubuntu-logs.sh` |
| `auto-log-commit.sh` | Cron job: sync + commit log changes tiap 15 menit | Otomatis via cron |

**Format Commit:**
```
<kategori>: <deskripsi>

Timestamp: 2026-11-04 20:45:00 WIB
Profile: supermaster

Detail:
<detail tambahan>
```

**Kategori Valid:** `feat`, `fix`, `docs`, `config`, `refactor`, `chore`, `backup`, `security`, `profile`, `skill`, `kanban`, `script`

---

## 🗂️ Struktur Profil (7 Profil)

| Profil | Peran | Use Case |
|--------|-------|----------|
| `supermaster` | Project lead, dispatcher | Kanban, planning, delegasi |
| `backend` | NestJS + TypeScript + Prisma | API, database, auth |
| `frontend` | React + TypeScript + Vite + Tailwind | UI, component, state |
| `qa` | Testing, dogfood, checklist | E2E, contract test, security scan |
| `reviewer` | Code review, security audit | PR review, static analysis |
| `researcher` | Web research, paper lookup | Arxiv, competitor monitor, wiki |
| `writer` | Documentation, changelog | Markdown, DESIGN.md, release notes |

---

## 📊 Log & Git LFS

### Log yang Di-track
- **Hermes root**: `logs/agent.log`, `errors.log`, `gateway.log`, `install.log`, curator reports
- **7 Profil**: `profiles/<name>/logs/agent.log`, `errors.log`, `gateway.log`, process results
- **Ubuntu/WSL**: `logs/ubuntu/syslog*`, `auth.log*`, `kern.log*`, `dmesg*`, `journalctl*`, `dpkg.log*`, `apt/history.log*`

### Git LFS
File log > 500KB disimpan di Git LFS (bukan Git repo biasa):
```bash
# LFS tracking patterns (di .gitattributes)
logs/agent.log
logs/errors.log
profiles/*/logs/agent.log
profiles/*/logs/errors.log
logs/ubuntu/syslog*
logs/ubuntu/auth.log*
logs/ubuntu/kern.log*
logs/ubuntu/dmesg*
logs/ubuntu/journalctl*
```

### Ukuran Repo
- **Git objects**: ~200 KB (hanya pointer LFS)
- **LFS storage (GitHub)**: ~13 MB (file log aktual)
- **Total**: Jauh di bawah batas 1 GB GitHub

### Auto-Commit Log
- **Cron (15 menit)**: `auto-log-commit.sh` → sync Ubuntu logs → commit & push log changes
- **Assistant (setiap tugas)**: `auto_git_activity.py` → sync → commit aktivitas → commit log changes → push

---

## ⚠️ Catatan Penting

### Yang TIDAK Masuk Git (di-ignore)
| File/Folder | Alasan |
|-------------|--------|
| `.env`, `auth.json` | API key, token, secret |
| `state.db*`, `kanban.db*`, `shared-state.db` | SQLite database runtime |
| `cache/`, `sessions/`, `runtime/`, `state/` | Cache & temp files |
| `models_dev_cache.json` (5.9 MB) | Cache model provider |
| `tools/`, `hermes-agent/` | Binary & core (install ulang via script) |

### Path Absolut di config.yaml
Semua path di `config.yaml` menggunakan `/home/rafi_ansf/.hermes/...`. **WAJIB diganti** ke `$HOME/.hermes` user baru.

### Provider & Model
Konfigurasi saat ini:
- **Main chat**: 9Router (localhost:20128) → model `hermes-kuat`
- **Fallback**: NVIDIA NIM → `moonshotai/kimi-k2.6` (gratis, 40 RPM)
- **Vision**: Tidak aktif (`auxiliary.vision` unset)

User baru harus setup provider mereka sendiri di `.env` dan `config.yaml`.

---

## 🔄 Workflow Harian

### Untuk Pengembang (Assistant)
```bash
# Setelah selesaikan tugas, assistant otomatis jalankan:
python3 -m scripts.auto_git_activity "config" "ubah temperature" "set 0.7 untuk creative writing"
```

### Untuk Manual Sync Log Ubuntu
```bash
./scripts/sync-ubuntu-logs.sh
./scripts/auto-log-commit.sh
```

### Untuk Lihat Status Log LFS
```bash
git lfs ls-files
git lfs status
```

---

## 🛠️ Troubleshooting

### Git LFS Error: "git-lfs: command not found"
```bash
# Install Git LFS binary lokal
cd /tmp
wget -q https://github.com/git-lfs/git-lfs/releases/download/v3.5.1/git-lfs-linux-amd64-v3.5.1.tar.gz
tar -xzf git-lfs-linux-amd64-v3.5.1.tar.gz
mkdir -p ~/.local/bin
cp git-lfs-3.5.1/git-lfs ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
git lfs install
```

### Cron Tidak Jalan / Log Tidak Ter-commit
```bash
# Cek cron aktif
crontab -l

# Cek log cron
cat ~/.hermes/logs/auto-log-commit.cron.log

# Jalankan manual untuk debug
~/.hermes/scripts/auto-log-commit.sh
```

### Push Gagal: "Could not resolve host: github.com"
```bash
# Cek koneksi / proxy / DNS
ping github.com
# Atau gunakan SSH URL jika sudah setup SSH key
git remote set-url origin git@github.com:SANTOSMUSIC/Hermes-Via-WSL-UBUNTU.git
```

### Config Path Masih Menunjuk ke User Lama
```bash
# Cek path di config.yaml
grep -n "rafi_ansf" config.yaml

# Fix otomatis
sed -i "s|/home/rafi_ansf|$HOME|g" config.yaml
```

---

## 📝 Changelog

| Tanggal | Commit | Perubahan |
|---------|--------|-----------|
| 2026-11-04 | `7b3ebaf` | Initial commit: Hermes config dengan 7 profil |
| 2026-11-04 | `95e09dd` | Tambah helper `git-activity.sh` |
| 2026-11-04 | `dc4631c` | Tambah `auto_git_activity.py` + ignore `__pycache__` |
| 2026-11-04 | `d4943ee` | Track semua log Hermes (unignore `logs/` dan `profiles/*/logs/`) |
| 2026-11-04 | `671b9d5` | Tambah `sync-ubuntu-logs.sh` + initial Ubuntu logs |
| 2026-11-04 | `a9c8e21` | Enhance `auto_git_activity.py`: sync Ubuntu logs + auto-commit log changes |
| 2026-11-04 | `7b42b55` | Tambah `auto-log-commit.sh` + cron job 15 menit |
| 2026-11-04 | `84018e9` | Add Git LFS tracking untuk file log besar |
| 2026-11-04 | `c35d553` | Migrate large log files ke Git LFS (13 MB uploaded) |
| 2026-11-04 | `f19d306` | Update scripts PATH untuk Git LFS binary |

---

## 🔗 Link Terkait

- **Repository**: https://github.com/SANTOSMUSIC/Hermes-Via-WSL-UBUNTU
- **Hermes Agent Docs**: https://hermes-agent.nousresearch.com/docs
- **Git LFS Docs**: https://git-lfs.github.com/
- **NVIDIA NIM Limits**: https://docs.api.nvidia.com/nim/reference/limits

---

## 📄 License

Konfigurasi pribadi untuk keperluan development. Tidak untuk redistribusi komersial tanpa izin.

---

**Dibuat dengan ❤️ menggunakan Hermes Agent + WSL2 Ubuntu**