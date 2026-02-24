"""
text_poster.py — NairaIntel text-only tweet engine.

Handles 3 content types:
  Type A — Historical facts with live data anchors (facts_pool.py)
  Type B — Live data templates, direction-aware (rising vs falling)
  Type C — Weekly scraped data (bank rates, charges, fintech news)

Called by text_main.py which is triggered by text_post.yml workflow.
"""

import datetime
import json
import os
import re
import requests
import tweepy

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.json")


# ─── Cache helpers ─────────────────────────────────────────────────────────────

def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# ─── Type B: Live data templates ───────────────────────────────────────────────

TYPE_B_TEMPLATES = [

    # ── INFLATION ──────────────────────────────────────────────────────────────

    {
        "id": "inflation_up",
        "condition": lambda d: (d.get("inflation", 0) or 0) > (d.get("prev_inflation", 0) or 0),
        "text": lambda d: (
            f"Inflation climbed to {d['inflation']}% this month.\n\n"
            f"₦100,000 in savings lost ₦{_inflation_loss(d['inflation']):,.0f} in real value.\n\n"
            f"Every month above 30% inflation is a pay cut you didn't agree to.\n\n"
            f"📈 NairaIntel"
        )
    },
    {
        "id": "inflation_down",
        "condition": lambda d: (d.get("inflation", 0) or 0) < (d.get("prev_inflation", 0) or 33),
        "text": lambda d: (
            f"Inflation eased to {d['inflation']}% — down from {d.get('prev_inflation', '?')}%.\n\n"
            f"₦100,000 preserved ₦{_inflation_gain(d['inflation'], d.get('prev_inflation', d['inflation'])):,.0f} more than last month.\n\n"
            f"Progress — but still {round(d['inflation']/9, 1)}x above the CBN's 9% target.\n\n"
            f"📉 NairaIntel"
        )
    },

    # ── PARALLEL RATE ─────────────────────────────────────────────────────────

    {
        "id": "rate_up",
        "condition": lambda d: (d.get("parallel", 0) or 0) > (d.get("prev_parallel", 0) or 0),
        "text": lambda d: (
            f"Dollar climbed to ₦{d['parallel']:,.0f} today — up ₦{_rate_change(d):,.0f} from last month.\n\n"
            f"A ₦500k salary is now worth ${round(500000/d['parallel'])}/month.\n\n"
            f"Every naira lost means less dollar. Same work. Less purchasing power.\n\n"
            f"📈 NairaIntel"
        )
    },
    {
        "id": "rate_down",
        "condition": lambda d: (d.get("parallel", 0) or 0) < (d.get("prev_parallel", 9999) or 9999),
        "text": lambda d: (
            f"Naira strengthened to ₦{d['parallel']:,.0f}/$ today — down from ₦{d.get('prev_parallel', d['parallel']):,.0f}.\n\n"
            f"A ₦500k salary recovered ${_salary_recovery(d)}/month in dollar value.\n\n"
            f"Small wins matter. Watch the trend, not just the day.\n\n"
            f"📉 NairaIntel"
        )
    },

    # ── PETROL PRICE ──────────────────────────────────────────────────────────

    {
        "id": "petrol_up",
        "condition": lambda d: (d.get("petrol", 0) or 0) > (d.get("prev_petrol", 0) or 0),
        "text": lambda d: (
            f"Petrol rose to ₦{d['petrol']:,}/L.\n\n"
            f"Filling a 50L tank now costs ₦{50*d['petrol']:,}.\n\n"
            f"At ₦5,000/day wages, that is {round((50*d['petrol'])/5000, 1)} days work just to fill up.\n\n"
            f"⛽ NairaIntel"
        )
    },
    {
        "id": "petrol_down",
        "condition": lambda d: (d.get("petrol", 0) or 0) < (d.get("prev_petrol", 9999) or 9999),
        "text": lambda d: (
            f"Petrol dropped to ₦{d['petrol']:,}/L — down from ₦{d.get('prev_petrol', d['petrol']):,}/L.\n\n"
            f"Filling a 50L tank now saves ₦{_petrol_savings(d):,} vs last reading.\n\n"
            f"Every kobo matters at the pump.\n\n"
            f"⛽ NairaIntel"
        )
    },

    # ── PURCHASING POWER ──────────────────────────────────────────────────────

    {
        "id": "purchasing_power_check",
        "condition": lambda d: True,
        "text": lambda d: (
            f"What ₦10,000 buys today:\n\n"
            f"⛽ Petrol: {round(10000/d['petrol'], 1)}L\n"
            f"🍚 Rice (1kg): ~4kg\n"
            f"📱 Data (1GB): ~10-16 units\n"
            f"🍜 Indomie: ~25 packs\n\n"
            f"In 2020 ₦10,000 bought nearly double each.\n\n"
            f"Inflation: {d['inflation']}% | $1 = ₦{d['parallel']:,.0f}\n\n"
            f"💸 NairaIntel"
        )
    },

    # ── FUEL ACCESSIBILITY ────────────────────────────────────────────────────

    {
        "id": "fuel_access",
        "condition": lambda d: True,
        "text": lambda d: (
            f"$1 buys {round(d['parallel']/d['petrol'], 2):.2f} litres of petrol in Nigeria today.\n\n"
            f"Compare:\n"
            f"🇺🇸 USA: ~3.2L per $1\n"
            f"🇬🇭 Ghana: ~2.1L per $1\n"
            f"🇳🇬 Nigeria: {round(d['parallel']/d['petrol'], 2):.2f}L per $1\n\n"
            f"Lower means fuel is relatively more expensive for the average worker.\n\n"
            f"⛽ NairaIntel"
        )
    },

    # ── SPREAD / PARALLEL VS CBN ──────────────────────────────────────────────

    {
        "id": "spread_wide",
        "condition": lambda d: (d.get("spread_pct", 0) or 0) > 10,
        "text": lambda d: (
            f"The gap between CBN rate (₦{d.get('cbn',0):,.0f}) and parallel rate (₦{d['parallel']:,.0f}) is now {d.get('spread_pct',0):.1f}%.\n\n"
            f"A {d.get('spread_pct',0):.0f}% spread means:\n"
            f"— Importers pay premium for dollars\n"
            f"— Cost passes to consumers\n"
            f"— Inflation stays high\n\n"
            f"Wide spread = expensive everything.\n\n"
            f"📊 NairaIntel"
        )
    },
    {
        "id": "spread_narrow",
        "condition": lambda d: 0 < (d.get("spread_pct", 0) or 0) <= 10,
        "text": lambda d: (
            f"CBN rate: ₦{d.get('cbn',0):,.0f}\nParallel: ₦{d['parallel']:,.0f}\nSpread: {d.get('spread_pct',0):.1f}%\n\n"
            f"A narrowing spread signals improving FX stability.\n\n"
            f"When CBN and parallel converge, importers pay less premium — prices should follow.\n\n"
            f"📊 NairaIntel"
        )
    },

    # ── SALARY EROSION ────────────────────────────────────────────────────────

    {
        "id": "salary_erosion",
        "condition": lambda d: True,
        "text": lambda d: (
            f"₦500,000/month salary in USD:\n\n"
            f"Jan 2020: ${round(500000/360):,}\n"
            f"Jan 2023: ${round(500000/460):,}\n"
            f"Today: ${round(500000/d['parallel']):,}\n\n"
            f"Same naira. Less dollar. Less global purchasing power.\n\n"
            f"$1 = ₦{d['parallel']:,.0f} today.\n\n"
            f"💰 NairaIntel"
        )
    },

    # ── FX RESERVES ───────────────────────────────────────────────────────────

    {
        "id": "reserves_check",
        "condition": lambda d: d.get("reserves") is not None,
        "text": lambda d: (
            f"Nigeria's FX reserves: ${d.get('reserves', 34.2):.1f}B\n\n"
            f"At current import levels (~$50B/yr), that covers ~{round(d.get('reserves',34.2)/50*12):.0f} months of imports.\n\n"
            f"The IMF minimum recommendation is 3 months.\n\n"
            f"Healthy — but the naira still trades at ₦{d['parallel']:,.0f}/$1.\n\n"
            f"Reserves alone don't fix confidence.\n\n"
            f"🏦 NairaIntel"
        )
    },

    # ── BTC VS NAIRA ──────────────────────────────────────────────────────────

    {
        "id": "btc_naira",
        "condition": lambda d: d.get("btc_usd") is not None,
        "text": lambda d: (
            f"1 BTC = ₦{round(d['btc_usd'] * d['parallel'] / 1e6, 2):.2f}M today.\n\n"
            f"In January 2020:\n"
            f"1 BTC = $7,200 × ₦360 = ₦2.59M\n\n"
            f"Today:\n"
            f"1 BTC = ${d['btc_usd']:,} × ₦{d['parallel']:,.0f} = ₦{round(d['btc_usd']*d['parallel']/1e6,2):.2f}M\n\n"
            f"BTC absorbed both dollar gains AND naira devaluation.\n\n"
            f"₿ NairaIntel"
        )
    },

    # ── GOLD VS NAIRA ─────────────────────────────────────────────────────────

    {
        "id": "gold_naira",
        "condition": lambda d: d.get("gold_usd") is not None,
        "text": lambda d: (
            f"Gold today: ${d.get('gold_usd', 2930):,.0f}/oz\n\n"
            f"In naira: ₦{round(d.get('gold_usd',2930) * d['parallel']):,}/oz\n\n"
            f"In 2015, 1oz gold cost ₦{round(1200 * 197):,} (gold ~$1,200, ₦197/$1)\n\n"
            f"Today: ₦{round(d.get('gold_usd',2930) * d['parallel']):,}\n\n"
            f"Gold in naira has outperformed every Nigerian savings account.\n\n"
            f"🥇 NairaIntel"
        )
    },

    # ── WEEK RECAP ────────────────────────────────────────────────────────────

    {
        "id": "week_recap",
        "condition": lambda d: d.get("usd_wk_hi") and d.get("usd_wk_lo"),
        "text": lambda d: (
            f"This week's dollar range:\n\n"
            f"📈 High: ₦{d.get('usd_wk_hi', d['parallel']):,.0f}\n"
            f"📉 Low: ₦{d.get('usd_wk_lo', d['parallel']):,.0f}\n"
            f"📍 Now: ₦{d['parallel']:,.0f}\n\n"
            f"Range: ₦{round(d.get('usd_wk_hi', d['parallel']) - d.get('usd_wk_lo', d['parallel'])):,.0f}\n\n"
            f"Volatility is the price you pay for a floating currency.\n\n"
            f"📊 NairaIntel"
        )
    },

    # ── OIL PRICE IMPACT ──────────────────────────────────────────────────────

    {
        "id": "oil_impact",
        "condition": lambda d: d.get("brent") is not None,
        "text": lambda d: (
            f"Brent crude: ${d.get('brent', 75):.1f}/bbl today.\n\n"
            f"Nigeria earns ~$18-20 for every barrel exported.\n\n"
            f"At {round(1.42, 2)}M bpd production, that's ~${round(1.42e6 * 19 / 1e9, 1):.1f}B/day in oil revenue.\n\n"
            f"Yet petrol is ₦{d['petrol']:,}/L domestically.\n\n"
            f"The resource curse is real.\n\n"
            f"🛢 NairaIntel"
        )
    },
]


