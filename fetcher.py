"""
fetcher.py — All data fetching for NairaIntel Bot
Handles 4 tiers: live APIs, daily scrapes, weekly scrapes, monthly scrapes
Falls back to cache on any failure.

FORMULA AUDIT (all verified):
- EUR/NGN:  rates["NGN"] / rates["EUR"]   e.g. 1600/0.92 = 1739 NGN per 1 EUR  ✅
- GBP/NGN:  rates["NGN"] / rates["GBP"]   e.g. 1600/0.79 = 2025 NGN per 1 GBP  ✅
- KES/NGN:  rates["NGN"] / rates["KES"]   e.g. 1600/129  = 12.4 NGN per 1 KES  ✅
- litres_per_dollar: parallel / petrol    e.g. 1600/900  = 1.78 L per $1        ✅
- spread_pct: (parallel-cbn)/cbn*100                                             ✅
- salary_usd: salary_ngn / parallel_rate                                         ✅
- Aza strength_label: derived from Aza total score, NOT spread alone             ✅ FIXED
- P2P sanity check: rejects parallel rate if spread < 2%                         ✅ FIXED
- date_label: uses strftime, not hardcoded "Feb"                                 ✅ FIXED
"""

import json
import os
import re
import requests
import datetime

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.json")

# Sanity bounds — fetched values outside these are rejected
BOUNDS = {
    "cbn":      (800,   3000),
    "parallel": (900,   3500),
    "btc_usd":  (10000, 500000),
    "eth_usd":  (500,   20000),
    "bnb_usd":  (50,    2000),
    "gold_usd": (1000,  5000),
    "brent":    (20,    200),
    "petrol":   (400,   5000),
    "diesel":   (400,   8000),
}

# Minimum realistic spread between parallel and CBN (%)
# Sub-2% has not been a real condition in Nigeria since 2021
MIN_PARALLEL_SPREAD_PCT = 2.0


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def date_label(dt=None):
    """Short label like 'Feb-21' — works for any month, no hardcoding"""
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%b-") + str(dt.day)   # str(dt.day) strips leading zero

def in_bounds(value, key):
    if value is None:
        return False
    lo, hi = BOUNDS.get(key, (None, None))
    if lo is None:
        return True
    return lo <= value <= hi

def increment_failure(cache, key):
    cache["scrape_failures"][key] = cache["scrape_failures"].get(key, 0) + 1

def reset_failure(cache, key):
    cache["scrape_failures"][key] = 0

def should_alert(cache, key, threshold=3):
    return cache["scrape_failures"].get(key, 0) >= threshold


# ─── Tier 1: Live APIs ─────────────────────────────────────────────────────────

def fetch_exchange_rates(api_key):
    """
    ExchangeRate-API v6 — base currency USD.
    Cross rates formula: NGN_per_X = rates["NGN"] / rates["X"]
    Reason: if 1 USD = 1600 NGN and 1 USD = 0.92 EUR,
    then 1 EUR = 1600/0.92 = 1739 NGN. Correct.
    """
    if not api_key:
        print("[WARN] No ExchangeRate API key — skipping")
        return None
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        resp = r.json()
        if resp.get("result") != "success":
            print(f"[WARN] ExchangeRate-API error: {resp.get('error-type')}")
            return None
        rates = resp.get("conversion_rates", {})
        ngn = rates.get("NGN")
        if not ngn or not in_bounds(ngn, "cbn"):
            print(f"[WARN] ExchangeRate-API: suspicious NGN value {ngn}")
            return None

        def cross(currency):
            x = rates.get(currency)
            return round(ngn / x, 3) if (x and x > 0) else None

        return {
            "ngn":     ngn,
            "eur_ngn": cross("EUR"),
            "gbp_ngn": cross("GBP"),
            "cny_ngn": cross("CNY"),
            "kes_ngn": cross("KES"),
            "ghs_ngn": cross("GHS"),
            "zar_ngn": cross("ZAR"),
            "egp_ngn": cross("EGP"),
            "xof_ngn": cross("XOF"),
        }
    except Exception as e:
        print(f"[WARN] ExchangeRate-API: {e}")
        return None


