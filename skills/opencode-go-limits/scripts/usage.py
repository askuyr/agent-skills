#!/usr/bin/env python3
"""Estimate OpenCode Go allowance usage from the local OpenCode database.

Go limits are monthly dollar allowances per model. Local messages store tokens
(not allowance), so cost is estimated from the published Go price table.

Usage: python usage.py [--plan go|go-plus|go-teams] [--provider opencode-go]
                       [--json] [--model ID] [--db PATH] [--warn]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
LIMITS_PATH = os.path.join(SKILL, "references", "limits.json")
DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".local", "share", "opencode", "opencode.db")


def load_limits(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_peak(ts: dt.datetime) -> bool:
    """DeepSeek peak: 01:00-04:00 and 06:00-10:00 UTC, Mon-Fri."""
    if ts.weekday() >= 5:
        return False
    h = ts.hour
    return (1 <= h < 4) or (6 <= h < 10)


def message_cost(tokens: dict, price: dict, ts: dt.datetime) -> float:
    p = price
    if price.get("peak") and is_peak(ts):
        p = price["peak"]
    inp = tokens.get("input") or 0
    out = (tokens.get("output") or 0) + (tokens.get("reasoning") or 0)
    cache = tokens.get("cache") or {}
    cr = cache.get("read") or 0
    cw = cache.get("write") or 0
    cost = inp / 1e6 * (p.get("input") or 0)
    cost += out / 1e6 * (p.get("output") or 0)
    cost += cr / 1e6 * (p.get("cache_read") or 0)
    cost += cw / 1e6 * (p.get("cache_write") or 0)
    return cost


def fmt_usd(v: float) -> str:
    if v >= 10:
        return f"${v:.0f}"
    if v >= 1:
        return f"${v:.2f}"
    return f"${v:.3f}"


def main() -> int:
    ap = argparse.ArgumentParser(description="OpenCode Go allowance estimate")
    ap.add_argument("--plan", default=None, help="go | go-plus | go-teams (default: go)")
    ap.add_argument("--provider", default="opencode-go")
    ap.add_argument("--model", default=None)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--warn", action="store_true", help="exit 2 when any window is >=80%")
    args = ap.parse_args()

    data = load_limits(LIMITS_PATH)
    plan = args.plan
    if plan is None:
        cfg_path = os.path.join(SKILL, "config.json")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, encoding="utf-8") as f:
                    plan = json.load(f).get("plan")
            except (OSError, json.JSONDecodeError):
                plan = None
    plan = plan or "go"
    if plan not in data["plans"]:
        print(f"unknown plan '{plan}'; available: {', '.join(data['plans'])}", file=sys.stderr)
        return 1

    limits = data["plans"][plan]["limits_usd"]
    prices = data["pricing_per_million"]
    shares = data["windows"]

    if not os.path.isfile(args.db):
        print(f"database not found: {args.db}", file=sys.stderr)
        return 1

    now = dt.datetime.now(dt.timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start = now - dt.timedelta(days=shares["week_days"])
    five_start = now - dt.timedelta(hours=shares["five_hour_hours"])
    earliest = min(month_start, week_start, five_start)

    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    cur = con.cursor()
    rows = cur.execute(
        "SELECT time_created, data FROM session_message "
        "WHERE type = 'assistant' AND data LIKE ? AND time_created >= ?",
        (f'%"{args.provider}"%', int(earliest.timestamp() * 1000)),
    ).fetchall()

    usage: dict[str, dict[str, float]] = {}
    unpriced: set[str] = set()
    total_points = 0
    for ms, raw in rows:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        model = (payload.get("model") or {})
        if model.get("providerID") != args.provider:
            continue
        mid = model.get("id") or "unknown"
        if args.model and mid != args.model:
            continue
        tokens = payload.get("tokens") or {}
        ts = dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)
        price = prices.get(mid)
        if price is None:
            unpriced.add(mid)
            continue
        cost = message_cost(tokens, price, ts)
        rec = usage.setdefault(mid, {"five": 0.0, "week": 0.0, "month": 0.0, "requests": 0})
        rec["requests"] += 1
        if ts >= five_start:
            rec["five"] += cost
        if ts >= week_start:
            rec["week"] += cost
        if ts >= month_start:
            rec["month"] += cost
        total_points += 1

    result = {
        "plan": plan,
        "plan_price_usd": data["plans"][plan]["price_usd"],
        "generated_at": now.isoformat(timespec="seconds"),
        "provider": args.provider,
        "messages_counted": total_points,
        "models": [],
        "unpriced_models": sorted(unpriced),
    }
    limit = limits
    for mid in sorted(usage, key=lambda m: usage[m]["month"], reverse=True):
        monthly = limit.get(mid)
        rec = usage[mid]
        entry = {
            "model": mid,
            "requests": rec["requests"],
            "five_hour_usd": round(rec["five"], 4),
            "week_usd": round(rec["week"], 4),
            "month_usd": round(rec["month"], 4),
            "month_limit_usd": monthly,
            "five_hour_cap_usd": None if monthly is None else round(monthly * shares["five_hour_share"], 2),
            "week_cap_usd": None if monthly is None else round(monthly * shares["week_share"], 2),
            "month_used_pct": None if not monthly else round(rec["month"] / monthly * 100, 1),
        }
        avg = rec["month"] / rec["requests"] if rec["requests"] else 0
        entry["avg_request_usd"] = round(avg, 4)
        entry["requests_left_month"] = (
            None if not monthly or avg <= 0 else int((monthly - rec["month"]) / avg)
        )
        result["models"].append(entry)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"OpenCode Go - plan {plan} (${result['plan_price_usd']}/mo) | {now:%Y-%m-%d %H:%M} UTC")
        print(f"messages: {total_points} | provider: {args.provider}")
        if not result["models"]:
            print("\nNo Go usage found in the local database for this period.")
            print("Check that the model provider is 'opencode-go' and that the DB is current.")
        else:
            print()
            print(f"{'model':28} {'5h':>14} {'week':>14} {'month':>14} {'mo %':>6}")
            for e in result["models"]:
                def cell(v, cap):
                    return f"{fmt_usd(v)}/{fmt_usd(cap) if cap else 'unl'}"
                pct = "" if e["month_used_pct"] is None else f"{e['month_used_pct']:.1f}%"
                print(f"{e['model'][:28]:28} {cell(e['five_hour_usd'], e['five_hour_cap_usd']):>14} "
                      f"{cell(e['week_usd'], e['week_cap_usd']):>14} "
                      f"{cell(e['month_usd'], e['month_limit_usd']):>14} {pct:>6}")
            print("\n5h = 20% of monthly limit, week = 50%, month = 100% (per model).")
            print("Estimate from tokens; authoritative value is opencode.allowance in the console.")
        if result["unpriced_models"]:
            print(f"\nNo price entry (skipped): {', '.join(result['unpriced_models'])}")

    if args.warn:
        for e in result["models"]:
            if e["month_limit_usd"] and (
                e["month_usd"] >= e["month_limit_usd"] * 0.8
                or (e["five_hour_cap_usd"] and e["five_hour_usd"] >= e["five_hour_cap_usd"] * 0.8)
                or (e["week_cap_usd"] and e["week_usd"] >= e["week_cap_usd"] * 0.8)
            ):
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