# ─── Type C: Structured data posts ─────────────────────────────────────────────
#
# 20 templates cycling every 10 days (2 Type C slots/day).
# Sources:
#   - Live API data: parallel, BTC, ETH, gold, brent, petrol, diesel, reserves
#   - Accurate hardcoded Nigerian data: CBN charges, NERC tariffs, T-bill rates,
#     mobile data prices, food basket, housing, remittance fees
#   - Weekly RSS: fintech_news only (feedparser, falls back to static)
#
# All hardcoded rates verified Feb 2026. Update quarterly.

TYPE_C_TEMPLATES = [
    "bank_savings_rates",      # savings rates vs inflation (live inflation)
    "bank_transfer_charges",   # NIP/stamp duty/ATM fees — CBN Guide 2020
    "investment_platforms",    # PiggyVest/Cowrywise/T-bills vs inflation
    "crypto_savings_compare",  # USDT/BTC vs naira savings (live BTC)
    "fuel_cost_breakdown",     # petrol/diesel/LPG vs daily wages (live prices)
    "fx_rates_today",          # USD/EUR/GBP/BTC all in naira (live rates)
    "gold_vs_naira",           # gold price in naira (live gold + parallel)
    "weekly_fx_range",         # week hi/low context (live weekly tracking)
    "cbn_rates_snapshot",      # MPR/CRR/parallel spread (live CBN + parallel)
    "remittance_compare",      # sending $200 home: fees by platform
    "data_bundle_costs",       # MTN/Airtel/Glo 1GB vs wages (live petrol as ref)
    "salary_breakdown",        # min wage vs Lagos cost of living
    "oil_revenue_snapshot",    # brent + output + daily earnings (live brent)
    "crypto_weekly_range",     # BTC week hi/low in naira (live BTC + parallel)
    "housing_cost_snapshot",   # rent ranges Lagos/Abuja in naira + USD
    "food_basket_cost",        # weekly food basket now vs 2020 (live inflation)
    "electricity_cost",        # NERC tariff bands + generator cost reality
    "mobile_money_stats",      # NIP volumes + charge math
    "dollar_cost_averaging",   # weekly naira-to-dollar conversion table
    "fintech_news",            # latest headline from TechCabal/Nairametrics RSS
]


def scrape_weekly_data(cache):
    """
    Collects Type C supporting data.
    Most templates use live_data directly — only fintech_news needs a weekly fetch.
    Runs RSS scrape on Sunday; uses cached headline rest of week.
    """
    WAT = datetime.timezone(datetime.timedelta(hours=1))
    now = datetime.datetime.now(tz=WAT)
    today_str = now.strftime("%Y-%m-%d")
    last_scrape = cache.get("type_c_last_scrape", "")

    # Always return hardcoded structure — most content is live-data-driven
    result = cache.get("type_c_data", {})
    if not result:
        result = {}

    # Only fetch RSS on Sunday or if never fetched
    if not last_scrape or now.weekday() == 6:
        print("[INFO] Type C: fetching fintech news RSS...")
        news = _scrape_fintech_news()
        if news:
            result["fintech_news"] = news
            print(f"[INFO] Type C news: {news.get('headline','')[:60]}")
        cache["type_c_data"] = result
        cache["type_c_last_scrape"] = today_str

    return result


