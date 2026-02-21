"""
fetcher.py — All data fetching for AzaIndex Bot
Handles 4 tiers: live APIs, daily scrapes, weekly scrapes, monthly scrapes
Falls back to cache on any failure.
"""

import json
import os
import requests
import datetime
from datetime import timezone

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.json")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def increment_failure(cache, key):
    cache["scrape_failures"][key] = cache["scrape_failures"].get(key, 0) + 1

def reset_failure(cache, key):
    cache["scrape_failures"][key] = 0

def should_alert(cache, key, threshold=3):
    return cache["scrape_failures"].get(key, 0) >= threshold

# ─── Tier 1: Live APIs (every run) ────────────────────────────────────────────

def fetch_exchange_rates(api_key):
    """ExchangeRate-API: USD/NGN and all cross-rates"""
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        r = requests.get(url, timeout=10)
        data = r.json()
        rates = data.get("conversion_rates", {})
        return {
            "ngn": rates.get("NGN", None),
            "eur_ngn": rates.get("NGN", 0) / rates.get("EUR", 1) * rates.get("EUR", 1),
            "gbp_ngn": rates.get("NGN", 0) / rates.get("GBP", 1) if rates.get("GBP") else None,
            "cny_ngn": rates.get("NGN", 0) / rates.get("CNY", 1) if rates.get("CNY") else None,
            "kes_ngn": rates.get("NGN", 0) / rates.get("KES", 1) if rates.get("KES") else None,
            "ghs_ngn": rates.get("NGN", 0) / rates.get("GHS", 1) if rates.get("GHS") else None,
            "zar_ngn": rates.get("NGN", 0) / rates.get("ZAR", 1) if rates.get("ZAR") else None,
            "egp_ngn": rates.get("NGN", 0) / rates.get("EGP", 1) if rates.get("EGP") else None,
            "xof_ngn": rates.get("NGN", 0) / rates.get("XOF", 1) if rates.get("XOF") else None,
            "eur_usd": 1 / rates.get("EUR", 1),
            "gbp_usd": 1 / rates.get("GBP", 1) if rates.get("GBP") else None,
        }
    except Exception as e:
        print(f"[WARN] ExchangeRate-API failed: {e}")
        return None


