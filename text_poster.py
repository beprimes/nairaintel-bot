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


# ─── Type C: Weekly scraped data ───────────────────────────────────────────────

TYPE_C_TEMPLATES = [
    "bank_savings_rates",
    "bank_transfer_charges",
    "fintech_spotlight",
    "investment_platforms",
]


def scrape_weekly_data(cache):
    """
    Scrape Type C data: bank rates, charges, fintech news.
    Runs once per week (Sunday) and caches results.
    Returns cached data if scrape already done this week.
    """
    now = datetime.datetime.now()
    last_scrape = cache.get("type_c_last_scrape", "")
    today_str = now.strftime("%Y-%m-%d")

    # Only re-scrape on Sunday or if never scraped
    if last_scrape and now.weekday() != 6:
        # Not Sunday — use cached data
        cached = cache.get("type_c_data", {})
        if cached:
            return cached

    print("[INFO] Type C: running weekly scrape...")
    result = {}

    # ── Bank savings rates ────────────────────────────────────────────────────
    savings = _scrape_savings_rates()
    if savings:
        result["savings_rates"] = savings
        print(f"[INFO] Type C savings rates: {savings}")

    # ── Bank transfer charges ─────────────────────────────────────────────────
    charges = _scrape_transfer_charges()
    if charges:
        result["transfer_charges"] = charges

    # ── Fintech news ──────────────────────────────────────────────────────────
    news = _scrape_fintech_news()
    if news:
        result["fintech_news"] = news

    # ── Investment platform rates ─────────────────────────────────────────────
    invest = _scrape_investment_rates()
    if invest:
        result["investment_rates"] = invest

    if result:
        cache["type_c_data"] = result
        cache["type_c_last_scrape"] = today_str
        print("[INFO] Type C: scrape complete, cached.")
    else:
        print("[WARN] Type C: all scrapes failed, using last cached data.")
        result = cache.get("type_c_data", {})

    return result


def _scrape_savings_rates():
    """Scrape current savings/deposit rates from CBN or Nairametrics."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        # CBN publishes MPC rates — savings rates follow from this
        # Also try Nairametrics for bank rate comparisons
        url = "https://nairametrics.com/category/finance-and-economy/banking-sector/"
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code == 200:
            text = r.text
            # Look for savings rate mentions
            rates = {}
            # Pattern: "X% per annum" or "X% p.a." near a bank name
            bank_names = ["GTBank", "Zenith", "Access", "UBA", "First Bank",
                         "Kuda", "PiggyVest", "Cowrywise", "Carbon"]
            for bank in bank_names:
                pat = rf'{bank}[^.]*?(\d{{1,2}}(?:\.\d{{1,2}})?)\s*%'
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    rate = float(m.group(1))
                    if 1 <= rate <= 30:
                        rates[bank] = rate

            if rates:
                return rates
    except Exception as e:
        print(f"[WARN] Type C savings scrape: {e}")

    # Fallback: known approximate rates (updated quarterly)
    return {
        "GTBank": 4.0,
        "Zenith Bank": 4.5,
        "Access Bank": 5.0,
        "UBA": 4.0,
        "Kuda": 10.0,
        "PiggyVest Flex": 10.0,
        "PiggyVest Safelock": 13.0,
        "Cowrywise": 14.5,
        "Carbon": 15.0,
        "_source": "approximate — verify at bank",
        "_date": datetime.date.today().isoformat(),
    }


def _scrape_transfer_charges():
    """CBN-regulated bank transfer charges."""
    # CBN Revised Guide to Charges by Banks 2020 — these rarely change
    # Returns known charges as fallback
    return {
        "NIP_below_5k": 10,       # ₦10 flat for transfers ≤ ₦5,000
        "NIP_5k_to_50k": 25,      # ₦25 flat for ₦5,001 – ₦50,000
        "NIP_above_50k": 50,      # ₦50 flat for > ₦50,000
        "stamp_duty": 50,         # ₦50 stamp duty on transfers ≥ ₦10,000 (receiving)
        "ATM_own_bank": 0,        # Free
        "ATM_other_bank_3": 35,   # ₦35 after 3 free/month
        "card_maintenance": 50,   # ₦50/month card maintenance
        "SMS_alert": 4,           # ₦4 per SMS alert (varies)
        "_source": "CBN Revised Guide to Charges 2020",
        "_date": datetime.date.today().isoformat(),
    }


def _scrape_fintech_news():
    """Get latest fintech headline from Nairametrics or TechCabal RSS."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        # Try TechCabal RSS — plain XML, no JS rendering
        import feedparser
        feed = feedparser.parse("https://techcabal.com/feed/")
        if feed.entries:
            # Find fintech/finance relevant entry
            keywords = ["fintech", "bank", "payment", "funding", "naira", "CBN",
                       "investment", "startup", "raise", "million", "billion"]
            for entry in feed.entries[:10]:
                title = entry.get("title", "").lower()
                if any(kw in title for kw in keywords):
                    return {
                        "headline": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "date": entry.get("published", ""),
                    }
            # Return first entry if no keyword match
            e = feed.entries[0]
            return {
                "headline": e.get("title", ""),
                "link": e.get("link", ""),
                "date": e.get("published", ""),
            }
    except Exception as e:
        print(f"[WARN] Type C RSS: {e}")

    try:
        # Try Nairametrics RSS
        import feedparser
        feed = feedparser.parse("https://nairametrics.com/feed/")
        if feed.entries:
            keywords = ["bank", "fintech", "CBN", "naira", "rate", "inflation",
                       "investment", "payment", "billion", "million"]
            for entry in feed.entries[:10]:
                title = entry.get("title", "").lower()
                if any(kw in title for kw in keywords):
                    return {
                        "headline": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "date": entry.get("published", ""),
                    }
    except Exception as e2:
        print(f"[WARN] Type C Nairametrics RSS: {e2}")

    return None