def _scrape_fintech_news():
    """Fetch latest finance/fintech headline. Tries TechCabal then Nairametrics RSS."""
    keywords = ["fintech", "bank", "payment", "funding", "naira", "CBN",
                "raise", "million", "billion", "launch", "acquire", "invest"]
    for feed_url in [
        "https://techcabal.com/feed/",
        "https://nairametrics.com/feed/",
    ]:
        try:
            import feedparser
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                continue
            for entry in feed.entries[:15]:
                title = entry.get("title", "").lower()
                if any(kw in title for kw in keywords):
                    return {
                        "headline": entry.get("title", ""),
                        "link":     entry.get("link", ""),
                        "date":     entry.get("published", ""),
                    }
            # No keyword match — return first entry anyway
            e = feed.entries[0]
            return {"headline": e.get("title",""), "link": e.get("link",""), "date": e.get("published","")}
        except Exception as ex:
            print(f"[WARN] Type C RSS {feed_url}: {ex}")
    return None


# ─── Type C renderers ──────────────────────────────────────────────────────────

def render_type_c(template_name, type_c_data, live_data):
    """Dispatch to the correct Type C renderer."""
    d         = live_data
    inflation = d.get("inflation", 33.2)
    parallel  = d.get("parallel", 1578)
    petrol    = d.get("petrol", 897)
    diesel    = d.get("diesel", 1771)
    lpg       = d.get("lpg_kg", 1200)
    btc       = d.get("btc_usd", 65640)
    eth       = d.get("eth_usd", 1895)
    gold      = d.get("gold_usd", 2930)
    brent     = d.get("brent", 75)
    reserves  = d.get("reserves", 34.2)
    cbn       = d.get("cbn", 1346)
    spread    = d.get("spread_pct", 17.2)
    spread_n  = d.get("spread_ngn", round(parallel - cbn, 0))
    eur       = d.get("eur_ngn", 1590)
    gbp       = d.get("gbp_ngn", 1820)
    wk_hi     = d.get("usd_wk_hi", parallel)
    wk_lo     = d.get("usd_wk_lo", parallel)
    btc_wk_hi = d.get("btc_wk_hi", btc)
    btc_wk_lo = d.get("btc_wk_lo", btc)

    # ── 1. Bank savings rates ──────────────────────────────────────────────────
    if template_name == "bank_savings_rates":
        # Verified rates Feb 2026 — traditional banks 4-7%, digital banks 10-15%
        # CBN MPR is 27.5%, savings accounts lag far behind
        rates = [
            ("GTBank", 4.0), ("Access Bank", 5.25), ("Zenith Bank", 4.75),
            ("UBA", 4.5), ("First Bank", 4.0),
        ]
        lines = "\n".join(
            f"  {b}: {r}% ({'+' if r-inflation>=0 else ''}{round(r-inflation,1)}% real)"
            for b, r in rates
        )
        post = (
            f"Savings rates vs {inflation}% inflation:\n\n"
            f"{lines}\n\n"
            f"All 5 lose money in real terms.\n\n"
            f"💰 NairaIntel"
        )
        return _fit(post)

    # ── 2. Bank transfer charges ───────────────────────────────────────────────
    elif template_name == "bank_transfer_charges":
        # CBN Revised Guide to Charges, Banks & OFIs — 2020, still current
        post = (
            f"What banks charge to move YOUR money (CBN 2020 guide):\n\n"
            f"📲 Transfer ≤₦5,000: ₦10 flat\n"
            f"📲 Transfer ≤₦50,000: ₦25 flat\n"
            f"📲 Transfer >₦50,000: ₦50 flat\n"
            f"🏧 ATM (other bank, after 3 free): ₦35\n"
            f"📩 Stamp duty on receipt ≥₦10k: ₦50\n\n"
            f"Banks profit from your own movements.\n\n"
            f"🏦 NairaIntel"
        )
        return _fit(post)

    # ── 3. Investment platforms ────────────────────────────────────────────────
    elif template_name == "investment_platforms":
        # Verified rates Feb 2026. ARM MMF ~18-19%, T-bills ~20%
        platforms = [
            ("ARM MMF", 18.5),
            ("T-Bill (91d)", 20.0),
            ("PiggyVest Lock", 13.0),
            ("Cowrywise", 14.5),
            ("Risevest USD", 10.0),
        ]
        lines = "\n".join(
            f"  {p}: {r}% ({'+' if r-inflation>=0 else ''}{round(r-inflation,1)}% real)"
            for p, r in platforms
        )
        post = (
            f"Returns vs {inflation}% inflation:\n\n"
            f"{lines}\n\n"
            f"Only T-Bills beat inflation (min ₦50M).\n\n"
            f"💰 NairaIntel"
        )
        return _fit(post)

    # ── 4. Crypto vs naira savings ─────────────────────────────────────────────
    elif template_name == "crypto_savings_compare":
        usdt_rate = parallel   # P2P USDT ≈ parallel rate
        # ₦100k invested in different ways 1 year ago
        # BTC 1yr ago ~$42,000; today ~$btc — rough calc
        btc_1yr_ago = 42000
        btc_gain_pct = round((btc - btc_1yr_ago) / btc_1yr_ago * 100, 1)
        post = (
            f"₦100,000 invested 12 months ago:\n\n"
            f"🏦 Bank savings (avg 5%): ₦105,000\n"
            f"  Real value: ₦{round(105000/(1+inflation/100)):,} (lost to inflation)\n\n"
            f"💵 USDT (dollar-linked): ₦{round(100000*(parallel/1150)):,}\n"
            f"  ₦ gained from devaluation alone\n\n"
            f"₿ BTC: {btc_gain_pct:+.1f}% in USD + naira devaluation gains\n\n"
            f"Inflation: {inflation}% | $1 = ₦{parallel:,.0f}\n\n"
            f"📊 NairaIntel"
        )
        return _fit(post)

    # ── 5. Fuel cost breakdown ─────────────────────────────────────────────────
    elif template_name == "fuel_cost_breakdown":
        tank_50     = 50 * petrol
        diesel_20   = 20 * diesel   # 20L typical generator fill
        lpg_12kg    = 12 * lpg      # 12kg cylinder refill
        min_wage    = 70000
        post = (
            f"Fuel costs today vs minimum wage (₦{min_wage:,}/month):\n\n"
            f"⛽ Petrol 50L tank: ₦{tank_50:,} ({round(tank_50/min_wage*100):.0f}% of min wage)\n"
            f"🔌 Diesel 20L gen: ₦{diesel_20:,} ({round(diesel_20/min_wage*100):.0f}% of min wage)\n"
            f"🔥 LPG 12kg cylinder: ₦{lpg_12kg:,} ({round(lpg_12kg/min_wage*100):.0f}% of min wage)\n\n"
            f"June 2023: total would have cost ₦{round(50*185 + 20*700 + 12*800):,}\n"
            f"Today: ₦{round(tank_50 + diesel_20 + lpg_12kg):,}\n\n"
            f"⛽ NairaIntel"
        )
        return _fit(post)

    # ── 6. FX rates today ──────────────────────────────────────────────────────
    elif template_name == "fx_rates_today":
        btc_ngn_m = round(btc * parallel / 1e6, 2)
        eth_ngn_k = round(eth * parallel / 1000, 0)
        post = (
            f"Currency rates in naira today:\n\n"
            f"🇺🇸 $1 (USD):   ₦{parallel:,.0f}\n"
            f"🇪🇺 €1 (EUR):   ₦{eur:,.0f}\n"
            f"🇬🇧 £1 (GBP):   ₦{gbp:,.0f}\n"
            f"₿  1 BTC:      ₦{btc_ngn_m:.2f}M\n"
            f"Ξ  1 ETH:      ₦{eth_ngn_k:,.0f}k\n\n"
            f"CBN official: ₦{cbn:,.0f} | Parallel: ₦{parallel:,.0f}\n"
            f"Spread: {spread:.1f}% (₦{spread_n:,.0f})\n\n"
            f"📊 NairaIntel"
        )
        return _fit(post)

    # ── 7. Gold vs naira ───────────────────────────────────────────────────────
    elif template_name == "gold_vs_naira":
        gold_ngn   = round(gold * parallel)
        gold_2015  = round(1200 * 197)       # gold ~$1,200, rate ₦197 in 2015
        gold_2020  = round(1800 * 360)       # gold ~$1,800, rate ₦360 in 2020
        post = (
            f"Gold price in naira:\n\n"
            f"📅 2015: ₦{gold_2015:,}/oz ($1,200 × ₦197)\n"
            f"📅 2020: ₦{gold_2020:,}/oz ($1,800 × ₦360)\n"
            f"📅 Today: ₦{gold_ngn:,}/oz (${gold:,.0f} × ₦{parallel:,.0f})\n\n"
            f"Gold in naira: up {round((gold_ngn/gold_2015 - 1)*100):.0f}% since 2015.\n"
            f"Naira savings: -ve real return every year.\n\n"
            f"🥇 NairaIntel"
        )
        return _fit(post)

    # ── 8. Weekly FX range ────────────────────────────────────────────────────
    elif template_name == "weekly_fx_range":
        wk_range  = round(wk_hi - wk_lo, 0)
        wk_mid    = round((wk_hi + wk_lo) / 2, 0)
        pos_pct   = round((parallel - wk_lo) / wk_range * 100) if wk_range > 0 else 50
        post = (
            f"USD/NGN this week:\n\n"
            f"📈 High: ₦{wk_hi:,.0f}\n"
            f"📉 Low:  ₦{wk_lo:,.0f}\n"
            f"📍 Now:  ₦{parallel:,.0f} ({pos_pct}% of range)\n"
            f"↔️  Swing: ₦{wk_range:,.0f}\n\n"
            f"A ₦{wk_range:,.0f} weekly range means ₦{round(wk_range * 500000 / parallel):,} "
            f"difference on a $500k salary payment depending on timing.\n\n"
            f"📊 NairaIntel"
        )
        return _fit(post)

    # ── 9. CBN rates snapshot ─────────────────────────────────────────────────
    elif template_name == "cbn_rates_snapshot":
        # CBN MPC raised MPR to 27.5% in Feb 2025, CRR at 50%
        mpr     = 27.5
        crr     = 50.0
        liquidity = 30.0
        real_mpr = round(mpr - inflation, 1)
        post = (
            f"CBN policy rates vs reality:\n\n"
            f"📌 MPR (base rate): {mpr}%\n"
            f"📌 CRR (cash reserve): {crr}%\n"
            f"📌 Liquidity ratio: {liquidity}%\n\n"
            f"Real MPR (inflation-adjusted): {real_mpr:+.1f}%\n"
            f"CBN rate: ₦{cbn:,.0f} | Parallel: ₦{parallel:,.0f}\n"
            f"Spread: {spread:.1f}% — importers pay the premium.\n\n"
            f"🏦 NairaIntel"
        )
        return _fit(post)

    # ── 10. Remittance comparison ──────────────────────────────────────────────
    elif template_name == "remittance_compare":
        # Verified remittance costs Feb 2026 (sending $200 UK→Nigeria)
        # Western Union: ~3.5% + exchange margin ~2% = ~$11 total cost
        # Lemfi: ~1% fee, close to mid-rate = ~$2
        # Grey/Chipper: ~1-1.5%, ~$2-3
        # Wise: ~0.6% fee + mid-rate = ~$1.2 on $200
        amount   = 200
        received = round(amount * parallel)
        post = (
            f"Sending $200 to Nigeria today (₦{received:,} received):\n\n"
            f"🏦 Western Union: ~$11 fee + poor rate → ~₦{round((amount-11)*parallel*0.97):,}\n"
            f"📱 Lemfi/Grey: ~$2 fee + near-parallel → ~₦{round((amount-2)*parallel*0.99):,}\n"
            f"💙 Wise: ~$1.20 fee + mid-rate → ~₦{round((amount-1.2)*parallel*0.985):,}\n\n"
            f"Difference: up to ₦{round(11*parallel*0.97 - 1.2*parallel*0.985):,} per transfer.\n"
            f"Fintech wins on remittances.\n\n"
            f"✈️ NairaIntel"
        )
        return _fit(post)

    # ── 11. Mobile data bundle costs ──────────────────────────────────────────
    elif template_name == "data_bundle_costs":
        # MTN/Airtel/Glo 1GB prices as of Feb 2026 (verified from operator sites)
        # MTN: 1GB = ₦1,200 (30 days), Airtel: ₦1,000, Glo: ₦900
        # In 2020: 1GB ~₦200-300
        mtn_1gb   = 1200
        airtel_1gb = 1000
        glo_1gb   = 900
        min_wage  = 70000
        bundles_min_wage = round(min_wage / mtn_1gb)
        post = (
            f"Mobile data prices today vs 2020:\n\n"
            f"📱 MTN 1GB (30d):   ₦{mtn_1gb:,}  (was ₦300)\n"
            f"📱 Airtel 1GB (30d): ₦{airtel_1gb:,} (was ₦250)\n"
            f"📱 Glo 1GB (30d):   ₦{glo_1gb:,}  (was ₦200)\n\n"
            f"On ₦70k min wage: affords ~{bundles_min_wage} GBs/month.\n"
            f"Inflation: {inflation}% | Data: up ~300-400% since 2020.\n\n"
            f"📱 NairaIntel"
        )
        return _fit(post)

    # ── 12. Salary vs cost of living ──────────────────────────────────────────
    elif template_name == "salary_breakdown":
        # Lagos cost of living estimates Feb 2026
        min_wage   = 70000
        rent_1bed  = 120000   # ₦/month 1-bed, mainland Lagos (annual/12)
        food_mo    = 80000    # conservative monthly food for 1 person
        transport  = 30000    # bus/keke monthly
        data       = 1200     # 1GB MTN
        total      = rent_1bed + food_mo + transport + data
        post = (
            f"Minimum wage (₦{min_wage:,}) vs Lagos survival cost:\n\n"
            f"🏠 1-bed rent (mainland): ₦{rent_1bed:,}/mo\n"
            f"🍚 Food (basic): ₦{food_mo:,}/mo\n"
            f"🚌 Transport: ₦{transport:,}/mo\n"
            f"📱 Data (1GB): ₦{data:,}/mo\n"
            f"━━ Total: ₦{total:,}/mo\n\n"
            f"Shortfall on min wage: ₦{total - min_wage:,}/mo\n"
            f"Before rent, utilities, clothing, health.\n\n"
            f"💰 NairaIntel"
        )
        return _fit(post)

    # ── 13. Oil revenue snapshot ──────────────────────────────────────────────
    elif template_name == "oil_revenue_snapshot":
        oil_prod   = d.get("oil_production", 1.42)   # million bpd
        govt_take  = round(brent * 0.25, 1)           # ~25% of brent to govt after costs
        daily_rev  = round(oil_prod * 1e6 * govt_take / 1e6, 1)  # $M/day
        annual_rev = round(daily_rev * 365 / 1000, 1)  # $B/year
        post = (
            f"Nigeria oil revenue snapshot:\n\n"
            f"🛢 Brent crude: ${brent:.1f}/bbl\n"
            f"🇳🇬 Production: {oil_prod:.2f}M bpd\n"
            f"💵 Est. govt take: ~${govt_take:.0f}/bbl\n"
            f"📅 Est. daily revenue: ~${daily_rev:.0f}M\n"
            f"📅 Est. annual: ~${annual_rev:.1f}B\n\n"
            f"FX reserves: ${reserves:.1f}B\n"
            f"$1 = ₦{parallel:,.0f} despite oil earnings.\n\n"
            f"🛢 NairaIntel"
        )
        return _fit(post)

    # ── 14. BTC weekly range in naira ─────────────────────────────────────────
    elif template_name == "crypto_weekly_range":
        btc_hi_ngn = round(btc_wk_hi * parallel / 1e6, 2)
        btc_lo_ngn = round(btc_wk_lo * parallel / 1e6, 2)
        btc_now_ngn = round(btc * parallel / 1e6, 2)
        btc_swing  = round((btc_wk_hi - btc_wk_lo) / btc_wk_lo * 100, 1) if btc_wk_lo else 0
        post = (
            f"Bitcoin this week (in naira):\n\n"
            f"📈 High: ${btc_wk_hi:,} = ₦{btc_hi_ngn:.2f}M\n"
            f"📉 Low:  ${btc_wk_lo:,} = ₦{btc_lo_ngn:.2f}M\n"
            f"📍 Now:  ${btc:,} = ₦{btc_now_ngn:.2f}M\n"
            f"↔️  Weekly swing: {btc_swing:+.1f}%\n\n"
            f"BTC volatility in naira = dollar volatility × naira volatility.\n"
            f"High risk. High potential hedge.\n\n"
            f"₿ NairaIntel"
        )
        return _fit(post)

    # ── 15. Housing cost snapshot ─────────────────────────────────────────────
    elif template_name == "housing_cost_snapshot":
        # Lagos rental market Feb 2026 — annual rents converted to monthly
        # Source: PropertyPro, Private Property Nigeria averages
        lekki_2bed_yr  = 4200000    # ₦4.2M/yr = ₦350k/month
        mainland_1bed_yr = 1200000  # ₦1.2M/yr = ₦100k/month
        abuja_gwarimpa = 1800000    # ₦1.8M/yr = ₦150k/month
        lekki_usd      = round(lekki_2bed_yr / parallel / 12)
        mainland_usd   = round(mainland_1bed_yr / parallel / 12)
        post = (
            f"Lagos/Abuja rental market today:\n\n"
            f"🏙 Lekki 2-bed: ₦{lekki_2bed_yr//12:,}/mo (~${lekki_usd}/mo)\n"
            f"🏘 Mainland 1-bed: ₦{mainland_1bed_yr//12:,}/mo (~${mainland_usd}/mo)\n"
            f"🏛 Abuja Gwarimpa: ₦{abuja_gwarimpa//12:,}/mo\n\n"
            f"Most landlords demand 1-2 years upfront.\n"
            f"Lekki 2-bed = {round(lekki_2bed_yr/70000):.0f}x monthly min wage — per year.\n\n"
            f"🏠 NairaIntel"
        )
        return _fit(post)

    # ── 16. Food basket cost ──────────────────────────────────────────────────
    elif template_name == "food_basket_cost":
        # Weekly food basket for 1 person, Lagos markets Feb 2026
        # Rice 1kg: ₦2,500 | Tomatoes 1kg: ₦2,000 | Egg crate(30): ₦3,800
        # Chicken 1kg: ₦4,500 | Bread: ₦800 | Groundnut oil 1L: ₦2,200
        basket_now  = 2500 + 2000 + 3800 + 4500 + 800 + 2200   # ₦15,800
        basket_2020 = 600  + 500  + 1200 + 1800 + 300 + 700    # ₦5,100
        increase    = round((basket_now / basket_2020 - 1) * 100)
        post = (
            f"Weekly food basket (1 person), Lagos markets:\n\n"
            f"🛒 2020: ₦{basket_2020:,}/week\n"
            f"🛒 Today: ₦{basket_now:,}/week\n"
            f"📈 Increase: {increase}% in 5 years\n\n"
            f"Rice 1kg: ₦2,500 | Eggs(30): ₦3,800\n"
            f"Chicken 1kg: ₦4,500 | Oil 1L: ₦2,200\n\n"
            f"Inflation: {inflation}%. Food inflation ran even hotter.\n\n"
            f"🍚 NairaIntel"
        )
        return _fit(post)

    # ── 17. Electricity cost ──────────────────────────────────────────────────
    elif template_name == "electricity_cost":
        # NERC Multi-Year Tariff Order (MYTO) 2024 bands — R2 residential
        # Band A (20h/day supply): ₦225/kWh | Band B (16h): ₦63/kWh
        # Band C (12h): ₦50/kWh | Band D (8h): ₦43/kWh | Band E (4h): ₦40/kWh
        # Generator diesel cost: 1L diesel generates ~3kWh → ₦{diesel}/3 per kWh
        gen_kwh = round(diesel / 3)
        post = (
            f"Electricity cost in Nigeria (NERC 2024 tariffs):\n\n"
            f"⚡ Band A (20h/day): ₦225/kWh\n"
            f"⚡ Band B (16h/day): ₦63/kWh\n"
            f"⚡ Band C (12h/day): ₦50/kWh\n"
            f"⚡ Band D/E (<8h/day): ₦40-43/kWh\n\n"
            f"🔌 Gen (diesel ₦{diesel:,}/L): ≈₦{gen_kwh:,}/kWh\n"
            f"Most businesses pay ₦{gen_kwh:,}/kWh for real power.\n\n"
            f"⚡ NairaIntel"
        )
        return _fit(post)

    # ── 18. Mobile money / NIP volumes ────────────────────────────────────────
    elif template_name == "mobile_money_stats":
        # NIBSS NIP data 2024: ~1B+ transactions/month, ₦50T+/month value
        # Source: NIBSS annual report 2024
        nip_monthly_vol = "1B+"
        nip_monthly_val = "₦50T+"
        charge_per_txn  = 25        # average NIP charge ₦25 (₦5k-50k bracket)
        bank_annual_nip = round(1e9 * 12 * 25 / 1e9, 0)  # ₦B/year banks earn on NIP
        post = (
            f"Nigeria's payment rails by numbers:\n\n"
            f"📊 NIP transactions/month: {nip_monthly_vol}\n"
            f"💰 NIP value/month: {nip_monthly_val}\n"
            f"💳 Avg NIP charge: ₦{charge_per_txn}\n"
            f"🏦 Bank NIP revenue/yr: ~₦{bank_annual_nip:.0f}B\n\n"
            f"USSD: 100M+ txns/month on feature phones.\n"
            f"Built on ₦{parallel:,.0f}/$1 and {inflation}% inflation.\n\n"
            f"🏦 NairaIntel"
        )
        return _fit(post)

    # ── 19. Dollar-cost averaging table ───────────────────────────────────────
    elif template_name == "dollar_cost_averaging":
        # Show what consistent naira-to-dollar conversions look like
        amounts = [10000, 20000, 50000, 100000]
        lines = "\n".join(
            f"  ₦{a:,}/week → ${round(a/parallel, 2):.2f} → ${round(a/parallel*52, 0):.0f}/yr"
            for a in amounts
        )
        post = (
            f"Converting naira to dollars weekly:\n\n"
            f"{lines}\n\n"
            f"At ₦{parallel:,.0f}/$1 + {inflation}% inflation:\n"
            f"earn naira → save dollars → spend naira.\n\n"
            f"💵 NairaIntel"
        )
        return _fit(post)

    # ── 20. Fintech news ──────────────────────────────────────────────────────
    elif template_name == "fintech_news":
        news = type_c_data.get("fintech_news")
        if news:
            headline = news.get("headline", "")
            if len(headline) > 130:
                headline = headline[:127] + "..."
            post = (
                f"📰 Nigeria Fintech Update:\n\n"
                f"{headline}\n\n"
                f"$1 = ₦{parallel:,.0f} | Inflation: {inflation}% | BTC: ${btc:,}\n\n"
                f"🏦 NairaIntel"
            )
            return _fit(post)
        # Fallback: ecosystem stat
        post = (
            f"Nigeria fintech ecosystem (2025):\n\n"
            f"💳 Flutterwave: $3B valuation, 34 countries\n"
            f"💳 OPay: 40M+ users, $2B valuation\n"
            f"💳 Moniepoint: SME banking, 10M+ users\n"
            f"💳 Kuda: 8M+ users, digital-only bank\n\n"
            f"Africa's largest fintech market.\n"
            f"Built on {inflation}% inflation & ₦{parallel:,.0f}/$1.\n\n"
            f"🏦 NairaIntel"
        )
        return _fit(post)

    return None