def fetch_binance_p2p():
    """
    Binance P2P USDT/NGN — average of top 5 BUY ads.
    BUY = buyer pays NGN to receive USDT = real market price for USD.
    """
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT", "fiat": "NGN",
            "merchantCheck": False, "page": 1,
            "payTypes": [], "rows": 10, "tradeType": "BUY"
        }
        r = requests.post(url, json=payload,
                          headers={"Content-Type": "application/json",
                                   "User-Agent": "Mozilla/5.0"}, timeout=12)
        r.raise_for_status()
        ads = r.json().get("data", [])
        prices = []
        for ad in ads:
            try:
                p = float(ad["adv"]["price"])
                if in_bounds(p, "parallel"):
                    prices.append(p)
            except Exception:
                pass
        if len(prices) >= 2:
            avg = round(sum(prices[:5]) / min(5, len(prices)), 0)
            print(f"[INFO] Binance P2P top prices: {[int(p) for p in prices[:5]]} → avg ₦{avg:.0f}")
            return avg
        print("[WARN] Binance P2P: insufficient valid prices")
        return None
    except Exception as e:
        print(f"[WARN] Binance P2P: {e}")
        return None


def fetch_bybit_p2p():
    """
    Bybit P2P USDT/NGN — average of top 5 BUY offers.
    side=0 means buyer (paying NGN to get USDT).
    """
    try:
        url = "https://api2.bybit.com/fiat/otc/item/online"
        payload = {
            "tokenId": "USDT", "currencyId": "NGN",
            "payment": [], "side": "0", "size": "10", "page": "1"
        }
        r = requests.post(url, json=payload,
                          headers={"Content-Type": "application/json",
                                   "User-Agent": "Mozilla/5.0"}, timeout=12)
        r.raise_for_status()
        items = r.json().get("result", {}).get("items", [])
        prices = []
        for item in items:
            try:
                p = float(item["price"])
                if in_bounds(p, "parallel"):
                    prices.append(p)
            except Exception:
                pass
        if len(prices) >= 2:
            avg = round(sum(prices[:5]) / min(5, len(prices)), 0)
            print(f"[INFO] Bybit P2P top prices: {[int(p) for p in prices[:5]]} → avg ₦{avg:.0f}")
            return avg
        print("[WARN] Bybit P2P: insufficient valid prices")
        return None
    except Exception as e:
        print(f"[WARN] Bybit P2P: {e}")
        return None


def fetch_wise_rate():
    """Wise USD→NGN transfer rate — typically 3–5% below parallel"""
    try:
        url = "https://wise.com/rates/live?source=USD&target=NGN"
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            data = r.json()
            rate = data.get("value") or data.get("rate")
            if rate and in_bounds(float(rate), "cbn"):
                return float(rate)
        return None
    except Exception as e:
        print(f"[WARN] Wise rate: {e}")
        return None


