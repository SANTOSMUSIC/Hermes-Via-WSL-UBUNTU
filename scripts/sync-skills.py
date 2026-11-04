#!/usr/bin/env python3
"""
Sync skills from supermaster -> other profiles (one-way, additive only).
Only copies skills that don't already exist in target profile.
Backs up target profile skills dir before any changes.
"""
import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
# If HERMES_HOME points to a profile dir (contains config.yaml and parent is profiles/), go up to .hermes root
if (HERMES_HOME / "config.yaml").exists() and HERMES_HOME.parent.name == "profiles":
    HERMES_HOME = HERMES_HOME.parent.parent
elif (HERMES_HOME / "profiles").exists():
    # Already at root
    pass
elif HERMES_HOME.parent.name == "profiles":
    HERMES_HOME = HERMES_HOME.parent.parent
SOURCE_PROFILE = "supermaster"
TARGET_PROFILES = ["backend", "frontend", "qa", "reviewer", "researcher", "writer"]

SKILLS_DIR_NAME = "skills"

def get_skill_dirs(profile: str) -> Path:
    return HERMES_HOME / "profiles" / profile / SKILLS_DIR_NAME

def list_skills(skills_dir: Path) -> set[str]:
    """Return set of skill directory names (recursive, excluding hidden dirs/files)"""
    if not skills_dir.exists():
        return set()
    skills = set()
    for root, dirs, files in os.walk(skills_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        # Check if this directory contains a SKILL.md (skill root)
        if "SKILL.md" in files:
            # Get relative path from skills_dir
            rel = Path(root).relative_to(skills_dir)
            skills.add(str(rel))
    return skills

def backup_skills_dir(skills_dir: Path, timestamp: str) -> Path:
    """Create timestamped backup of skills directory"""
    backup_root = HERMES_HOME / "backups" / timestamp / "skills"
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / skills_dir.parent.name
    if skills_dir.exists():
        shutil.copytree(skills_dir, backup_path, dirs_exist_ok=True)
    return backup_path

def sync_skills(dry_run: bool = True) -> dict:
    """Sync skills from source to targets. Returns summary dict."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_dir = get_skill_dirs(SOURCE_PROFILE)
    source_skills = list_skills(source_dir)

    print(f"=== Skill Sync {'(DRY RUN)' if dry_run else '(APPLY)'} ===")
    print(f"Source: {SOURCE_PROFILE} ({len(source_skills)} skills)")
    print(f"Targets: {', '.join(TARGET_PROFILES)}")
    print(f"Timestamp: {timestamp}")
    print()

    summary = {
        "timestamp": timestamp,
        "source_profile": SOURCE_PROFILE,
        "source_skill_count": len(source_skills),
        "targets": {},
    }

    for target in TARGET_PROFILES:
        target_dir = get_skill_dirs(target)
        target_skills = list_skills(target_dir)

        # Skills to copy = in source but not in target
        to_copy = source_skills - target_skills
        already_have = source_skills & target_skills
        target_only = target_skills - source_skills

        print(f"--- {target} ---")
        print(f"  Already have: {len(already_have)} skills")
        print(f"  Target-only (kept): {len(target_only)} skills")
        print(f"  Will copy: {len(to_copy)} skills")

        if to_copy:
            print(f"  Skills to copy: {', '.join(sorted(to_copy))}")
        else:
            print("  (no new skills to copy)")

        summary["targets"][target] = {
            "already_have": len(already_have),
            "target_only": len(target_only),
            "will_copy": len(to_copy),
            "skills_to_copy": sorted(to_copy),
            "skills_target_only": sorted(target_only),
        }

        if not dry_run and to_copy:
            # Backup target skills dir first
            backup_path = backup_skills_dir(target_dir, timestamp)
            print(f"  Backed up to: {backup_path}")

            # Copy each skill directory (preserving category structure)
            for skill_rel in to_copy:
                src = source_dir / skill_rel
                dst = target_dir / skill_rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, dst)
                print(f"  Copied: {skill_rel}")

        print()

    return summary

def main():
    parser = argparse.ArgumentParser(description="Sync skills from supermaster to other profiles (additive only)")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes (default: dry-run)")
    parser.add_argument("--target", action="append", help="Specific target profile(s) to sync (default: all 6)")
    args = parser.parse_args()

    global TARGET_PROFILES
    if args.target:
        TARGET_PROFILES = args.target

    summary = sync_skills(dry_run=not args.apply)

    if not args.apply:
        print("=== DRY RUN COMPLETE ===")
        print("Re-run with --apply to execute the sync.")
        print("Backup will be created at ~/.hermes/backups/<timestamp>/skills/<profile>/")
    else:
        print("=== SYNC APPLIED ===")

    return 0

if __name__ == "__main__":
    sys.exit(main())