def _fit(text, limit=280):
    """Return text if within limit, else truncate cleanly at last newline."""
    if len(text) <= limit:
        return text
    # Try to cut at a paragraph break
    cut = text[:limit-3].rfind("\n\n")
    if cut > limit // 2:
        return text[:cut] + "\n\n..."
    return text[:limit-3] + "..."




# ─── Type D: Rate snapshots ────────────────────────────────────────────────────
#
# Two sub-types, alternated by which hour fires:
#   hour 6  → crypto snapshot  (BTC / ETH / SOL / USDT)
#   hour 23 → FX snapshot      (USD / GBP / EUR / CAD)
#
# Format mirrors the style: "1 BTC ⇛ ₦X"
# Timestamp pulled from live WAT time.
# USDT/USDC use parallel rate as proxy (P2P USDT ≈ parallel).

def render_type_d(hour, live_data):
    """Render a rate snapshot post. hour 6 = crypto, hour 23 = FX."""
    WAT = datetime.timezone(datetime.timedelta(hours=1))
    now = datetime.datetime.now(tz=WAT)
    ts  = now.strftime("%a %d %b, %Y • %I:%M %p")

    d        = live_data
    parallel = d.get("parallel", 1578)
    cbn      = d.get("cbn", 1346)
    btc      = d.get("btc_usd", 65640)
    eth      = d.get("eth_usd", 1895)
    sol      = d.get("sol_usd", 150)
    eur      = d.get("eur_ngn", 1590)
    gbp      = d.get("gbp_ngn", 1820)
    cad      = d.get("cad_ngn", 1010)

    # USDT/USDC track parallel rate very closely on P2P
    usdt_ngn = round(parallel, 3)
    usdc_ngn = round(parallel * 0.999, 3)   # USDC slight discount to USDT

    btc_ngn  = round(btc * parallel, 3)
    eth_ngn  = round(eth * parallel, 3)
    sol_ngn  = round(sol * parallel, 3)

    if hour == 6:
        # Crypto snapshot
        post = (
            f"Avg. | {ts}\n"
            f"1 BTC ⇛ ₦{btc_ngn:,.3f}\n"
            f"1 ETH ⇛ ₦{eth_ngn:,.3f}\n"
            f"1 SOL ⇛ ₦{sol_ngn:,.3f}\n"
            f"1 USDT ⇛ ₦{usdt_ngn:,.3f}\n"
            f"1 USDC ⇛ ₦{usdc_ngn:,.3f}"
        )
    else:
        # FX snapshot (hour 23)
        post = (
            f"{ts}\n"
            f"1 USD ⇛ ₦{parallel:,.3f}\n"
            f"1 GBP ⇛ ₦{gbp:,.3f}\n"
            f"1 EUR ⇛ ₦{eur:,.3f}\n"
            f"1 CAD ⇛ ₦{cad:,.3f}\n"
            f"CBN: ₦{cbn:,.3f}"
        )

    return post if len(post) <= 280 else _truncate(post)


