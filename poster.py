"""
poster.py — Posts 4 images to X (Twitter) as a single tweet
Uses Tweepy with API v2
"""

import tweepy
import os


def build_caption(data):
    """
    Build tweet caption — max 280 characters.
    No hashtags. One strong search keyword baked in naturally.
    Rotates keyword focus across the 3 daily posts based on hour.
    """
    aza = data["aza"]
    strength = data["strength_label"]
    parallel = data["parallel"]
    btc_usd = data.get("btc_usd", 0)
    brent = data.get("brent", 0)
    ngx = data.get("ngx", 0)
    ngx_chg = data.get("ngx_chg", 0)
    petrol = data.get("petrol", 0)
    inflation = data.get("inflation", 0)
    date_str = data.get("post_time_short", "")
    time_str = data.get("post_hour", "")
    hour = int(time_str.split(":")[0]) if time_str else 8

    # Aza status emoji
    if aza >= 75:   aza_emoji = "🟢"
    elif aza >= 50: aza_emoji = "🟡"
    elif aza >= 25: aza_emoji = "🟠"
    else:           aza_emoji = "🔴"

    ngx_arrow = "▲" if ngx_chg >= 0 else "▼"

    # Rotate focus keyword by post time — morning=FX, afternoon=fuel, evening=markets
    if hour < 11:
        # Morning — Dollar to Naira focus
        caption = (
            f"Dollar to Naira today — {date_str}\n"
            f"Parallel: ₦{parallel:,.0f} • Inflation: {inflation:.1f}%\n"
            f"BTC: ₦{btc_usd*parallel/1e6:.2f}M • Brent: ${brent:.1f}/bbl\n"
            f"\n"
            f"{aza_emoji} Aza Index: {aza}/100 — {strength}\n"
            f"NairaIntel"
        )
    elif hour < 16:
        # Afternoon — Petrol price focus
        caption = (
            f"Petrol price today: ₦{petrol}/L | {date_str}\n"
            f"USD/NGN: ₦{parallel:,.0f} • NGX: {ngx:,} {ngx_arrow}{abs(ngx_chg):.1f}%\n"
            f"BTC: ₦{btc_usd*parallel/1e6:.2f}M • Brent: ${brent:.1f}/bbl\n"
            f"\n"
            f"{aza_emoji} Aza Index: {aza}/100 — {strength}\n"
            f"NairaIntel"
        )
    else:
        # Evening — NigeriaEconomy focus
        caption = (
            f"NigeriaEconomy update — {date_str}\n"
            f"Parallel rate: ₦{parallel:,.0f} • Inflation: {inflation:.1f}%\n"
            f"NGX: {ngx:,} {ngx_arrow}{abs(ngx_chg):.1f}% • Brent: ${brent:.1f}/bbl\n"
            f"\n"
            f"{aza_emoji} Aza Index: {aza}/100 — {strength}\n"
            f"NairaIntel"
        )

    # Safety check — trim if somehow over 280
    if len(caption) > 280:
        caption = caption[:277] + "..."

    return caption


def post_to_x(images, caption, config):
    """
    Post 4 images as a single tweet to X.
    config must have: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    """
    try:
        # v1.1 client for media upload
        auth = tweepy.OAuth1UserHandler(
            config["X_API_KEY"],
            config["X_API_SECRET"],
            config["X_ACCESS_TOKEN"],
            config["X_ACCESS_TOKEN_SECRET"]
        )
        api_v1 = tweepy.API(auth)

        # Upload all 4 images
        media_ids = []
        for img_path in images:
            print(f"[INFO] Uploading {os.path.basename(img_path)}...")
            media = api_v1.media_upload(filename=img_path)
            media_ids.append(str(media.media_id))
            print(f"[INFO] Uploaded media_id: {media.media_id}")

        # v2 client for posting tweet
        client_v2 = tweepy.Client(
            consumer_key=config["X_API_KEY"],
            consumer_secret=config["X_API_SECRET"],
            access_token=config["X_ACCESS_TOKEN"],
            access_token_secret=config["X_ACCESS_TOKEN_SECRET"]
        )

        response = client_v2.create_tweet(
            text=caption,
            media_ids=media_ids
        )
        tweet_id = response.data["id"]
        print(f"[OK] Tweet posted: https://x.com/i/web/status/{tweet_id}")
        return tweet_id

    except Exception as e:
        print(f"[ERROR] Failed to post tweet: {e}")
        raise
