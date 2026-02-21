# AzaIndex Bot 🇳🇬

Automated Nigerian market data bot. Posts 4 images to X (Twitter) 3× daily showing live FX, crypto, oil, NGX, macroeconomic data, and the Aza Index — a composite economic health score.

**Posting times:** 08:00 / 13:00 / 19:00 WAT

---

## Image Overview

| Image | Title | Accent |
|-------|-------|--------|
| 1 | Nigeria Live Markets | Green |
| 2 | Nigeria Economy | Orange |
| 3 | Africa & Global Markets | Purple |
| 4 | Aza Index | Blue |

---

## Quick Setup (5 steps)

### 1. Fork this repository

Fork to your own GitHub account. Make it **public** — GitHub Actions is free on public repos.

### 2. Get your API keys

#### X (Twitter) Developer API
1. Go to [developer.x.com](https://developer.x.com)
2. Create a new App
3. Under **User authentication settings**, enable:
   - Read and Write permissions
   - OAuth 1.0a
4. Generate: API Key, API Key Secret, Access Token, Access Token Secret
5. You need the **Free tier** at minimum — it allows posting tweets

#### ExchangeRate-API (free tier)
1. Go to [exchangerate-api.com](https://www.exchangerate-api.com)
2. Sign up for free — no credit card needed
3. Copy your API key from the dashboard
4. Free tier: 1,500 requests/month — the bot uses ~90/month (3 runs/day × 30 days)

### 3. Add GitHub Secrets

In your forked repo, go to **Settings → Secrets and variables → Actions → New repository secret**

Add these 5 secrets:

| Secret Name | Where to get it |
|------------|----------------|
| `X_API_KEY` | X Developer Portal → Your App → Keys |
| `X_API_SECRET` | X Developer Portal → Your App → Keys |
| `X_ACCESS_TOKEN` | X Developer Portal → Your App → Keys |
| `X_ACCESS_TOKEN_SECRET` | X Developer Portal → Your App → Keys |
| `EXCHANGERATE_API_KEY` | ExchangeRate-API dashboard |

### 4. Set your X handle

In `renderer.py`, search for `@AzaIndex` and replace with your actual X handle.  
It appears in the top-right of every image and in the footer.

```python
# In renderer.py — search for this and replace:
"@AzaIndex"
# Replace with e.g.:
"@YourHandle"
```

Also update the caption in `poster.py`:
```python
# In poster.py → build_caption():
f"#AzaIndex #NairaRate ..."
# Update hashtags to match your brand
```

### 5. Enable GitHub Actions

Go to **Actions** tab in your forked repo and click **"I understand my workflows, go ahead and enable them"**

That's it. The bot will automatically run at 07:00, 12:00, and 18:00 UTC (08:00, 13:00, 19:00 WAT).

---

## Manual Test Run

To test without posting to X:

1. Go to **Actions → AzaIndex Bot → Run workflow**
2. Check **"Dry run"** box
3. Click **Run workflow**
4. After it completes, download the images from the **Artifacts** section

To test posting for real, run without the dry run checkbox.

---

## Data Sources

### Zero-scraping (stable free APIs)
| Data | Source | Update frequency |
|------|--------|-----------------|
| USD/NGN CBN | ExchangeRate-API | Live |
| EUR, GBP, CNY, KES, GHS, ZAR, EGP, XOF | ExchangeRate-API | Live |
| BTC, ETH, BNB, Gold prices | CoinGecko free | Live |
| Brent crude, Bonny Light | Stooq.com | Daily |
| S&P500, FTSE, DAX, Nikkei | Stooq.com | Daily |
| DXY Dollar Index | Stooq.com | Daily |
| JSE (South Africa), EGX (Egypt) | Stooq.com | Daily |
| Silver, Cocoa | Stooq.com | Daily |
| USDT P2P rate | Binance P2P API | Live |
| USDT P2P rate | Bybit P2P API | Live |
| Remittance rate | Wise public API | Live |

### Daily scrape (08:00 run only)
| Data | Source | Fallback |
|------|--------|---------|
| Petrol/Diesel pump prices | Pricecheck.ng | Cached value + date |
| NGX top 3 movers | NGX Group website | Shows index only |
| FX Reserves | CBN website | Cached value + date |

### Monthly update (manual via GitHub Secrets or auto-scrape 1st of month)
| Data | Source | How to update |
|------|--------|--------------|
| Inflation rate | NBS | Edit `cache.json` → `tier4.inflation` |
| External debt | DMO | Edit `cache.json` → `tier4.external_debt` |
| OPEC quota | OPEC | Edit `cache.json` → `tier4.opec_quota` |
| Unemployment | NBS | Edit `cache.json` → `tier4.unemployment` |
| Poverty rate | World Bank | Edit `cache.json` → `tier4.poverty_rate` |

---

## Updating Monthly Data (Manual)

When NBS publishes new inflation figures (usually mid-month):

1. Open `cache.json` in your GitHub repo
2. Click the pencil (edit) icon
3. Update the relevant values under `tier4`:

```json
"tier4": {
  "inflation": 33.2,           ← update this
  "inflation_date": "Jan 2026", ← update this
  ...
}
```

4. Commit directly to main branch
5. Next bot run will use the new values automatically

---

## The Aza Index

A composite score (0–100) measuring Nigerian economic health from the average citizen's perspective.

### Components

| Component | Weight | Measures |
|-----------|--------|---------|
| FX Stability | 30% | Parallel market premium over CBN rate |
| Inflation Pressure | 25% | NBS headline inflation rate |
| Fuel Accessibility | 20% | Litres of petrol purchaseable per $1 |
| Crypto Confidence | 15% | USDT P2P premium over CBN rate |
| Stock Momentum | 10% | NGX daily trend |

### Score Interpretation

| Range | Status | Meaning |
|-------|--------|---------|
| 75–100 | STRONG | Economy breathing well |
| 50–74 | STRAINED | Pressure building |
| 25–49 | STRESSED | Everyday Nigerians feeling it |
| 0–24 | CRISIS | Emergency conditions |

---

## Scrape Failure Handling

Every data point has 3 fallback layers:

```
Layer 1: Live API / scrape
    ↓ fails ↓
Layer 2: Cache (last known value + "as of" date shown on image)
    ↓ fails ↓  
Layer 3: Replacement data from stable API, or "unavailable" note
```

After 3 consecutive failures, a GitHub Actions alert email is sent to your account.

The bot never crashes — images always post regardless of individual data failures.

---

## Project Structure

```
azaindex-bot/
├── main.py            # Entry point — orchestrates fetch → render → post
├── fetcher.py         # All data fetching (APIs, scrapes, cache logic)
├── renderer.py        # Pillow image generation for all 4 images
├── poster.py          # X/Twitter API posting
├── cache.json         # Persistent data store (committed back each run)
├── requirements.txt   # Python dependencies
├── .gitignore
└── .github/
    └── workflows/
        └── post.yml   # GitHub Actions schedule
```

---

## Customisation

### Change posting times

Edit `.github/workflows/post.yml`:
```yaml
schedule:
  - cron: '0 7 * * *'   # 08:00 WAT (07:00 UTC)
  - cron: '0 12 * * *'  # 13:00 WAT (12:00 UTC)
  - cron: '0 18 * * *'  # 19:00 WAT (18:00 UTC)
```

### Change the salary baseline for erosion tracker

In `fetcher.py`, find:
```python
data["salary_ngn"] = 500000  # ₦500k/month example salary
data["salary_usd_then"] = data["salary_ngn"] / 910  # 1 year ago rate
```

### Change the Aza Index weights

In `fetcher.py` → `calculate_aza_index()`:
```python
components["fx"]       = {"score": fx_score,    "weight": 0.30, ...}
components["inflation"]= {"score": inf_score,   "weight": 0.25, ...}
components["fuel"]     = {"score": fuel_score,  "weight": 0.20, ...}
components["crypto"]   = {"score": crypto_score,"weight": 0.15, ...}
components["stock"]    = {"score": stock_score, "weight": 0.10, ...}
```
Weights must add up to 1.0.

### Change colours

In `renderer.py`, edit the palette at the top of the file:
```python
GREEN  = "#00D48A"
RED    = "#FF3D5A"
YELLOW = "#FFB300"
...
```

---

## Troubleshooting

**Bot runs but tweet doesn't appear**
- Check X Developer Portal: your App needs Read + Write OAuth permissions
- Regenerate Access Token after enabling Write permission
- Verify all 4 X secrets are set correctly

**"ExchangeRate-API" errors**
- Free tier limit is 1,500 requests/month. Bot uses ~90/month so this should not trigger
- Verify `EXCHANGERATE_API_KEY` secret is set

**Images look wrong**
- Run manually with `DRY_RUN=true` and download artifacts to inspect
- Check GitHub Actions logs for any Python errors

**Cache not updating**
- Ensure the repo is public OR GitHub Actions has write permissions
- Check the "Commit updated cache" step in Actions logs

---

## Zero-cost Architecture

Everything runs for free:
- **GitHub Actions**: free on public repos (2,000 min/month free, bot uses ~90 min/month)
- **ExchangeRate-API**: free tier (1,500 req/month)
- **CoinGecko**: free tier (30 calls/min)
- **Stooq.com**: free, no API key needed
- **Binance P2P**: public endpoint, no auth
- **Bybit P2P**: public endpoint, no auth
- **Wise**: public rate endpoint

Total cost: **$0/month**

---

*AzaIndex Bot — Built for the people who feel every kobo of devaluation.*