# ─── Type E: Engagement questions ─────────────────────────────────────────────
#
# 50 questions. Mix of:
#   - Would you rather / A vs B choices
#   - Opinion polls
#   - Personal finance scenarios
#   - Hot takes on Nigerian economy
#
# Rotates sequentially, no repeat until all 50 used.
# No live data needed — pure engagement.

TYPE_E_QUESTIONS = [
    # ── Would you rather ───────────────────────────────────────────────────────
    "If you had the opportunity today, would you choose to earn in dollars:\n\nA. Remotely from Nigeria\nB. Abroad\nC. Both (remote + relocation)\nD. I'm fine earning naira",

    "Would you rather:\n\nA. ₦50M in Nigeria today\nB. $50,000 abroad with a stable job\n\nBe honest.",

    "Would you rather own:\n\nA. A house in Lagos worth ₦150M\nB. $100,000 in a US index fund\n\nWhich actually builds more wealth?",

    "If you could start over, would you:\n\nA. Stay in Nigeria and build here\nB. Japa and send remittances home\nC. Build abroad first, return later\nD. Never return",

    "Would you rather earn:\n\nA. ₦15M once today\nB. ₦3M every year for 5 years\n\nWhich actually pays more?",

    "If NEPA gave you 22hrs of electricity daily, would you:\n\nA. Still buy a generator\nB. Sell your generator immediately\nC. Keep it as backup",

    "Would you rather:\n\nA. High salary in a toxic job\nB. Lower salary in a great environment\n\nWhat's your number? At what salary difference does it stop mattering?",

    "Which would stress you out more:\n\nA. Losing ₦500k in a bad investment\nB. Watching inflation eat ₦500k in savings over 2 years\n\nBoth are losses. Which hits harder?",

    # ── Personal finance scenarios ─────────────────────────────────────────────
    "Your rent is ₦1.2M yearly and your salary is ₦2.4M.\nHalf your income goes to housing.\n\nIs that living or surviving?",

    "You have ₦500k saved. What do you do with it?\n\nA. Dollar savings (Grey/Lemfi)\nB. Fixed deposit\nC. Crypto (BTC/USDT)\nD. Small business\nE. T-Bills",

    "Which builds wealth faster:\n\nA. Saving more\nB. Earning more\n\nMost people debate this but the data is clear. What do you think?",

    "How many months of expenses do you have saved as emergency fund?\n\nA. None\nB. 1–2 months\nC. 3–6 months\nD. 6+ months\n\nBe honest.",

    "At what monthly income (naira) would you feel financially comfortable in Lagos?\n\nA. ₦500k\nB. ₦1M\nC. ₦2M\nD. ₦5M+",

    "Your salary just doubled. What's the first thing you change?\n\nA. Accommodation\nB. Start investing\nC. Clear debt\nD. Nothing — lifestyle inflation is a trap",

    "Is it better to:\n\nA. Rent forever and invest the difference\nB. Buy property as soon as possible\n\nNigeria context matters here.",

    "What percentage of your income goes to food?\n\nA. Under 20%\nB. 20–35%\nC. 35–50%\nD. Over 50%\n\nNationally it's ~56%. Where do you sit?",

    # ── Hot takes / opinions ───────────────────────────────────────────────────
    "Hot take: Owning a car in Lagos is a financial mistake for most people.\n\nAgree or disagree?\n\nFuel + maintenance + parking + traffic time cost = ?",

    "Real question: Is the Nigerian middle class extinct?\n\nA. Yes — it's just rich and poor now\nB. It's shrinking but exists\nC. It never really existed\nD. It's growing quietly",

    "The naira has lost 99% of its value since 1985.\n\nWho's most responsible?\n\nA. The government\nB. Oil dependency\nC. CBN policy\nD. All of the above",

    "Is crypto a legitimate wealth tool in Nigeria or mostly speculation?\n\nA. Legitimate — USDT saved many portfolios\nB. Speculation — too volatile\nC. Both depending on the coin\nD. I don't touch it",

    "Hard truth: most Nigerian salary earners are getting poorer every year even if their salary increases.\n\nIs your salary growing faster than inflation (33.2%)?\n\nA. Yes\nB. No\nC. About the same",

    "What's the biggest financial mistake Nigerians make?\n\nA. Not investing early\nB. Too much money in naira savings\nC. Lifestyle inflation\nD. Sending too much to family\nE. No emergency fund",

    "Should Nigerian companies be forced to offer dollar salary options?\n\nA. Yes — protect workers from devaluation\nB. No — that would cause inflation\nC. Optional — let the market decide",

    "Is Japa worth it financially in the long run?\n\nA. Yes — dollar income changes everything\nB. Depends on where you go\nC. No — cost of living abroad is underestimated\nD. Only if you send money back",

    # ── Economy / current affairs ──────────────────────────────────────────────
    "Petrol went from ₦185 to ₦897 in under 2 years.\n\nWho absorbed most of that cost?\n\nA. Workers (transport costs up)\nB. Business owners (logistics up)\nC. Consumers (everything got more expensive)\nD. All three equally",

    "If the naira hit ₦2,000/$1, what would you do first?\n\nA. Convert all savings to dollars immediately\nB. Buy property (naira prices lag)\nC. Invest in local businesses (import competitors)\nD. Leave",

    "Can Nigeria fix inflation without fixing the exchange rate?\n\nA. No — they're directly linked\nB. Yes — with the right fiscal policy\nC. Neither is fixable right now",

    "Which is more damaging to the average Nigerian:\n\nA. High inflation (33%+)\nB. A weak naira (₦1,578/$1)\nC. Fuel prices (₦897/L)\nD. Electricity cost + generator bills",

    "Nigeria earns billions in oil revenue but 40% of citizens are in poverty.\n\nWhat's the core problem?\n\nA. Corruption\nB. Population growth outpacing revenue\nC. Poor revenue management\nD. All of the above",

    "Will the naira ever get back to ₦500/$1?\n\nA. Yes — in the next 5 years\nB. Yes — but it'll take 10+ years\nC. No — structural issues are too deep\nD. Only if oil hits $200/barrel",

    # ── Investing & markets ────────────────────────────────────────────────────
    "Best place to protect ₦1M from inflation right now?\n\nA. Dollar account (Grey/Lemfi)\nB. T-Bills (20% yield)\nC. NGX stocks\nD. Bitcoin\nE. Real estate",

    "At 33% inflation, keeping ₦1M in a savings account loses you ~₦330k in real value per year.\n\nIs anyone still doing this intentionally? Why?",

    "NGX All-Share Index has gone from 20,000 (2010) to 100,000+ (2024).\nBut the naira fell 600% in the same period.\n\nIs Nigerian stock market investing worth it in dollar terms?",

    "T-Bills currently yield ~20% in Nigeria.\nInflation is 33%.\n\nThat's a -13% real return.\n\nIs there any safe naira investment that beats inflation right now?",

    "Dollar-cost averaging: putting ₦50k/month into dollars for 5 years.\n\nRealistic for most Nigerians?\n\nA. Yes — cut expenses to make it work\nB. No — ₦50k is too much to lock away\nC. I'm already doing this\nD. I'd put it in crypto instead",

    # ── Generational / lifestyle ───────────────────────────────────────────────
    "Are Nigerian parents a financial liability or asset for their adult children?\n\nA. Liability — school fees + upkeep + medical\nB. Asset — inheritance, land, connections\nC. Both\nD. Depends entirely on the family",

    "Gen Z Nigerians: are they more financially aware than previous generations?\n\nA. Yes — social media, crypto, side hustles\nB. No — same problems, just louder\nC. More aware but worse conditions\nD. Too early to judge",

    "Side hustle or salary increase — which is the better wealth strategy in Nigeria?\n\nA. Side hustle — multiple income streams\nB. Salary — compound career growth\nC. Both are necessary\nD. Neither if you don't manage what you have",

    "What's the minimum salary you'd accept to relocate from Lagos to Abuja?\n\nA. Same salary — Abuja is cheaper\nB. 20% increase\nC. 50% increase\nD. I'd never leave Lagos",

    "Is having a car in Nigeria still a status symbol or just a necessity?\n\nA. Status — people still judge by car\nB. Necessity — public transport is unreliable\nC. Both depending on where you live\nD. It's becoming a burden",

    # ── Savings / behaviour ────────────────────────────────────────────────────
    "What's your savings strategy in 2026?\n\nA. Dollar-denominated accounts\nB. T-Bills / money market\nC. Crypto (USDT/BTC)\nD. I'm spending everything — survival mode\nE. NGX / stocks",

    "How do you protect your naira income from devaluation?\n\nA. Convert to dollars immediately\nB. Buy assets (property, gold)\nC. Invest in stocks/T-Bills\nD. Spend it fast before it loses value\nE. I haven't figured this out yet",

    "Is ₦70,000 minimum wage a joke, a crime, or a starting point?\n\nA. A joke — it's not survivable in any city\nB. A crime — government knows this\nC. A starting point — it just needs to rise faster\nD. It's not meant to be the only income",

    "What financial goal are you working toward in 2026?\n\nA. Emergency fund (3–6 months)\nB. First investment\nC. Dollar savings\nD. Debt-free\nE. Property/land\nF. Survival — ask me again next year",

    "Final question for the week: what's the one financial move you wish you'd made 5 years ago?\n\nDollar savings? Crypto? Property? Stocks?\n\nWhat was the missed opportunity?",
]


