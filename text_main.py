"""
text_main.py — NairaIntel text post entry point.
Run by GitHub Actions every 2 hours via text_post.yml.

Flow:
  1. Check if current WAT hour is a text post slot
  2. Load live data from cache (already fetched by main.py image runs)
  3. Build the appropriate post (Type A / B / C)
  4. Post to X
  5. Update cache (used facts, used templates)
"""

import datetime
import json
import os
import sys

# WAT = UTC+1. GitHub Actions runners are UTC.
# We compute WAT explicitly rather than relying on TZ env var,
# which Python's datetime.now() does not always pick up.
WAT = datetime.timezone(datetime.timedelta(hours=1))


def load_config():
    return {
        "X_API_KEY":             os.environ.get("X_API_KEY", ""),
        "X_API_SECRET":          os.environ.get("X_API_SECRET", ""),
        "X_ACCESS_TOKEN":        os.environ.get("X_ACCESS_TOKEN", ""),
        "X_ACCESS_TOKEN_SECRET": os.environ.get("X_ACCESS_TOKEN_SECRET", ""),
        "DRY_RUN": os.environ.get("DRY_RUN", "false").lower() == "true",
    }


def load_cache():
    cache_path = os.path.join(os.path.dirname(__file__), "cache.json")
    with open(cache_path, "r") as f:
        return json.load(f)


def save_cache(cache):
    cache_path = os.path.join(os.path.dirname(__file__), "cache.json")
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)


def build_live_data_from_cache(cache):
    """
    Reconstruct the live_data dict from cached values.
    This avoids re-fetching all APIs — the image bot already
    fetched everything and cached it. We just read the cache.
    """
    t2 = cache.get("tier2", {})
    t4 = cache.get("tier4", {})
    wt = cache.get("weekly_tracking", {})

    parallel      = cache.get("last_parallel", 1499)
    prev_parallel = cache.get("prev_parallel_month", parallel)
    petrol        = t2.get("petrol", 897)
    prev_petrol   = cache.get("prev_petrol_month", petrol)
    inflation     = t4.get("inflation", 33.2)
    prev_inflation = cache.get("prev_inflation_month", inflation)

    return {
        "parallel":       parallel,
        "cbn":            cache.get("last_cbn", 1346),
        "spread_pct":     round(((parallel - cache.get("last_cbn", 1346)) /
                                  cache.get("last_cbn", 1346)) * 100, 2)
                          if cache.get("last_cbn", 1346) > 0 else 0,
        "prev_parallel":  prev_parallel,
        "btc_usd":        cache.get("last_btc_usd", 68000),
        "eth_usd":        cache.get("last_eth_usd", 2100),
        "gold_usd":       cache.get("last_gold_usd", 2930),
        "brent":          cache.get("last_brent", 75),
        "inflation":      inflation,
        "prev_inflation": prev_inflation,
        "petrol":         petrol,
        "prev_petrol":    prev_petrol,
        "diesel":         t2.get("diesel", 1450),
        "lpg_kg":         t2.get("lpg_kg", 1200),
        "ngx":            t2.get("ngx_index", 104520),
        "ngx_chg":        t2.get("ngx_change", 0.6),
        "reserves":       t2.get("reserves", 34.2),
        "oil_production": cache.get("tier3", {}).get("oil_production", 1.42),
        "usd_wk_hi":      wt.get("usd_ngn_week_high", parallel),
        "usd_wk_lo":      wt.get("usd_ngn_week_low", parallel),
        "btc_wk_hi":      wt.get("btc_week_high", 0),
        "btc_wk_lo":      wt.get("btc_week_low", 0),
        "salary_usd":     round(500000 / parallel) if parallel else 333,
        "yr":             datetime.datetime.now(tz=WAT).year,
    }


def main():
    now_wat = datetime.datetime.now(tz=WAT)

    # FORCE_HOUR env var allows manual workflow_dispatch testing of specific slots
    force_hour = os.environ.get("FORCE_HOUR", "").strip()
    if force_hour and force_hour.isdigit():
        hour = int(force_hour)
        print(f"[INFO] FORCE_HOUR override: using hour {hour:02d}:00 WAT")
    else:
        hour = now_wat.hour

    print(f"\n{'='*55}")
    print(f"NairaIntel Text Bot — {now_wat.strftime('%Y-%m-%d %H:%M WAT')}")
    print(f"Current hour: {hour:02d}:00 WAT")
    print(f"{'='*55}\n")

    config = load_config()

    # Check required secrets
    missing = [k for k in ["X_API_KEY", "X_API_SECRET",
                            "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
               if not config[k]]
    if missing and not config["DRY_RUN"]:
        print(f"[ERROR] Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    # Check if this is a text post hour
    from post_schedule import is_text_post_hour, TEXT_POST_HOURS
    if not is_text_post_hour(hour):
        print(f"[INFO] Hour {hour:02d}:00 is not a text post slot.")
        print(f"[INFO] Text post slots: {TEXT_POST_HOURS}")
        print("[INFO] Nothing to do. Exiting cleanly.")
        sys.exit(0)

    print(f"[INFO] Hour {hour:02d}:00 IS a text post slot. Building post...")

    # Load cache and build live data
    cache     = load_cache()
    live_data = build_live_data_from_cache(cache)

    print(f"[INFO] Live data: parallel=₦{live_data['parallel']:,} "
          f"inflation={live_data['inflation']}% "
          f"petrol=₦{live_data['petrol']:,}/L")

    # Build the post
    from text_poster import build_text_post
    post_text, post_type = build_text_post(hour, live_data, cache)

    if not post_text:
        print(f"[WARN] No post generated for hour {hour}. Exiting.")
        save_cache(cache)
        sys.exit(0)

    print(f"\n[POST PREVIEW — Type {post_type}]")
    print(f"{'─'*50}")
    print(post_text)
    print(f"{'─'*50}")
    print(f"[INFO] Character count: {len(post_text)}/280")

    if len(post_text) > 280:
        print(f"[ERROR] Post exceeds 280 chars ({len(post_text)}). Aborting.")
        save_cache(cache)
        sys.exit(1)

    # Update monthly baseline values for direction-awareness
    # Only update on 1st of each month to track monthly changes
    if now_wat.day == 1 and now_wat.hour == 6:
        cache["prev_parallel_month"] = live_data["parallel"]
        cache["prev_petrol_month"]   = live_data["petrol"]
        cache["prev_inflation_month"] = live_data["inflation"]
        print("[INFO] Updated monthly baseline values in cache.")

    # Save cache (updated used-fact indices)
    save_cache(cache)

    if config["DRY_RUN"]:
        print("\n[DRY RUN] Post NOT sent to X. Exiting.")
        return

    # Post to X
    from text_poster import post_text_tweet
    try:
        tweet_id = post_text_tweet(post_text, config)
        print(f"\n[SUCCESS] Type {post_type} post live: "
              f"https://x.com/i/web/status/{tweet_id}")
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
