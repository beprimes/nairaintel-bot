"""
main.py — AzaIndex Bot entry point
Run by GitHub Actions 3x daily at 08:00, 13:00, 19:00 WAT
"""

import os
import sys
import json
import datetime


def load_config():
    """Load config from environment variables (set as GitHub Secrets)"""
    return {
        # X / Twitter
        "X_API_KEY":              os.environ.get("X_API_KEY", ""),
        "X_API_SECRET":           os.environ.get("X_API_SECRET", ""),
        "X_ACCESS_TOKEN":         os.environ.get("X_ACCESS_TOKEN", ""),
        "X_ACCESS_TOKEN_SECRET":  os.environ.get("X_ACCESS_TOKEN_SECRET", ""),

        # ExchangeRate-API
        "EXCHANGERATE_API_KEY":   os.environ.get("EXCHANGERATE_API_KEY", ""),

        # Flags
        "DRY_RUN": os.environ.get("DRY_RUN", "false").lower() == "true",
    }


def send_github_alert(message):
    """
    Write alert to GitHub step summary.
    GitHub Actions reads $GITHUB_STEP_SUMMARY and emails on failure.
    """
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(f"⚠️ **AzaIndex Bot Alert**: {message}\n")
    print(f"[ALERT] {message}")


def main():
    print(f"\n{'='*60}")
    print(f"AzaIndex Bot — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    config = load_config()

    # Check critical secrets
    missing = []
    for key in ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]:
        if not config[key]:
            missing.append(key)
    if missing and not config["DRY_RUN"]:
        print(f"[ERROR] Missing secrets: {', '.join(missing)}")
        print("[INFO] Set these as GitHub Secrets. See README.md for instructions.")
        sys.exit(1)

    # ── Step 1: Fetch all data ─────────────────────────────────────────────
    print("[STEP 1] Fetching data...")
    from fetcher import fetch_all_data
    try:
        data, alerts = fetch_all_data(config)
    except Exception as e:
        print(f"[ERROR] Data fetch failed critically: {e}")
        send_github_alert(f"Critical data fetch failure: {e}")
        sys.exit(1)

    # Send any non-critical alerts
    for alert in alerts:
        send_github_alert(alert)

    print(f"\n[DATA SUMMARY]")
    print(f"  USD/NGN Parallel: ₦{data.get('parallel',0):,.0f}")
    print(f"  BTC: ${data.get('btc_usd',0):,}")
    print(f"  Brent: ${data.get('brent',0):.1f}/bbl")
    print(f"  Inflation: {data.get('inflation',0):.1f}%")
    print(f"  Aza Index: {data.get('aza',0)}/100")
    print(f"  Strength: {data.get('strength_label','')}")
    print()

    # ── Step 2: Generate images ────────────────────────────────────────────
    print("[STEP 2] Generating images...")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    from renderer import render_all
    try:
        images = render_all(data, output_dir)
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        send_github_alert(f"Image generation failure: {e}")
        sys.exit(1)

    print(f"[OK] Generated {len(images)} images")

    # ── Step 3: Build caption ──────────────────────────────────────────────
    print("[STEP 3] Building caption...")
    from poster import build_caption
    caption = build_caption(data)
    print(f"\n[CAPTION PREVIEW]\n{caption}\n")

    # ── Step 4: Post to X ─────────────────────────────────────────────────
    if config["DRY_RUN"]:
        print("[DRY RUN] Skipping X post. Images saved to ./output/")
        print("[DRY RUN] To post for real, remove DRY_RUN=true from env.")
        return

    print("[STEP 4] Posting to X...")
    from poster import post_to_x
    try:
        tweet_id = post_to_x(images, caption, config)
        print(f"[SUCCESS] Bot run complete. Tweet: https://x.com/i/web/status/{tweet_id}")
    except Exception as e:
        print(f"[ERROR] Posting failed: {e}")
        send_github_alert(f"X post failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