def _scrape_investment_rates():
    """Known investment platform rates — updated manually quarterly."""
    return {
        "PiggyVest Safelock": {"rate": 13.0, "type": "fixed", "min_days": 10},
        "Cowrywise": {"rate": 14.5, "type": "flexible", "min_days": 1},
        "Carbon": {"rate": 15.0, "type": "fixed", "min_days": 30},
        "Bamboo (USD)": {"rate": 6.0, "type": "flexible", "min_days": 1},
        "Risevest (USD)": {"rate": 10.0, "type": "fixed", "min_days": 90},
        "ARM Money Market": {"rate": 18.5, "type": "flexible", "min_days": 1},
        "FBN Quest T-Bill": {"rate": 20.0, "type": "fixed", "min_days": 91},
        "_source": "platform websites — verify before investing",
        "_date": datetime.date.today().isoformat(),
        "_inflation": None,   # filled at render time
    }


# ─── Type C renderers ──────────────────────────────────────────────────────────

def render_type_c(template_name, type_c_data, live_data):
    """Render a Type C post from cached weekly data + live data."""
    inflation = live_data.get("inflation", 33.2)
    parallel  = live_data.get("parallel", 1499)

    if template_name == "bank_savings_rates":
        rates = type_c_data.get("savings_rates", {})
        if not rates:
            return None
        lines = []
        for bank, rate in rates.items():
            if bank.startswith("_"):
                continue
            real = round(rate - inflation, 1)
            sign = "+" if real >= 0 else ""
            lines.append(f"  {bank}: {rate}% ({sign}{real}% real)")

        date_str = rates.get("_date", "recent")
        post = (
            f"Best savings rates in Nigeria vs inflation:\n\n"
            + "\n".join(lines[:6])
            + f"\n\nInflation: {inflation}%\n"
            f"Any rate below {inflation}% = losing money in real terms.\n\n"
            f"💰 NairaIntel"
        )
        return post if len(post) <= 280 else _truncate(post)

    elif template_name == "bank_transfer_charges":
        ch = type_c_data.get("transfer_charges", {})
        if not ch:
            return None
        post = (
            f"What Nigerian banks charge to move your own money:\n\n"
            f"📲 Transfer ≤₦5k: ₦{ch.get('NIP_below_5k', 10)}\n"
            f"📲 Transfer ≤₦50k: ₦{ch.get('NIP_5k_to_50k', 25)}\n"
            f"📲 Transfer >₦50k: ₦{ch.get('NIP_above_50k', 50)}\n"
            f"💳 ATM (other bank): ₦{ch.get('ATM_other_bank_3', 35)}/withdrawal\n"
            f"📩 Stamp duty (receiving ≥₦10k): ₦{ch.get('stamp_duty', 50)}\n\n"
            f"₦1 to send, ₦{ch.get('stamp_duty', 50)} to receive.\n"
            f"Banks profit from friction.\n\n"
            f"🏦 NairaIntel"
        )
        return post if len(post) <= 280 else _truncate(post)

    elif template_name == "fintech_spotlight":
        news = type_c_data.get("fintech_news")
        if not news:
            # Fallback fintech fact
            return (
                f"Nigeria fintech by numbers:\n\n"
                f"💳 Flutterwave: $3B valuation\n"
                f"💳 Paystack: acquired by Stripe $200M\n"
                f"💳 Moniepoint: 10M+ users\n"
                f"💳 OPay: 40M+ users\n\n"
                f"Africa's largest fintech ecosystem.\n"
                f"$1 = ₦{parallel:,.0f} and fintech still growing.\n\n"
                f"🏦 NairaIntel"
            )
        headline = news.get("headline", "")
        # Keep it short
        if len(headline) > 120:
            headline = headline[:117] + "..."
        post = (
            f"📰 Nigeria Fintech Update:\n\n"
            f"{headline}\n\n"
            f"$1 = ₦{parallel:,.0f} | Inflation: {inflation}%\n\n"
            f"🏦 NairaIntel"
        )
        return post if len(post) <= 280 else _truncate(post)

    elif template_name == "investment_platforms":
        inv = type_c_data.get("investment_rates", {})
        if not inv:
            return None
        lines = []
        for platform, info in inv.items():
            if platform.startswith("_"):
                continue
            if isinstance(info, dict):
                rate = info.get("rate", 0)
                real = round(rate - inflation, 1)
                sign = "+" if real >= 0 else ""
                usd = "(USD)" in platform
                tag = "🌍" if usd else "🇳🇬"
                lines.append(f"{tag} {platform}: {rate}% ({sign}{real}% real)")

        post = (
            f"Investment returns vs inflation ({inflation}%):\n\n"
            + "\n".join(lines[:5])
            + f"\n\nOnly USD-denominated accounts beat naira inflation.\n\n"
            f"💰 NairaIntel"
        )
        return post if len(post) <= 280 else _truncate(post)

    return None


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
    except Exception as e:
        print(f"[ERROR] Text tweet failed: {e}")
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