def render_type_e(cache):
    """Pick next engagement question, rotate through pool without repeating."""
    used = cache.get("text_post_used_e", [])
    total = len(TYPE_E_QUESTIONS)
    unused = [i for i in range(total) if i not in used]
    if not unused:
        cache["text_post_used_e"] = []
        unused = list(range(total))
    chosen = unused[0]
    used_list = cache.get("text_post_used_e", [])
    used_list.append(chosen)
    cache["text_post_used_e"] = used_list
    text = TYPE_E_QUESTIONS[chosen]
    return text if len(text) <= 280 else _truncate(text)




# ─── Main post builder ─────────────────────────────────────────────────────────

def build_text_post(hour, live_data, cache):
    """
    Build the appropriate text post for the given hour.
    Returns (post_text, post_type) or (None, None) if not a post slot.
    """
    from post_schedule import (
        is_text_post_hour, get_slot_type,
        get_next_fact_index, get_type_b_template_index,
        get_type_c_template_index, SLOT_CATEGORIES
    )

    if not is_text_post_hour(hour):
        return None, None

    slot_type = get_slot_type(hour)

    # ── Type A ────────────────────────────────────────────────────────────────
    if slot_type == "A":
        from facts_pool import render_fact
        preferred_cats = SLOT_CATEGORIES.get(hour, [])
        fact_idx = get_next_fact_index(cache, preferred_cats)
        text = render_fact(fact_idx, live_data)
        if text and len(text) <= 280:
            return text, "A"
        # Fact too long — try next one
        for _ in range(5):
            fact_idx = get_next_fact_index(cache, preferred_cats)
            text = render_fact(fact_idx, live_data)
            if text and len(text) <= 280:
                return text, "A"
        return text[:277] + "..." if text else None, "A"

    # ── Type B ────────────────────────────────────────────────────────────────
    elif slot_type == "B":
        # Find applicable templates (condition met)
        applicable = [
            (i, t) for i, t in enumerate(TYPE_B_TEMPLATES)
            if t["condition"](live_data)
        ]
        if not applicable:
            return None, None

        # Pick next unused
        used_b = set(cache.get("text_post_used_b", []))
        unused = [(i, t) for i, t in applicable if i not in used_b]
        if not unused:
            cache["text_post_used_b"] = []
            unused = applicable

        chosen_i, chosen_t = unused[0]
        used_b_list = cache.get("text_post_used_b", [])
        used_b_list.append(chosen_i)
        cache["text_post_used_b"] = used_b_list

        try:
            text = chosen_t["text"](live_data)
            return (text if len(text) <= 280 else _truncate(text)), "B"
        except Exception as e:
            print(f"[WARN] Type B render error: {e}")
            return None, None

    # ── Type C ────────────────────────────────────────────────────────────────
    elif slot_type == "C":
        type_c_data = scrape_weekly_data(cache)
        used_c = cache.get("text_post_used_c", [])
        unused_c = [t for t in TYPE_C_TEMPLATES if t not in used_c]
        if not unused_c:
            cache["text_post_used_c"] = []
            unused_c = TYPE_C_TEMPLATES

        template_name = unused_c[0]
        used_c_list = cache.get("text_post_used_c", [])
        used_c_list.append(template_name)
        cache["text_post_used_c"] = used_c_list

        text = render_type_c(template_name, type_c_data, live_data)
        return (text if text and len(text) <= 280 else _truncate(text or "")), "C"

    # ── Type D ────────────────────────────────────────────────────────────────
    elif slot_type == "D":
        text = render_type_d(hour, live_data)
        return (text if text and len(text) <= 280 else _truncate(text or "")), "D"

    # ── Type E ────────────────────────────────────────────────────────────────
    elif slot_type == "E":
        text = render_type_e(cache)
        return (text if text and len(text) <= 280 else _truncate(text or "")), "E"

    # ── Type F ────────────────────────────────────────────────────────────────
    elif slot_type == "F":
        from type_f_pool import render_type_f
        from post_schedule import get_next_f_index, F_SLOT_CATEGORIES
        preferred_cats = F_SLOT_CATEGORIES.get(hour, [])
        f_idx = get_next_f_index(cache, preferred_cats)
        text = render_type_f(f_idx, live_data)
        if text and len(text) <= 280:
            return text, "F"
        # Too long — try next one (tags can add chars)
        for _ in range(5):
            f_idx = get_next_f_index(cache, preferred_cats)
            text = render_type_f(f_idx, live_data)
            if text and len(text) <= 280:
                return text, "F"
        return (_truncate(text) if text else None), "F"

    return None, None