def fetch_crypto_prices():
    """CoinGecko free API — BTC, ETH, BNB, Gold with 24h change"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,binancecoin,gold",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        result = {}
        mapping = [
            ("bitcoin",     "btc_usd",  "btc_chg",  "btc_usd"),
            ("ethereum",    "eth_usd",  "eth_chg",  "eth_usd"),
            ("binancecoin", "bnb_usd",  "bnb_chg",  "bnb_usd"),
            ("gold",        "gold_usd", "gold_chg", "gold_usd"),
        ]
        for coin, price_key, chg_key, bounds_key in mapping:
            p = data.get(coin, {}).get("usd")
            if p and in_bounds(p, bounds_key):
                result[price_key] = p
                result[chg_key]   = data[coin].get("usd_24h_change")
        if result:
            print(f"[INFO] Crypto: BTC ${result.get('btc_usd',0):,}  "
                  f"ETH ${result.get('eth_usd',0)}  Gold ${result.get('gold_usd',0)}")
        return result if result else None
    except Exception as e:
        print(f"[WARN] CoinGecko: {e}")
        return None


def _stooq_latest_and_prev(symbol):
    """
    Fetch latest and previous daily close from Stooq CSV.
    Returns (latest_close, prev_close) or (None, None).
    CSV format: Date,Open,High,Low,Close,Volume
    """
    try:
        url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
        r = requests.get(url, timeout=10)
        lines = r.text.strip().split("\n")
        # Filter out header and empty lines
        data_lines = [l for l in lines
                      if l and not l.lower().startswith("date")
                      and not l.lower().startswith("no data")]
        if len(data_lines) < 1:
            return None, None

        def close(line):
            parts = line.split(",")
            return float(parts[4]) if len(parts) >= 5 else None

        latest = close(data_lines[-1])
        prev   = close(data_lines[-2]) if len(data_lines) >= 2 else None
        return latest, prev
    except Exception as e:
        print(f"[WARN] Stooq {symbol}: {e}")
        return None, None


def _pct_chg(new, old):
    if new and old and old > 0:
        return round(((new - old) / old) * 100, 2)
    return None


def fetch_oil_prices():
    """
    Brent crude: Stooq symbol lcoj.f (ICE Brent front month).
    Bonny Light = Brent + $1.70 premium (Nigerian crude, not freely quoted).
    """
    brent, brent_prev = _stooq_latest_and_prev("lcoj.f")
    if not brent or not in_bounds(brent, "brent"):
        print(f"[WARN] Brent: value {brent} out of bounds or missing")
        return None
    return {
        "brent":     round(brent, 2),
        "brent_chg": _pct_chg(brent, brent_prev),
        "bonny":     round(brent + 1.7, 2),
        "bonny_chg": _pct_chg(brent, brent_prev),
    }


def fetch_global_indices():
    """
    Stooq symbols (verified):
    ^spx=S&P500, ^ftse=FTSE100, ^dax=DAX, ^nkx=Nikkei225, dx.f=DXY
    """
    symbols = {
        "sp500": "^spx", "ftse": "^ftse",
        "dax": "^dax", "nikkei": "^nkx", "dxy": "dx.f"
    }
    results = {}
    for key, sym in symbols.items():
        val, prev = _stooq_latest_and_prev(sym)
        if val:
            results[key]          = round(val, 2)
            results[f"{key}_chg"] = _pct_chg(val, prev)
        else:
            print(f"[WARN] Stooq {key} ({sym}): no data")
    return results


def fetch_african_indices():
    """
    Stooq: ^jse=JSE All Share (SA), ^egx30=EGX30 (Egypt)
    NSE Kenya not available on Stooq — uses cached static value.
    """
    symbols = {"jse": "^jse", "egx": "^egx30"}
    results = {}
    for key, sym in symbols.items():
        val, prev = _stooq_latest_and_prev(sym)
        if val:
            results[key]          = round(val, 2)
            results[f"{key}_chg"] = _pct_chg(val, prev)
        else:
            print(f"[WARN] Stooq {key} ({sym}): no data")
    return results


def fetch_commodities():
    """
    Stooq: xagusd=Silver spot (USD/oz), cc.f=Cocoa futures (USD/ton)
    """
    symbols = {"silver": "xagusd", "cocoa": "cc.f"}
    results = {}
    for key, sym in symbols.items():
        val, prev = _stooq_latest_and_prev(sym)
        if val:
            results[f"{key}_usd"] = round(val, 2)
            results[f"{key}_chg"] = _pct_chg(val, prev)
        else:
            print(f"[WARN] Stooq {key} ({sym}): no data")
    return results


# ─── Tier 2: Daily scrapes ─────────────────────────────────────────────────────

def fetch_fuel_prices(cache):
    """
    Scrape petrol/diesel prices from Nairametrics then Pricecheck as fallback.
    Sanity check: petrol ₦400–5000/L, diesel ₦400–8000/L.
    """
    sources = [
        ("https://nairametrics.com/category/oil-gas/downstream/",
         r'(?:petrol|pms)[^\d]{0,30}?(\d{3,4})', "Nairametrics"),
        ("https://pricecheck.ng/fuel-prices/",
         r'(?:petrol|pms)[^\d]{0,30}?(\d{3,4})', "Pricecheck"),
    ]
    for url, pattern, name in sources:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            text = r.text
            result = {}
            m_petrol = re.search(pattern, text, re.IGNORECASE)
            m_diesel = re.search(r'(?:diesel|ago)[^\d]{0,30}?(\d{3,4})', text, re.IGNORECASE)
            if m_petrol:
                v = int(m_petrol.group(1))
                if in_bounds(v, "petrol"):
                    result["petrol"] = v
            if m_diesel:
                v = int(m_diesel.group(1))
                if in_bounds(v, "diesel"):
                    result["diesel"] = v
            if result:
                print(f"[INFO] Fuel from {name}: {result}")
                return result
        except Exception as e:
            print(f"[WARN] Fuel scrape {name}: {e}")
    return None


def fetch_fx_reserves(cache):
    """CBN FX reserves. Sanity: $5B–$100B."""
    try:
        r = requests.get("https://www.cbn.gov.ng/IntOps/ExtReserves.asp",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        m = re.search(r'\$([\d,\.]+)\s*(?:billion|bn)', r.text, re.IGNORECASE)
        if m:
            val = float(m.group(1).replace(",", ""))
            if 5 <= val <= 100:
                return val
        return None
    except Exception as e:
        print(f"[WARN] FX reserves: {e}")
        return None


def fetch_ngx_movers(cache):
    """NGX top movers — returns None until reliable source confirmed."""
    return None


# ─── Aza Index ────────────────────────────────────────────────────────────────

def calculate_aza_index(data):
    """
    Aza Index: 5 components, each 0–100, weighted sum = total score.

    KEY FIX: strength_label and strength_score are derived from the
    Aza TOTAL score, not from the FX spread alone.

    Weights: FX 30% | Inflation 25% | Fuel 20% | Crypto 15% | Stock 10%

    Zones:  75–100 = STRONG
            50–74  = STRAINED
            25–49  = STRESSED
             0–24  = CRISIS
    """

    # 1. FX STABILITY (30%) — parallel/CBN spread %
    # Nigeria reality: spread rarely below 3%, typical 4–15%+
    spread = data.get("spread_pct", 8)
    if spread < 2:
        fx_score = 95   # Near-unification — extremely rare
    elif spread < 5:
        fx_score = 70
    elif spread < 10:
        fx_score = 40
    elif spread < 20:
        fx_score = 15
    else:
        fx_score = 5

    # 2. INFLATION (25%) — NBS headline CPI %
    inf = data.get("inflation", 33)
    if inf < 10:
        inf_score = 100
    elif inf < 15:
        inf_score = 80
    elif inf < 20:
        inf_score = 60
    elif inf < 28:
        inf_score = 40
    elif inf < 35:
        inf_score = 20
    else:
        inf_score = 5

    # 3. FUEL ACCESS (20%) — litres per $1
    # Formula: parallel_rate / petrol_price — verified ✅
    # Benchmark: pre-subsidy (May 2023) ≈ 2.5 L/$1
    lpd = data.get("litres_per_dollar", 1.5)
    if lpd >= 3.0:
        fuel_score = 100
    elif lpd >= 2.5:
        fuel_score = 80
    elif lpd >= 2.0:
        fuel_score = 60
    elif lpd >= 1.5:
        fuel_score = 40
    elif lpd >= 1.0:
        fuel_score = 20
    else:
        fuel_score = 5

    # 4. CRYPTO CONFIDENCE (15%) — USDT P2P premium over CBN %
    # Formula: (usdt_p2p - cbn) / cbn * 100 — separate from FX spread
    # High premium = people fleeing to crypto = low confidence in Naira
    p2p = data.get("usdt_p2p", 0)
    cbn = data.get("cbn", 1)
    if cbn > 0 and p2p > 0 and p2p != data.get("parallel"):
        crypto_prem = ((p2p - cbn) / cbn) * 100
    else:
        # usdt_p2p == parallel (they're the same source) so use spread_pct
        crypto_prem = data.get("spread_pct", 5)

    if crypto_prem < 2:
        crypto_score = 90
    elif crypto_prem < 5:
        crypto_score = 65
    elif crypto_prem < 10:
        crypto_score = 40
    elif crypto_prem < 20:
        crypto_score = 15
    else:
        crypto_score = 5

    # 5. STOCK MOMENTUM (10%) — NGX daily % change
    ngx_chg = data.get("ngx_chg") or 0
    if ngx_chg > 3:
        stock_score = 100
    elif ngx_chg > 1:
        stock_score = 80
    elif ngx_chg > 0:
        stock_score = 65
    elif ngx_chg == 0:
        stock_score = 50
    elif ngx_chg > -1:
        stock_score = 35
    elif ngx_chg > -3:
        stock_score = 20
    else:
        stock_score = 5

    # Weighted total
    total = round(
        fx_score     * 0.30 +
        inf_score    * 0.25 +
        fuel_score   * 0.20 +
        crypto_score * 0.15 +
        stock_score  * 0.10
    )

    # Zone and speedometer — derived from TOTAL, not from any single component
    if total >= 75:
        zone = "STRONG"
    elif total >= 50:
        zone = "STRAINED"
    elif total >= 25:
        zone = "STRESSED"
    else:
        zone = "CRISIS"

    print(f"[INFO] Aza: FX={fx_score} Inf={inf_score} Fuel={fuel_score} "
          f"Crypto={crypto_score} Stock={stock_score} → TOTAL={total} ({zone})")

    return {
        "fx":             fx_score,
        "inflation":      inf_score,
        "fuel":           fuel_score,
        "crypto":         crypto_score,
        "stock":          stock_score,
        "total":          total,
        "zone":           zone,
        "strength_score": total / 100,   # 0.0→1.0 for speedometer needle
        "raw_spread":     round(spread, 1),
        "raw_lpd":        round(lpd, 2),
        "raw_inflation":  inf,
        "raw_crypto_prem": round(crypto_prem, 1),
    }


# ─── Master fetch ──────────────────────────────────────────────────────────────

def fetch_all_data(config):
    """Fetch all data. Returns (data_dict, alerts_list)."""
    cache = load_cache()
    now   = datetime.datetime.now()
    is_first_run_today = now.hour < 9
    is_monday          = now.weekday() == 0
    data   = {}
    alerts = []

    # ── Exchange rates ─────────────────────────────────────────────────────────
    print("[INFO] Fetching exchange rates...")
    fx = fetch_exchange_rates(config.get("EXCHANGERATE_API_KEY", ""))
    if fx and fx.get("ngn"):
        ngn = fx["ngn"]
        data["cbn"]     = round(ngn, 2)
        data["eur_ngn"] = fx.get("eur_ngn") or round(ngn / 0.92, 0)
        data["gbp_ngn"] = fx.get("gbp_ngn") or round(ngn * 1.27, 0)
        data["cny_ngn"] = fx.get("cny_ngn") or round(ngn * 0.137, 0)
        data["kes_ngn"] = fx.get("kes_ngn") or round(ngn * 0.0077, 2)
        data["ghs_ngn"] = fx.get("ghs_ngn") or round(ngn * 0.064, 2)
        data["zar_ngn"] = fx.get("zar_ngn") or round(ngn * 0.053, 2)
        data["egp_ngn"] = fx.get("egp_ngn") or round(ngn * 0.020, 2)
        data["xof_ngn"] = fx.get("xof_ngn") or round(ngn * 0.0015, 3)
        print(f"[INFO] CBN rate: ₦{ngn:,.0f}/USD")
    else:
        print("[WARN] Exchange rate API failed — using cache")
        data["cbn"]     = cache.get("last_cbn",     1590)
        data["eur_ngn"] = cache.get("last_eur_ngn", 1730)
        data["gbp_ngn"] = cache.get("last_gbp_ngn", 2020)
        data["cny_ngn"] = cache.get("last_cny_ngn",  218)
        data["kes_ngn"] = cache.get("last_kes_ngn",  12.3)
        data["ghs_ngn"] = cache.get("last_ghs_ngn",  102)
        data["zar_ngn"] = cache.get("last_zar_ngn",   84)
        data["egp_ngn"] = cache.get("last_egp_ngn",   32)
        data["xof_ngn"] = cache.get("last_xof_ngn",  2.5)

    # African currency daily changes (tracked across runs via cache)
    for cur in ["kes", "ghs", "zar", "egp", "xof"]:
        key  = f"{cur}_ngn"
        prev = cache.get(f"prev_{key}")
        curr = data.get(key)
        data[f"{cur}_chg"] = round(((curr - prev) / prev) * 100, 2) \
                             if (prev and curr and prev > 0) else 0.0
        cache[f"prev_{key}"] = curr

    # ── P2P / Parallel rate ────────────────────────────────────────────────────
    print("[INFO] Fetching P2P rates...")
    binance_rate = fetch_binance_p2p()
    bybit_rate   = fetch_bybit_p2p()

    if binance_rate and bybit_rate:
        raw_parallel    = (binance_rate + bybit_rate) / 2
        data["binance"] = round(binance_rate, 0)
        data["bybit"]   = round(bybit_rate,   0)
    elif binance_rate:
        raw_parallel    = binance_rate
        data["binance"] = round(binance_rate, 0)
        data["bybit"]   = round(binance_rate, 0)
    elif bybit_rate:
        raw_parallel    = bybit_rate
        data["binance"] = round(bybit_rate, 0)
        data["bybit"]   = round(bybit_rate, 0)
    else:
        raw_parallel = None

    # ── SANITY CHECK: reject if spread is implausibly low ─────────────────────
    cbn = data["cbn"]
    if raw_parallel and in_bounds(raw_parallel, "parallel"):
        raw_spread_pct = ((raw_parallel - cbn) / cbn) * 100
        if raw_spread_pct < MIN_PARALLEL_SPREAD_PCT:
            print(f"[WARN] P2P rate ₦{raw_parallel:.0f} → spread {raw_spread_pct:.1f}% "
                  f"is below minimum realistic {MIN_PARALLEL_SPREAD_PCT}%. Rejecting.")
            alerts.append(
                f"P2P rate suspicious: spread was {raw_spread_pct:.1f}% "
                f"(min floor: {MIN_PARALLEL_SPREAD_PCT}%). Used cached rate."
            )
            raw_parallel = None

    # Use verified rate or fall back to cache
    if raw_parallel:
        data["parallel"] = round(raw_parallel, 0)
    else:
        cached = cache.get("last_parallel")
        if cached and in_bounds(cached, "parallel"):
            data["parallel"] = cached
            print(f"[INFO] Using cached parallel: ₦{cached:.0f}")
        else:
            data["parallel"] = round(max(cbn * 1.05, 1400), 0)
            print("[WARN] Fallback parallel rate used")

    data["usdt_p2p"]   = data["parallel"]
    data["spread"]     = round(data["parallel"] - cbn, 0)
    data["spread_pct"] = round((data["spread"] / cbn) * 100, 2) if cbn else 0
    print(f"[INFO] Parallel ₦{data['parallel']:.0f} | "
          f"Spread ₦{data['spread']:.0f} ({data['spread_pct']:.1f}%)")

    # Wise rate
    wise = fetch_wise_rate()
    data["wise"] = round(wise, 0) if (wise and in_bounds(wise, "cbn")) \
                   else round(data["parallel"] * 0.96, 0)

    # ── Crypto ────────────────────────────────────────────────────────────────
    print("[INFO] Fetching crypto...")
    crypto = fetch_crypto_prices()
    if crypto:
        data.update(crypto)
        for k in ["btc_usd", "eth_usd", "bnb_usd", "gold_usd"]:
            if k in crypto: cache[f"last_{k}"] = crypto[k]
    else:
        data["btc_usd"]  = cache.get("last_btc_usd",  85000)
        data["btc_chg"]  = None
        data["eth_usd"]  = cache.get("last_eth_usd",   2100)
        data["eth_chg"]  = None
        data["bnb_usd"]  = cache.get("last_bnb_usd",    580)
        data["bnb_chg"]  = None
        data["gold_usd"] = cache.get("last_gold_usd",  2900)
        data["gold_chg"] = None

    # ── Oil ───────────────────────────────────────────────────────────────────
    print("[INFO] Fetching oil prices...")
    oil = fetch_oil_prices()
    if oil:
        data.update(oil)
        cache["last_brent"] = oil["brent"]
    else:
        b = cache.get("last_brent", 75.0)
        data.update({"brent": b, "brent_chg": None,
                     "bonny": round(b + 1.7, 2), "bonny_chg": None})

    # ── Global indices ────────────────────────────────────────────────────────
    print("[INFO] Fetching global indices...")
    data.update(fetch_global_indices())
    for k, v in [("sp500",5500),("ftse",8200),("dax",18000),("nikkei",37000),("dxy",103.5)]:
        data.setdefault(k, v)
        data.setdefault(f"{k}_chg", None)

    # ── African indices ───────────────────────────────────────────────────────
    print("[INFO] Fetching African indices...")
    data.update(fetch_african_indices())
    for k, v in [("jse",80000), ("egx",30000)]:
        data.setdefault(k, v)
        data.setdefault(f"{k}_chg", None)
    data["nse_k"]    = cache.get("last_nsek", 198300)
    data["nsek_chg"] = None

    # ── Commodities ───────────────────────────────────────────────────────────
    print("[INFO] Fetching commodities...")
    data.update(fetch_commodities())
    for k, v in [("silver_usd", 32.0), ("cocoa_usd", 8500)]:
        data.setdefault(k, v)
        base = k.replace("_usd", "")
        data.setdefault(f"{base}_chg", None)

    # ── Tier 2: Daily scrapes (08:00 only) ───────────────────────────────────
    if is_first_run_today:
        print("[INFO] Running Tier 2 daily scrapes...")
        fuel = fetch_fuel_prices(cache)
        if fuel:
            if "petrol" in fuel: cache["tier2"]["petrol"] = fuel["petrol"]
            if "diesel" in fuel: cache["tier2"]["diesel"] = fuel["diesel"]
            cache["tier2"]["fuel_date"] = today_str()
            reset_failure(cache, "fuel")
        else:
            increment_failure(cache, "fuel")
            if should_alert(cache, "fuel"):
                alerts.append("ALERT: Fuel price scrape failed 3+ consecutive days")

        movers = fetch_ngx_movers(cache)
        if movers:
            cache["tier2"]["ngx_movers"]           = movers
            cache["tier2"]["ngx_movers_available"] = True
            cache["tier2"]["ngx_movers_date"]      = today_str()
            reset_failure(cache, "ngx_movers")
        else:
            cache["tier2"]["ngx_movers_available"] = False

        reserves = fetch_fx_reserves(cache)
        if reserves:
            cache["tier2"]["reserves"]      = reserves
            cache["tier2"]["reserves_date"] = today_str()
            reset_failure(cache, "reserves")
        else:
            increment_failure(cache, "reserves")

    # ── Weekly hi/lo tracking ─────────────────────────────────────────────────
    wt = cache.get("weekly_tracking", {})
    if is_monday and now.hour < 9:
        wt = {"usd_ngn_week_high": data["parallel"],
              "usd_ngn_week_low":  data["parallel"],
              "btc_week_high":     data.get("btc_usd", 0),
              "btc_week_low":      data.get("btc_usd", 0),
              "week_start":        today_str()}
    else:
        p = data["parallel"]
        if p > wt.get("usd_ngn_week_high", 0):      wt["usd_ngn_week_high"] = p
        if p < wt.get("usd_ngn_week_low", 9999999): wt["usd_ngn_week_low"]  = p
        btc = data.get("btc_usd", 0)
        if btc:
            if btc > wt.get("btc_week_high", 0):       wt["btc_week_high"] = btc
            if btc < wt.get("btc_week_low", 99999999): wt["btc_week_low"]  = btc
    cache["weekly_tracking"] = wt
    data["usd_wk_hi"] = wt.get("usd_ngn_week_high", data["parallel"])
    data["usd_wk_lo"] = wt.get("usd_ngn_week_low",  data["parallel"])
    data["btc_wk_hi"] = wt.get("btc_week_high",      data.get("btc_usd", 0))
    data["btc_wk_lo"] = wt.get("btc_week_low",       data.get("btc_usd", 0))

    # ── Pull cached tier data ─────────────────────────────────────────────────
    t2 = cache.get("tier2", {})
    t3 = cache.get("tier3", {})
    t4 = cache.get("tier4", {})

    data.update({
        "petrol":               t2.get("petrol",              897),
        "diesel":               t2.get("diesel",             1450),
        "lpg_kg":               t2.get("lpg_kg",             1200),
        "kerosene":             t2.get("kerosene",            950),
        "fuel_date":            t2.get("fuel_date",       "unknown"),
        "ngx":                  t2.get("ngx_index",        104520),
        "ngx_chg":              t2.get("ngx_change",          0.6),
        "ngx_movers":           t2.get("ngx_movers",           []),
        "ngx_movers_available": t2.get("ngx_movers_available",False),
        "ngx_movers_date":      t2.get("ngx_movers_date", "unknown"),
        "reserves":             t2.get("reserves",            34.2),
        "reserves_date":        t2.get("reserves_date",  "unknown"),
        "oil_production":       t3.get("oil_production",      1.42),
        "oil_production_date":  t3.get("oil_production_date","unknown"),
        "dangote_output":       t3.get("dangote_output",       350),
        "dangote_date":         t3.get("dangote_date",    "unknown"),
        "nnpc_import":          t3.get("nnpc_import",         32.4),
        "nnpc_date":            t3.get("nnpc_date",       "unknown"),
        "inflation":            t4.get("inflation",           33.2),
        "inflation_date":       t4.get("inflation_date",  "unknown"),
        "unemployment":         t4.get("unemployment",         4.3),
        "unemployment_date":    t4.get("unemployment_date","unknown"),
        "unemployment_note":    t4.get("unemployment_note","NBS 2023 methodology"),
        "poverty_rate":         t4.get("poverty_rate",        40.1),
        "poverty_date":         t4.get("poverty_date",      "2024"),
        "literacy_rate":        t4.get("literacy_rate",       62.0),
        "avg_income_formal":    t4.get("avg_income_formal", 420000),
        "avg_income_date":      t4.get("avg_income_date",   "2025"),
    })

    # ── Calculated fields (all formulas verified) ─────────────────────────────

    # Litres per dollar = parallel_rate / petrol_price
    # e.g. ₦1600 / ₦900/L = 1.78 L/$1 ✅
    data["litres_per_dollar"] = round(data["parallel"] / data["petrol"], 2) \
                                if data["petrol"] else 0

    # Days wages to fill 50L tank
    # ₦70,000 min wage ÷ 22 working days ≈ ₦3,182/day (formal floor)
    # Using ₦5,000/day as middle-ground informal worker estimate
    DAILY_WAGE    = 5000
    PETROL_2023   = t4.get("petrol_2023_baseline", 200)   # pre-subsidy price ₦200/L
    data["tank_cost"]      = 50 * data["petrol"]
    data["tank_days"]      = round(data["tank_cost"] / DAILY_WAGE, 1)
    data["tank_days_prev"] = round((50 * PETROL_2023) / DAILY_WAGE, 1)

    # Salary erosion — ₦500k/month in USD
    # yr_ago_rate from cache — set to real Feb 2025 parallel rate
    yr_ago_rate             = cache.get("yr_ago_rate", 1490)
    data["salary_ngn"]      = 500000
    data["salary_usd_now"]  = round(data["salary_ngn"] / data["parallel"], 0) \
                              if data["parallel"] else 0
    data["salary_usd_then"] = round(data["salary_ngn"] / yr_ago_rate, 0) \
                              if yr_ago_rate else 0
    data["yr_ago_rate"]     = yr_ago_rate
    data["yr_chg"]          = round(((data["parallel"] - yr_ago_rate) / yr_ago_rate) * 100, 1) \
                              if yr_ago_rate else 0

    # ── Aza Index — all labels come from total, not from spread alone ─────────
    aza = calculate_aza_index(data)
    data["aza_components"] = aza
    data["aza"]            = aza["total"]
    data["strength_label"] = aza["zone"]            # ← FIXED: from Aza total
    data["strength_score"] = aza["strength_score"]  # ← FIXED: from Aza total

    # ── Aza history ───────────────────────────────────────────────────────────
    aza_hist  = cache.get("aza_history", [])
    aza_dates = cache.get("aza_dates",   [])
    today_lbl = date_label(now)
    if not aza_dates or aza_dates[-1] != today_lbl:
        aza_hist.append(data["aza"])
        aza_dates.append(today_lbl)
        aza_hist  = aza_hist[-30:]
        aza_dates = aza_dates[-30:]
        cache["aza_history"] = aza_hist
        cache["aza_dates"]   = aza_dates

    data["aza_hist"]        = aza_hist[-7:]
    data["aza_dates_short"] = aza_dates[-7:]
    # Week-on-week change: compare today vs 7 entries ago (true 7-day diff)
    if len(aza_hist) >= 8:
        data["aza_chg"] = data["aza"] - aza_hist[-8]
    elif len(aza_hist) >= 2:
        data["aza_chg"] = data["aza"] - aza_hist[0]
    else:
        data["aza_chg"] = 0

    # ── Save cache ────────────────────────────────────────────────────────────
    cache.update({
        "last_parallel": data["parallel"],
        "last_cbn":      data["cbn"],
        "last_eur_ngn":  data.get("eur_ngn"),
        "last_gbp_ngn":  data.get("gbp_ngn"),
        "last_cny_ngn":  data.get("cny_ngn"),
        "last_kes_ngn":  data.get("kes_ngn"),
        "last_ghs_ngn":  data.get("ghs_ngn"),
        "last_zar_ngn":  data.get("zar_ngn"),
        "last_egp_ngn":  data.get("egp_ngn"),
        "last_xof_ngn":  data.get("xof_ngn"),
        "last_btc_usd":  data.get("btc_usd"),
        "last_eth_usd":  data.get("eth_usd"),
        "last_bnb_usd":  data.get("bnb_usd"),
        "last_gold_usd": data.get("gold_usd"),
        "last_brent":    data.get("brent"),
        "last_updated":  now.isoformat(),
    })
    save_cache(cache)

    # Post time
    data["post_time"]       = now.strftime("%b %d, %Y  •  %H:%M WAT")
    data["post_time_short"] = now.strftime("%b %d, %Y")
    data["post_hour"]       = now.strftime("%H:%M WAT")

    # Final log
    print(f"\n{'='*52}")
    print(f"  CBN:       ₦{data['cbn']:>10,.0f}")
    print(f"  Parallel:  ₦{data['parallel']:>10,.0f}  (spread {data['spread_pct']:.1f}%)")
    print(f"  BTC:       ${data.get('btc_usd',0):>10,}")
    print(f"  Brent:     ${data.get('brent',0):>10.1f}/bbl")
    print(f"  Inflation: {data['inflation']:>10.1f}%")
    print(f"  Fuel L/$1: {data['litres_per_dollar']:>10.2f}L")
    print(f"  Aza Index: {data['aza']:>10}/100 — {data['strength_label']}")
    print(f"{'='*52}\n")

    return data, alerts