def fetch_crypto_prices():
    """CoinGecko free API: BTC, ETH, BNB, Gold prices + 24h change"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,binancecoin,tether,gold",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return {
            "btc_usd": data.get("bitcoin", {}).get("usd"),
            "btc_chg": data.get("bitcoin", {}).get("usd_24h_change"),
            "eth_usd": data.get("ethereum", {}).get("usd"),
            "eth_chg": data.get("ethereum", {}).get("usd_24h_change"),
            "bnb_usd": data.get("binancecoin", {}).get("usd"),
            "bnb_chg": data.get("binancecoin", {}).get("usd_24h_change"),
            "gold_usd": data.get("gold", {}).get("usd"),
            "gold_chg": data.get("gold", {}).get("usd_24h_change"),
        }
    except Exception as e:
        print(f"[WARN] CoinGecko failed: {e}")
        return None


def fetch_binance_p2p():
    """Binance P2P: USDT/NGN buy price"""
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "NGN",
            "merchantCheck": False,
            "page": 1,
            "payTypes": [],
            "rows": 5,
            "tradeType": "BUY"
        }
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        prices = [float(ad["adv"]["price"]) for ad in data.get("data", [])]
        if prices:
            return sum(prices[:3]) / min(3, len(prices))
        return None
    except Exception as e:
        print(f"[WARN] Binance P2P failed: {e}")
        return None


def fetch_bybit_p2p():
    """Bybit P2P: USDT/NGN buy price"""
    try:
        url = "https://api2.bybit.com/fiat/otc/item/online"
        payload = {
            "tokenId": "USDT",
            "currencyId": "NGN",
            "payment": [],
            "side": "0",
            "size": "5",
            "page": "1"
        }
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        items = data.get("result", {}).get("items", [])
        prices = [float(i["price"]) for i in items[:3] if i.get("price")]
        if prices:
            return sum(prices) / len(prices)
        return None
    except Exception as e:
        print(f"[WARN] Bybit P2P failed: {e}")
        return None


def fetch_wise_rate():
    """Wise public rate: USD to NGN"""
    try:
        url = "https://wise.com/gb/currency-converter/usd-to-ngn-rate"
        # Use their public API endpoint
        api_url = "https://api.wise.com/v1/rates?source=USD&target=NGN"
        r = requests.get(api_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("rate")
        return None
    except Exception as e:
        print(f"[WARN] Wise rate failed: {e}")
        return None


def fetch_oil_prices():
    """Stooq: Brent crude and Bonny Light"""
    try:
        # Brent
        r_brent = requests.get("https://stooq.com/q/l/?s=lcoj.f&f=sd2t2ohlcv&h&e=csv", timeout=10)
        lines = r_brent.text.strip().split("\n")
        brent = None
        brent_prev = None
        if len(lines) > 1:
            parts = lines[-1].split(",")
            if len(parts) >= 5:
                brent = float(parts[4])
            if len(lines) > 2:
                prev_parts = lines[-2].split(",")
                if len(prev_parts) >= 5:
                    brent_prev = float(prev_parts[4])

        brent_chg = None
        if brent and brent_prev and brent_prev != 0:
            brent_chg = ((brent - brent_prev) / brent_prev) * 100

        return {
            "brent": brent,
            "brent_chg": brent_chg,
            "bonny": brent + 1.7 if brent else None,  # Bonny Light typically ~$1.5-2 premium
            "bonny_chg": brent_chg,
        }
    except Exception as e:
        print(f"[WARN] Oil price fetch failed: {e}")
        return None


def fetch_global_indices():
    """Stooq: S&P500, FTSE, DAX, Nikkei, DXY"""
    results = {}
    symbols = {
        "sp500": "^spx",
        "ftse": "^ftse",
        "dax": "^dax",
        "nikkei": "^nkx",
        "dxy": "dx.f",
    }
    for key, sym in symbols.items():
        try:
            r = requests.get(f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv", timeout=10)
            lines = r.text.strip().split("\n")
            if len(lines) > 1:
                parts = lines[-1].split(",")
                if len(parts) >= 5:
                    val = float(parts[4])
                    results[key] = val
                    if len(lines) > 2:
                        prev = lines[-2].split(",")
                        if len(prev) >= 5:
                            prev_val = float(prev[4])
                            results[f"{key}_chg"] = ((val - prev_val) / prev_val) * 100
        except Exception as e:
            print(f"[WARN] Stooq {key} failed: {e}")
    return results


def fetch_african_indices():
    """Stooq: JSE, NSE Kenya, EGX, NGX"""
    results = {}
    symbols = {
        "jse": "^jse",
        "egx": "^egx30",
    }
    for key, sym in symbols.items():
        try:
            r = requests.get(f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv", timeout=10)
            lines = r.text.strip().split("\n")
            if len(lines) > 1:
                parts = lines[-1].split(",")
                if len(parts) >= 5:
                    val = float(parts[4])
                    results[key] = val
                    if len(lines) > 2:
                        prev = lines[-2].split(",")
                        if len(prev) >= 5:
                            prev_val = float(prev[4])
                            results[f"{key}_chg"] = ((val - prev_val) / prev_val) * 100
        except Exception as e:
            print(f"[WARN] Stooq {key} failed: {e}")
    return results


def fetch_commodities():
    """Stooq: Silver, Cocoa"""
    results = {}
    symbols = {"silver": "xagusd", "cocoa": "cc.f"}
    for key, sym in symbols.items():
        try:
            r = requests.get(f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv", timeout=10)
            lines = r.text.strip().split("\n")
            if len(lines) > 1:
                parts = lines[-1].split(",")
                if len(parts) >= 5:
                    val = float(parts[4])
                    results[f"{key}_usd"] = val
                    if len(lines) > 2:
                        prev = lines[-2].split(",")
                        if len(prev) >= 5:
                            prev_val = float(prev[4])
                            results[f"{key}_chg"] = ((val - prev_val) / prev_val) * 100
        except Exception as e:
            print(f"[WARN] Stooq {key} failed: {e}")
    return results


# ─── Tier 2: Daily scrapes (first run only) ────────────────────────────────────

def fetch_ngx_movers(cache):
    """Scrape NGX top movers — optional, falls back gracefully"""
    try:
        r = requests.get("https://ngxgroup.com/exchange/trade/equities/", timeout=15,
                         headers={"User-Agent": "Mozilla/5.0"})
        # Parse top gainers/losers from NGX website
        # This is a best-effort scrape — structure may change
        from html.parser import HTMLParser
        # If scrape succeeds, parse and return movers
        # For now return None to trigger fallback (real parsing depends on live page structure)
        return None
    except Exception as e:
        print(f"[WARN] NGX movers scrape failed: {e}")
        return None


def fetch_fuel_prices(cache):
    """Scrape pump prices from Pricecheck.ng — cached daily"""
    try:
        r = requests.get("https://pricecheck.ng/fuel-prices/",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        text = r.text
        import re
        # Look for petrol price pattern like ₦897
        petrol_match = re.search(r'(?:petrol|pms)[^\d]*?(\d{3,4})', text, re.IGNORECASE)
        diesel_match = re.search(r'(?:diesel|ago)[^\d]*?(\d{3,4})', text, re.IGNORECASE)
        result = {}
        if petrol_match:
            result["petrol"] = int(petrol_match.group(1))
        if diesel_match:
            result["diesel"] = int(diesel_match.group(1))
        if result:
            return result
        return None
    except Exception as e:
        print(f"[WARN] Fuel price scrape failed: {e}")
        return None


def fetch_fx_reserves(cache):
    """CBN FX reserves — weekly"""
    try:
        r = requests.get("https://www.cbn.gov.ng/IntOps/ExtReserves.asp",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        import re
        match = re.search(r'\$([\d,\.]+)\s*(?:billion|bn)', r.text, re.IGNORECASE)
        if match:
            val = float(match.group(1).replace(",", ""))
            return val
        return None
    except Exception as e:
        print(f"[WARN] FX reserves scrape failed: {e}")
        return None


# ─── Master fetch function ────────────────────────────────────────────────────

def fetch_all_data(config):
    """
    Fetch all data, using cache as fallback.
    Returns complete data dict ready for image generation.
    """
    cache = load_cache()
    now = datetime.datetime.now()
    is_first_run_today = now.hour < 9  # Only 08:00 run does tier2 scrapes
    is_monday = now.weekday() == 0
    is_first_of_month = now.day == 1

    data = {}
    alerts = []

    # ── TIER 1: Live APIs ──────────────────────────────────────────────────────
    print("[INFO] Fetching exchange rates...")
    fx = fetch_exchange_rates(config.get("EXCHANGERATE_API_KEY", ""))
    if fx and fx.get("ngn"):
        cbn_rate = fx["ngn"]
        data["cbn"] = cbn_rate
        data["eur_ngn"] = fx.get("gbp_ngn", 0) * fx.get("eur_usd", 1)  # derive
        data["eur_ngn"] = cbn_rate / 0.89  # approximate EUR rate
        data["gbp_ngn"] = fx.get("gbp_ngn") or cbn_rate * 1.26
        data["cny_ngn"] = fx.get("cny_ngn") or cbn_rate * 0.14
        data["kes_ngn"] = fx.get("kes_ngn") or cbn_rate * 0.0077
        data["ghs_ngn"] = fx.get("ghs_ngn") or cbn_rate * 0.065
        data["zar_ngn"] = fx.get("zar_ngn") or cbn_rate * 0.053
        data["egp_ngn"] = fx.get("egp_ngn") or cbn_rate * 0.020
        data["xof_ngn"] = fx.get("xof_ngn") or cbn_rate * 0.0015
    else:
        # Fallback: use last known parallel rate
        data["cbn"] = cache.get("last_cbn", 1298)
        data["eur_ngn"] = cache.get("last_eur_ngn", 1458)
        data["gbp_ngn"] = cache.get("last_gbp_ngn", 1712)
        data["cny_ngn"] = cache.get("last_cny_ngn", 184)
        data["kes_ngn"] = cache.get("last_kes_ngn", 10.4)
        data["ghs_ngn"] = cache.get("last_ghs_ngn", 88.5)
        data["zar_ngn"] = cache.get("last_zar_ngn", 72.3)
        data["egp_ngn"] = cache.get("last_egp_ngn", 27.8)
        data["xof_ngn"] = cache.get("last_xof_ngn", 2.1)

    # Dummy daily changes for African currencies (ExchangeRate-API free doesn't give history)
    # These will be 0 unless we track yesterday's values in cache
    for cur in ["kes", "ghs", "zar", "egp", "xof"]:
        key = f"{cur}_ngn"
        prev_key = f"prev_{key}"
        prev = cache.get(prev_key)
        curr = data.get(key)
        if prev and curr:
            data[f"{cur}_chg"] = ((curr - prev) / prev) * 100
        else:
            data[f"{cur}_chg"] = 0.0
        cache[prev_key] = data.get(key)

    print("[INFO] Fetching P2P rates...")
    binance_rate = fetch_binance_p2p()
    bybit_rate = fetch_bybit_p2p()

    # Use P2P as parallel rate proxy
    if binance_rate and bybit_rate:
        data["parallel"] = (binance_rate + bybit_rate) / 2
        data["binance"] = binance_rate
        data["bybit"] = bybit_rate
    elif binance_rate:
        data["parallel"] = binance_rate
        data["binance"] = binance_rate
        data["bybit"] = binance_rate
    else:
        data["parallel"] = cache.get("last_parallel", 1357)
        data["binance"] = data["parallel"]
        data["bybit"] = data["parallel"]

    data["usdt_p2p"] = data["parallel"]
    data["spread"] = data["parallel"] - data["cbn"]
    data["spread_pct"] = (data["spread"] / data["cbn"]) * 100 if data["cbn"] else 0

    # Wise rate
    wise = fetch_wise_rate()
    data["wise"] = wise if wise else data["cbn"] * 0.97

    print("[INFO] Fetching crypto...")
    crypto = fetch_crypto_prices()
    if crypto:
        data.update(crypto)
        cache["last_btc_usd"] = crypto.get("btc_usd")
        cache["last_eth_usd"] = crypto.get("eth_usd")
    else:
        data["btc_usd"] = cache.get("last_btc_usd", 64200)
        data["btc_chg"] = 0
        data["eth_usd"] = cache.get("last_eth_usd", 3100)
        data["eth_chg"] = 0
        data["bnb_usd"] = cache.get("last_bnb_usd", 412)
        data["bnb_chg"] = 0
        data["gold_usd"] = cache.get("last_gold_usd", 2330)
        data["gold_chg"] = 0

    print("[INFO] Fetching oil prices...")
    oil = fetch_oil_prices()
    if oil and oil.get("brent"):
        data.update(oil)
        cache["last_brent"] = oil["brent"]
    else:
        data["brent"] = cache.get("last_brent", 82.4)
        data["brent_chg"] = 0
        data["bonny"] = data["brent"] + 1.7
        data["bonny_chg"] = 0

    print("[INFO] Fetching global indices...")
    indices = fetch_global_indices()
    data.update(indices)
    # Fallbacks for global indices
    for k, v in [("sp500",5420),("ftse",7820),("dax",17650),("nikkei",38200),("dxy",104.2)]:
        if k not in data: data[k] = v
        if f"{k}_chg" not in data: data[f"{k}_chg"] = 0

    print("[INFO] Fetching African indices...")
    af_indices = fetch_african_indices()
    data.update(af_indices)
    for k, v in [("jse",73450),("egx",26800)]:
        if k not in data: data[k] = v
        if f"{k}_chg" not in data: data[f"{k}_chg"] = 0
    # NSE Kenya and GSE not on stooq — use cached/static
    data["nse_k"] = 198300
    data["nsek_chg"] = 0.7
    data["gse"] = 3420
    data["gse_chg"] = 0.2

    print("[INFO] Fetching commodities...")
    comms = fetch_commodities()
    data.update(comms)
    for k, v in [("silver_usd", 27.4), ("cocoa_usd", 9850)]:
        if k not in data: data[k] = v
        if f"{k[:-4]}_chg" not in data: data[f"{k[:-4]}_chg"] = 0

    # ── TIER 2: Daily scrapes (08:00 run only) ─────────────────────────────────
    if is_first_run_today:
        print("[INFO] Tier 2: Daily scrapes...")

        # Fuel prices
        fuel = fetch_fuel_prices(cache)
        if fuel:
            if "petrol" in fuel: cache["tier2"]["petrol"] = fuel["petrol"]
            if "diesel" in fuel: cache["tier2"]["diesel"] = fuel["diesel"]
            cache["tier2"]["fuel_date"] = today_str()
            reset_failure(cache, "fuel")
        else:
            increment_failure(cache, "fuel")
            if should_alert(cache, "fuel"):
                alerts.append("fuel prices scrape failed 3+ times")

        # NGX movers
        movers = fetch_ngx_movers(cache)
        if movers:
            cache["tier2"]["ngx_movers"] = movers
            cache["tier2"]["ngx_movers_date"] = today_str()
            cache["tier2"]["ngx_movers_available"] = True
            reset_failure(cache, "ngx_movers")
        else:
            cache["tier2"]["ngx_movers_available"] = False
            increment_failure(cache, "ngx_movers")

        # FX Reserves
        reserves = fetch_fx_reserves(cache)
        if reserves:
            cache["tier2"]["reserves"] = reserves
            cache["tier2"]["reserves_date"] = today_str()
            reset_failure(cache, "reserves")
        else:
            increment_failure(cache, "reserves")

    # ── Weekly tracking: update high/low ──────────────────────────────────────
    wt = cache.get("weekly_tracking", {})
    # Reset weekly tracking on Monday
    if is_monday and now.hour < 9:
        wt["usd_ngn_week_high"] = data["parallel"]
        wt["usd_ngn_week_low"] = data["parallel"]
        wt["btc_week_high"] = data.get("btc_usd", 0)
        wt["btc_week_low"] = data.get("btc_usd", 0)
        wt["week_start"] = today_str()
    else:
        p = data["parallel"]
        if p > wt.get("usd_ngn_week_high", 0): wt["usd_ngn_week_high"] = p
        if p < wt.get("usd_ngn_week_low", 999999): wt["usd_ngn_week_low"] = p
        btc = data.get("btc_usd", 0)
        if btc and btc > wt.get("btc_week_high", 0): wt["btc_week_high"] = btc
        if btc and btc < wt.get("btc_week_low", 999999): wt["btc_week_low"] = btc
    cache["weekly_tracking"] = wt
    data["usd_wk_hi"] = wt.get("usd_ngn_week_high", data["parallel"])
    data["usd_wk_lo"] = wt.get("usd_ngn_week_low", data["parallel"])
    data["btc_wk_hi"] = wt.get("btc_week_high", data.get("btc_usd", 0))
    data["btc_wk_lo"] = wt.get("btc_week_low", data.get("btc_usd", 0))

    # Pull from cache tiers
    t2 = cache.get("tier2", {})
    t3 = cache.get("tier3", {})
    t4 = cache.get("tier4", {})

    data["petrol"] = t2.get("petrol", 897)
    data["diesel"] = t2.get("diesel", 1450)
    data["lpg_kg"] = t2.get("lpg_kg", 1200)
    data["kerosene"] = t2.get("kerosene", 950)
    data["fuel_date"] = t2.get("fuel_date", "unknown")
    data["ngx"] = t2.get("ngx_index", 104520)
    data["ngx_chg"] = t2.get("ngx_change", 0.6)
    data["ngx_movers"] = t2.get("ngx_movers", [])
    data["ngx_movers_available"] = t2.get("ngx_movers_available", False)
    data["ngx_movers_date"] = t2.get("ngx_movers_date", "unknown")
    data["reserves"] = t2.get("reserves", 34.2)
    data["reserves_date"] = t2.get("reserves_date", "unknown")
    data["oil_production"] = t3.get("oil_production", 1.42)
    data["oil_production_date"] = t3.get("oil_production_date", "unknown")
    data["dangote_output"] = t3.get("dangote_output", 350)
    data["dangote_date"] = t3.get("dangote_date", "unknown")
    data["nnpc_import"] = t3.get("nnpc_import", 32.4)
    data["nnpc_date"] = t3.get("nnpc_date", "unknown")
    data["inflation"] = t4.get("inflation", 33.2)
    data["inflation_date"] = t4.get("inflation_date", "unknown")
    data["unemployment"] = t4.get("unemployment", 4.3)
    data["unemployment_date"] = t4.get("unemployment_date", "unknown")
    data["unemployment_note"] = t4.get("unemployment_note", "NBS methodology")
    data["poverty_rate"] = t4.get("poverty_rate", 40.1)
    data["poverty_date"] = t4.get("poverty_date", "2024")
    data["literacy_rate"] = t4.get("literacy_rate", 62.0)
    data["avg_income_formal"] = t4.get("avg_income_formal", 420000)
    data["avg_income_date"] = t4.get("avg_income_date", "2025")

    # Calculated fields
    rate = data["parallel"]
    data["litres_per_dollar"] = rate / data["petrol"] if data["petrol"] else 0
    data["tank_cost"] = 50 * data["petrol"]
    daily_wage = 4000
    data["tank_days"] = data["tank_cost"] / daily_wage
    data["tank_days_prev"] = (50 * 200) / daily_wage  # 1 year ago baseline

    # Salary erosion: ₦500k/month
    data["salary_ngn"] = 500000
    data["salary_usd_now"] = data["salary_ngn"] / rate if rate else 0
    data["salary_usd_then"] = data["salary_ngn"] / 910  # 1 year ago rate

    # Naira strength score (0-1, higher = stronger)
    # Based on spread pct: 0% = 1.0, 20%+ = 0.0
    spread_pct = data["spread_pct"]
    data["strength_score"] = max(0, min(1, 1 - (spread_pct / 20)))
    if spread_pct < 2: data["strength_label"] = "STRONG"
    elif spread_pct < 5: data["strength_label"] = "NEUTRAL"
    elif spread_pct < 10: data["strength_label"] = "BEARISH"
    else: data["strength_label"] = "CRISIS"

    # Year ago comparison
    data["yr_ago_rate"] = cache.get("yr_ago_rate", 910.0)
    data["yr_chg"] = ((rate - data["yr_ago_rate"]) / data["yr_ago_rate"]) * 100

    # Aza Index
    data["aza_components"] = calculate_aza_index(data)
    data["aza"] = data["aza_components"]["total"]

    # Update Aza history
    aza_hist = cache.get("aza_history", [])
    aza_dates = cache.get("aza_dates", [])
    last_date = aza_dates[-1] if aza_dates else ""
    today_label = now.strftime("Feb-%d").replace("-0", "-")
    if last_date != today_label:
        aza_hist.append(data["aza"])
        aza_dates.append(today_label)
        if len(aza_hist) > 30:
            aza_hist = aza_hist[-30:]
            aza_dates = aza_dates[-30:]
        cache["aza_history"] = aza_hist
        cache["aza_dates"] = aza_dates

    data["aza_hist"] = aza_hist[-7:]
    data["aza_dates_short"] = aza_dates[-7:]
    data["aza_chg"] = data["aza"] - aza_hist[-2] if len(aza_hist) >= 2 else 0

    # Store current values for next run comparison
    cache["last_parallel"] = data["parallel"]
    cache["last_cbn"] = data["cbn"]
    cache["last_eur_ngn"] = data.get("eur_ngn")
    cache["last_gbp_ngn"] = data.get("gbp_ngn")
    cache["last_cny_ngn"] = data.get("cny_ngn")
    cache["last_kes_ngn"] = data.get("kes_ngn")
    cache["last_ghs_ngn"] = data.get("ghs_ngn")
    cache["last_zar_ngn"] = data.get("zar_ngn")
    cache["last_egp_ngn"] = data.get("egp_ngn")
    cache["last_xof_ngn"] = data.get("xof_ngn")
    cache["last_btc_usd"] = data.get("btc_usd")
    cache["last_eth_usd"] = data.get("eth_usd")
    cache["last_bnb_usd"] = data.get("bnb_usd")
    cache["last_gold_usd"] = data.get("gold_usd")
    cache["last_brent"] = data.get("brent")
    cache["last_updated"] = now.isoformat()

    save_cache(cache)

    # Add post time
    data["post_time"] = now.strftime("%b %d, %Y  •  %H:%M WAT")
    data["post_time_short"] = now.strftime("%b %d, %Y")
    data["post_hour"] = now.strftime("%H:%M WAT")

    return data, alerts


def calculate_aza_index(data):
    """
    Aza Index: 5 weighted components → single 0-100 score
    """
    components = {}

    # 1. FX Stability (30%) — parallel/CBN spread
    spread = data.get("spread_pct", 5)
    if spread <= 2: fx_score = 100
    elif spread <= 5: fx_score = 70
    elif spread <= 10: fx_score = 40
    else: fx_score = 10
    components["fx"] = {"score": fx_score, "weight": 0.30, "label": "FX Stability"}

    # 2. Inflation Pressure (25%)
    inf = data.get("inflation", 33)
    if inf < 15: inf_score = 100
    elif inf < 20: inf_score = 75
    elif inf < 28: inf_score = 50
    elif inf < 35: inf_score = 25
    else: inf_score = 10
    components["inflation"] = {"score": inf_score, "weight": 0.25, "label": "Inflation"}

    # 3. Fuel Accessibility (20%) — litres per dollar
    lpd = data.get("litres_per_dollar", 1.5)
    benchmark = 2.5  # historical good period
    fuel_score = min(100, int((lpd / benchmark) * 100))
    components["fuel"] = {"score": fuel_score, "weight": 0.20, "label": "Fuel Access"}

    # 4. Crypto Premium (15%) — USDT P2P vs CBN
    p2p = data.get("usdt_p2p", 0)
    cbn = data.get("cbn", 1)
    crypto_premium = ((p2p - cbn) / cbn * 100) if cbn else 5
    if crypto_premium <= 1: crypto_score = 100
    elif crypto_premium <= 3: crypto_score = 75
    elif crypto_premium <= 6: crypto_score = 50
    else: crypto_score = 20
    components["crypto"] = {"score": crypto_score, "weight": 0.15, "label": "Crypto Conf."}

    # 5. Stock Momentum (10%) — NGX daily change as proxy (ideally 30-day)
    ngx_chg = data.get("ngx_chg", 0)
    if ngx_chg > 5: stock_score = 100
    elif ngx_chg > 0: stock_score = 70
    elif ngx_chg == 0: stock_score = 50
    elif ngx_chg > -5: stock_score = 30
    else: stock_score = 10
    components["stock"] = {"score": stock_score, "weight": 0.10, "label": "Stock Mkt"}

    total = sum(c["score"] * c["weight"] for c in components.values())
    total = round(total)

    return {
        "fx": components["fx"]["score"],
        "inflation": components["inflation"]["score"],
        "fuel": components["fuel"]["score"],
        "crypto": components["crypto"]["score"],
        "stock": components["stock"]["score"],
        "total": total,
        "components": components
    }
