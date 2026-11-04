#!/usr/bin/env python3
"""
Cost tracking script for Hermes Agent.
Reads state.db (read-only) and reports usage per profile for YESTERDAY (full day).
No LLM calls — pure SQLite aggregation.
Run via system crontab (not Hermes cronjob) at 06:00.
Appends a single summary line to ~/.hermes/logs/cost-report.log
"""
import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERMES_HOME = Path("/home/rafi_ansf/.hermes")
PROFILES = ["backend", "frontend", "qa", "reviewer", "supermaster", "researcher", "writer"]
LOG_FILE = HERMES_HOME / "logs" / "cost-report.log"

THRESHOLD_API = 830
THRESHOLD_TOKENS = 8_000_000

def get_state_db(profile: str) -> Path:
    return HERMES_HOME / "profiles" / profile / "state.db"

def query_profile(db_path: Path, day_start_ts: float, day_end_ts: float) -> dict:
    """Aggregate usage from state.db for a single profile within [day_start_ts, day_end_ts)."""
    if not db_path.exists():
        return {"error": f"DB not found: {db_path}"}

    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Sessions in window
    cursor.execute("""
        SELECT profile_name, COUNT(*) as session_count,
               SUM(message_count) as total_messages,
               SUM(tool_call_count) as total_tool_calls,
               SUM(api_call_count) as total_api_calls,
               SUM(input_tokens) as total_input_tokens,
               SUM(output_tokens) as total_output_tokens,
               SUM(cache_read_tokens) as total_cache_read,
               SUM(cache_write_tokens) as total_cache_write,
               SUM(reasoning_tokens) as total_reasoning_tokens,
               SUM(estimated_cost_usd) as total_est_cost,
               SUM(actual_cost_usd) as total_actual_cost
        FROM sessions
        WHERE started_at >= ? AND started_at < ? AND profile_name IS NOT NULL
        GROUP BY profile_name
    """, (day_start_ts, day_end_ts))

    session_rows = cursor.fetchall()

    # Model usage breakdown
    cursor.execute("""
        SELECT billing_provider, model, task, SUM(api_call_count) as calls,
               SUM(input_tokens) as in_tokens, SUM(output_tokens) as out_tokens,
               SUM(estimated_cost_usd) as est_cost
        FROM session_model_usage
        WHERE first_seen >= ? AND first_seen < ?
        GROUP BY billing_provider, model, task
        ORDER BY est_cost DESC
    """, (day_start_ts, day_end_ts))

    usage_rows = cursor.fetchall()
    conn.close()

    return {
        "sessions": [dict(r) for r in session_rows],
        "model_usage": [dict(r) for r in usage_rows],
    }

def format_summary_line(date_str: str, total_api: int, total_tokens: int, status: str, per_profile: dict) -> str:
    """Return a single JSON line for log file."""
    record = {
        "date": date_str,
        "total_api_calls": total_api,
        "total_tokens": total_tokens,
        "status": status,
        "profiles": per_profile,
    }
    return json.dumps(record, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Hermes cost tracking (read-only) for yesterday")
    parser.add_argument("--test", action="store_true", help="Run for yesterday and print to stdout (no log append)")
    args = parser.parse_args()

    # Determine yesterday's date range in UTC (state.db timestamps are UNIX seconds, likely UTC)
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    day_start = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    day_end = day_start + timedelta(days=1)
    day_start_ts = day_start.timestamp()
    day_end_ts = day_end.timestamp()
    date_str = day_start.strftime("%Y-%m-%d")

    total_api = 0
    total_tokens = 0
    per_profile = {}
    any_warn = False

    for profile in PROFILES:
        db_path = get_state_db(profile)
        result = query_profile(db_path, day_start_ts, day_end_ts)

        if "error" in result:
            per_profile[profile] = {"error": result["error"]}
            continue

        sess = result["sessions"]
        usage = result["model_usage"]

        if not sess:
            per_profile[profile] = {"sessions": 0, "api_calls": 0, "tokens": 0}
            continue

        row = sess[0]
        p_api = row["total_api_calls"] or 0
        p_in = row["total_input_tokens"] or 0
        p_out = row["total_output_tokens"] or 0
        p_tokens = p_in + p_out

        total_api += p_api
        total_tokens += p_tokens

        profile_warn = False
        if p_api >= THRESHOLD_API or p_tokens >= THRESHOLD_TOKENS:
            profile_warn = True
            any_warn = True

        per_profile[profile] = {
            "sessions": row["session_count"],
            "api_calls": p_api,
            "tokens": p_tokens,
            "warn": profile_warn,
        }

    status = "WARN" if any_warn else "OK"

    # Build summary line
    line = format_summary_line(date_str, total_api, total_tokens, status, per_profile)

    if args.test:
        print(line)
    else:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

if __name__ == "__main__":
    main()