# ─── Posting ───────────────────────────────────────────────────────────────────

def post_text_tweet(text, config):
    """Post a text-only tweet via Tweepy v2."""
    try:
        client = tweepy.Client(
            consumer_key=config["X_API_KEY"],
            consumer_secret=config["X_API_SECRET"],
            access_token=config["X_ACCESS_TOKEN"],
            access_token_secret=config["X_ACCESS_TOKEN_SECRET"]
        )
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"[OK] Text tweet posted: https://x.com/i/web/status/{tweet_id}")
        return tweet_id

    except tweepy.errors.Forbidden as e:
        err_str = str(e).lower()
        print(f"[ERROR] 403 Forbidden — X rejected the post.")
        print(f"[ERROR] Raw error: {e}")
        if "not permitted" in err_str or "authorization" in err_str:
            print("[DIAGNOSIS] App permissions are likely set to Read-only.")
            print("[FIX] developer.twitter.com → App → User auth settings → Read+Write")
            print("[FIX] Then REGENERATE Access Token + Secret and update GitHub Secrets.")
        elif "duplicate" in err_str:
            print("[DIAGNOSIS] Duplicate content — too similar to a recent post.")
            print("[FIX] Usually harmless. Rotation logic should prevent recurrence.")
        else:
            print("[DIAGNOSIS] Unknown 403. Check app status/billing in Developer Portal.")
        raise

    except tweepy.errors.TooManyRequests as e:
        print(f"[ERROR] 429 Rate limit — too many requests.")
        print(f"[ERROR] Raw error: {e}")
        print("[DIAGNOSIS] Free tier allows 17 posts/24h. Check for duplicate workflow runs.")
        raise

    except tweepy.errors.Unauthorized as e:
        print(f"[ERROR] 401 Unauthorized — credentials rejected.")
        print(f"[ERROR] Raw error: {e}")
        print("[FIX] Regenerate all 4 X credentials in Developer Portal and update Secrets.")
        raise

    except tweepy.errors.BadRequest as e:
        print(f"[ERROR] 400 Bad Request — tweet content rejected.")
        print(f"[ERROR] Raw error: {e}")
        print(f"[DEBUG] Post was {len(text)} chars:
{text}")
        raise

    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        raise


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _inflation_loss(inflation):
    """How much ₦100k loses in real value at given inflation rate."""
    return round(100000 * (1 - (1 / (1 + inflation / 100))), 0)

def _inflation_gain(current, prev):
    """How much ₦100k preserved vs previous month's inflation."""
    loss_now  = 100000 * (1 - (1 / (1 + current / 100)))
    loss_prev = 100000 * (1 - (1 / (1 + prev / 100)))
    return max(0, round(loss_prev - loss_now, 0))

def _rate_change(data):
    """Absolute change in parallel rate vs last month."""
    return abs(round(data.get("parallel", 0) - data.get("prev_parallel", data.get("parallel", 0)), 0))

def _salary_recovery(data):
    """How many extra dollars a ₦500k salary is worth after rate drop."""
    now  = round(500000 / data.get("parallel", 1499))
    prev = round(500000 / data.get("prev_parallel", data.get("parallel", 1499)))
    return abs(now - prev)

def _petrol_savings(data):
    """Naira saved on 50L fill vs previous petrol price."""
    now  = 50 * data.get("petrol", 897)
    prev = 50 * data.get("prev_petrol", data.get("petrol", 897))
    return abs(prev - now)

def _truncate(text, limit=277):
    """Truncate text to fit in 280 chars with ellipsis."""
    if len(text) <= limit:
        return text
    return text[:limit] + "..."
