"""
renderer.py — Generates all 4 AzaIndex images
Image 1: Live Markets
Image 2: Nigeria Economy
Image 3: Africa & Global Markets
Image 4: Aza Index
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675

# ── Palette ────────────────────────────────────────────────────────────────────
BG      = "#070D18"
CARD    = "#0D1520"
CARD2   = "#101A28"
CARD3   = "#0A1422"
GREEN   = "#00D48A"
RED     = "#FF3D5A"
YELLOW  = "#FFB300"
ORANGE  = "#FF7A00"
BLUE    = "#1D9BF0"
PURPLE  = "#8B5CF6"
WHITE   = "#EEF2FF"
LGRAY   = "#8899AA"
DGRAY   = "#445566"
BORDER  = "#172030"
TICKER  = "#060C16"
DIVIDER = "#131F30"

# ── Fonts ──────────────────────────────────────────────────────────────────────
LS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
LS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LM_B = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
LM_R = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

def f(path, size):
    return ImageFont.truetype(path, size)

# ── Drawing helpers ────────────────────────────────────────────────────────────

def card(draw, x, y, w, h, fill=CARD, border=BORDER, r=8):
    draw.rounded_rectangle([(x, y), (x+w, y+h)], radius=r,
                            fill=fill, outline=border, width=1)

def rt(draw, text, font, right_x, y, fill):
    draw.text((right_x - draw.textlength(text, font=font), y), text, font=font, fill=fill)

def ct(draw, text, font, cx, y, fill):
    draw.text((cx - int(draw.textlength(text, font=font) // 2), y), text, font=font, fill=fill)

def clamp(text, draw, font, max_width):
    if draw.textlength(text, font=font) <= max_width:
        return text
    while len(text) > 3:
        text = text[:-1]
        if draw.textlength(text + "…", font=font) <= max_width:
            return text + "…"
    return text

def cc(v):
    """Change colour"""
    if v is None: return LGRAY
    return GREEN if v >= 0 else RED

def cs(v, decimals=1):
    """Change string"""
    if v is None: return "N/A"
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow}{abs(v):.{decimals}f}%"

def ngn(v, dec=0):
    if v is None: return "N/A"
    if v >= 1e9: return f"₦{v/1e9:.2f}B"
    if v >= 1e6: return f"₦{v/1e6:.2f}M"
    if v >= 1e3: return f"₦{v:,.{dec}f}"
    return f"₦{v:.{dec}f}"

def grid(draw):
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill="#09111E", width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill="#09111E", width=1)

def section_label(draw, x, y, text, dot_color=BLUE, font_size=15):
    draw.ellipse([(x, y+6), (x+8, y+14)], fill=dot_color)
    draw.text((x+14, y+2), text.upper(), font=f(LS_B, font_size), fill=LGRAY)

def ticker_bar(draw, items):
    ty = H - 86
    draw.rectangle([(0, ty), (W, ty+28)], fill=TICKER)
    draw.line([(0, ty), (W, ty)], fill=BORDER, width=1)
    fTk = f(LM_R, 14)
    fTkB = f(LM_B, 14)
    tx = 12
    for label, change_val in items:
        cstr = f"  {cs(change_val)}" if change_val is not None else ""
        lw = draw.textlength(label, font=fTk)
        cw = draw.textlength(cstr, font=fTkB) if cstr else 0
        if tx + lw + cw + 24 > W:
            break
        draw.text((tx, ty+7), label, font=fTk, fill=LGRAY)
        tx += lw
        if cstr:
            draw.text((tx, ty+7), cstr, font=fTkB, fill=cc(change_val))
            tx += cw
        draw.text((tx+3, ty+7), "·", font=fTk, fill=DGRAY)
        tx += 18

def footer(draw, sources):
    fFt = f(LS_R, 12)
    draw.text((40, H-54), f"Sources: {sources}", font=fFt, fill="#506070")
    draw.text((40, H-35),
              "Posted 08:00 / 13:00 / 19:00 WAT  •  Not financial advice  •  "
              "Cached data shows last-updated date  •  @AzaIndex",
              font=fFt, fill="#405060")

def accent_bar(draw, color):
    draw.rectangle([(0, H-5), (W, H)], fill=color)

def page_header(draw, title, subtitle_tag, accent, post_time):
    draw.rectangle([(0, 0), (W, 5)], fill=accent)
    draw.text((40, 18), title, font=f(LS_B, 34), fill=WHITE)
    draw.text((40, 62), post_time, font=f(LS_R, 17), fill=LGRAY)
    rt(draw, "@AzaIndex", f(LS_B, 16), W-40, 22, BLUE)
    rt(draw, subtitle_tag, f(LS_B, 13), W-40, 46, LGRAY)
    draw.line([(40, 94), (W-40, 94)], fill=BORDER, width=1)

def speedometer(draw, cx, cy, radius, score_0to1, label, label_color):
    """Draw a speedometer gauge. score_0to1: 0=leftmost(bad), 1=rightmost(good)"""
    # Arc segments (coloured background)
    for angle in range(180, 0, -1):
        rad = math.radians(angle)
        progress = (180 - angle) / 180
        if progress < 0.25:
            arc_col = (200, 20, 50)
        elif progress < 0.5:
            arc_col = (180, 80, 0)
        elif progress < 0.75:
            arc_col = (160, 130, 0)
        else:
            arc_col = (0, 170, 80)
        x1 = cx + int((radius-10) * math.cos(rad))
        y1 = cy - int((radius-10) * math.sin(rad))
        x2 = cx + int(radius * math.cos(rad))
        y2 = cy - int(radius * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=arc_col, width=4)

    # Needle
    needle_angle = 180 - (score_0to1 * 180)
    rad_n = math.radians(needle_angle)
    nx = cx + int((radius - 16) * math.cos(rad_n))
    ny = cy - int((radius - 16) * math.sin(rad_n))
    draw.line([(cx, cy), (nx, ny)], fill=WHITE, width=4)
    draw.ellipse([(cx-7, cy-7), (cx+7, cy+7)], fill=WHITE, outline=BG, width=2)

    # Zone labels — placed BELOW arc as a row for readability
    fLbl = f(LS_B, 12)
    label_y = cy + 12
    draw.text((cx - radius - 4, label_y), "CRISIS", font=fLbl, fill=RED)
    draw.text((cx - radius//2 - 28, label_y - 28), "STRESS", font=fLbl, fill=ORANGE)
    rt(draw, "STRAIN", fLbl, cx + radius//2 + 28, label_y - 28, YELLOW)
    rt(draw, "STRONG", fLbl, cx + radius + 4, label_y, GREEN)


def progress_bar(draw, x, y, width, height, pct, color, bg="#0A1828", r=3):
    draw.rounded_rectangle([(x, y), (x+width, y+height)], radius=r, fill=bg)
    fw = max(r*2, int(width * pct))
    draw.rounded_rectangle([(x, y), (x+fw, y+height)], radius=r, fill=color)


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 1 — LIVE MARKETS
# ══════════════════════════════════════════════════════════════════════════════

def render_image1(data, out_path):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    grid(draw)
    page_header(draw, "NIGERIA LIVE MARKETS", "MARKETS  •  1 OF 4", GREEN, data["post_time"])

    PAD = 13
    TOP = 104
    ROW = 30

    # ── FX RATES CARD ──────────────────────────────────────────────────────
    CX, CY, CW, CH = 28, TOP, 295, 295
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "FX Rates", GREEN)
    fL = f(LS_R, 16); fV = f(LM_B, 17)
    rows = [
        ("CBN Official",  ngn(data["cbn"]),       WHITE),
        ("Parallel Mkt",  ngn(data["parallel"]),   YELLOW),
        ("USDT P2P",      ngn(data["usdt_p2p"]),   WHITE),
        ("Spread",        f"{ngn(data['spread'])} ({data['spread_pct']:.1f}%)", RED),
        ("EUR / NGN",     ngn(data.get("eur_ngn")), LGRAY),
        ("GBP / NGN",     ngn(data.get("gbp_ngn")), LGRAY),
        ("CNY / NGN",     ngn(data.get("cny_ngn")), LGRAY),
    ]
    for i, (lbl, val, col) in enumerate(rows):
        yy = CY + 42 + i * ROW
        draw.text((CX+PAD, yy), clamp(lbl, draw, fL, CW//2-PAD), font=fL, fill=LGRAY)
        rt(draw, clamp(val, draw, fV, CW//2-4), fV, CX+CW-PAD, yy, col)

    # Week hi/lo
    wy = CY + 262
    draw.line([(CX+PAD, wy), (CX+CW-PAD, wy)], fill=DIVIDER, width=1)
    fWk = f(LS_R, 13); fWkV = f(LM_B, 14)
    draw.text((CX+PAD, wy+6), "Wk:", font=fWk, fill=LGRAY)
    draw.text((CX+PAD+34, wy+6), f"Hi {ngn(data['usd_wk_hi'])}", font=fWkV, fill=RED)
    rt(draw, f"Lo {ngn(data['usd_wk_lo'])}", fWkV, CX+CW-PAD, wy+6, GREEN)

    # ── 1-YEAR CARD ────────────────────────────────────────────────────────
    CX2, CY2, CW2, CH2 = 28, TOP+305, 295, 75
    card(draw, CX2, CY2, CW2, CH2, fill=CARD2)
    section_label(draw, CX2+PAD, CY2+PAD, "1-Year USD/NGN", RED, 13)
    fY = f(LM_B, 19)
    draw.text((CX2+PAD, CY2+35), f"₦{data['yr_ago_rate']:,.0f}", font=fY, fill=LGRAY)
    draw.text((CX2+PAD+76, CY2+35), f"→  ₦{data['parallel']:,.0f}", font=fY, fill=RED)
    draw.text((CX2+PAD, CY2+58), f"▲{data['yr_chg']:.1f}% devaluation in 12 months", font=f(LS_R, 12), fill=RED)

    # ── CRYPTO IN NAIRA ────────────────────────────────────────────────────
    CX, CY, CW, CH = 335, TOP, 348, 295
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "Crypto in Naira", YELLOW)
    rate = data["usdt_p2p"]
    fC = f(LM_B, 17); fCg = f(LM_R, 15)
    crypto_rows = [
        ("BTC",  data.get("btc_usd", 0) * rate,  data.get("btc_chg")),
        ("ETH",  data.get("eth_usd", 0) * rate,  data.get("eth_chg")),
        ("BNB",  data.get("bnb_usd", 0) * rate,  data.get("bnb_chg")),
        ("USDT", rate,                             None),
        ("GOLD", data.get("gold_usd", 0) * rate,  data.get("gold_chg")),
    ]
    for i, (coin, price_ngn, chg) in enumerate(crypto_rows):
        yy = CY + 42 + i * ROW
        draw.text((CX+PAD, yy), coin, font=f(LM_B, 17), fill=WHITE)
        draw.text((CX+PAD+60, yy), clamp(ngn(price_ngn), draw, fC, CW-160), font=fC, fill=WHITE)
        if coin == "USDT":
            rt(draw, "stable", f(LM_R, 14), CX+CW-PAD, yy+2, LGRAY)
        else:
            rt(draw, cs(chg), fCg, CX+CW-PAD, yy+2, cc(chg))

    # USD prices below
    draw.line([(CX+PAD, CY+200), (CX+CW-PAD, CY+200)], fill=DIVIDER, width=1)
    fUs = f(LS_R, 13); fUsV = f(LM_B, 14)
    draw.text((CX+PAD, CY+206), "BTC USD:", font=fUs, fill=LGRAY)
    draw.text((CX+PAD+68, CY+206), f"${data.get('btc_usd',0):,}", font=fUsV, fill=WHITE)
    draw.text((CX+PAD, CY+224), "Wk Hi:", font=fUs, fill=LGRAY)
    draw.text((CX+PAD+50, CY+224), f"${data['btc_wk_hi']:,}", font=fUsV, fill=RED)
    draw.text((CX+PAD+185, CY+224), "Lo:", font=fUs, fill=LGRAY)
    draw.text((CX+PAD+205, CY+224), f"${data['btc_wk_lo']:,}", font=fUsV, fill=GREEN)
    draw.text((CX+PAD, CY+248), f"ETH: ${data.get('eth_usd',0):,}", font=fUsV, fill=LGRAY)
    rt(draw, f"GOLD: ${data.get('gold_usd',0):,}/oz", fUsV, CX+CW-PAD, CY+248, LGRAY)

    # ── ARB & REMITTANCE ───────────────────────────────────────────────────
    CX2, CY2, CW2, CH2 = 335, TOP+305, 348, 75
    card(draw, CX2, CY2, CW2, CH2, fill=CARD2)
    section_label(draw, CX2+PAD, CY2+PAD, "Arb & Remittance", YELLOW, 13)
    fAb = f(LM_B, 15)
    fAs = f(LS_R, 13)
    # Line 1: Binance vs Bybit with gap — guard None when one exchange fails
    b_rate   = data.get("binance") or data.get("parallel", 0)
    by_rate  = data.get("bybit")   or data.get("parallel", 0)
    arb_gap  = abs(by_rate - b_rate)
    draw.text((CX2+PAD, CY2+36),
              f"Binance {ngn(b_rate)}  Bybit {ngn(by_rate)}  Gap {ngn(arb_gap)}",
              font=fAb, fill=WHITE)
    # Line 2: Wise remittance
    wise_rate = data.get("wise") or data.get("parallel", 0)
    wise_diff = data["parallel"] - wise_rate
    draw.text((CX2+PAD, CY2+56),
              f"Wise rate: {ngn(wise_rate)}  •  Premium over Wise: {ngn(wise_diff)}",
              font=fAs, fill=YELLOW)

    # ── NAIRA STRENGTH SPEEDOMETER ─────────────────────────────────────────
    CX, CY, CW, CH = 695, TOP, 236, 180
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "Naira Strength", RED)
    cx_s = CX + CW//2
    cy_s = CY + 138
    radius = 68
    speedometer(draw, cx_s, cy_s, radius, data["strength_score"], data["strength_label"], RED)
    lc = {"STRONG": GREEN, "NEUTRAL": YELLOW, "BEARISH": RED, "CRISIS": RED}.get(data["strength_label"], RED)
    ct(draw, data["strength_label"], f(LS_B, 18), cx_s, cy_s + 14, lc)

    # ── NGN VS AFRICA ──────────────────────────────────────────────────────
    CX, CY, CW, CH = 695, TOP+190, 236, 190
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "NGN vs Africa", BLUE)
    fAf = f(LS_R, 14); fAfV = f(LM_B, 15); fAfC = f(LM_R, 13)
    af_rows = [
        ("KES — Kenya",    data.get("kes_ngn"), data.get("kes_chg")),
        ("GHS — Ghana",    data.get("ghs_ngn"), data.get("ghs_chg")),
        ("ZAR — S.Africa", data.get("zar_ngn"), data.get("zar_chg")),
        ("EGP — Egypt",    data.get("egp_ngn"), data.get("egp_chg")),
        ("XOF — W.Africa", data.get("xof_ngn"), data.get("xof_chg")),
    ]
    for i, (lbl, val, chg) in enumerate(af_rows):
        yy = CY + 40 + i * 28
        if i > 0:
            draw.line([(CX+PAD, yy-4), (CX+CW-PAD, yy-4)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy), clamp(lbl, draw, fAf, CW*0.54), font=fAf, fill=LGRAY)
        val_str = f"₦{val:.2f}" if val else "N/A"
        rt(draw, val_str, fAfV, CX+CW-PAD-52, yy, WHITE)
        rt(draw, cs(chg), fAfC, CX+CW-PAD, yy+1, cc(chg))

    # ── AZA INDEX TEASER ───────────────────────────────────────────────────
    CX, CY, CW, CH = 943, TOP, 229, 380
    card(draw, CX, CY, CW, CH, fill=CARD3, border="#1A2840")
    section_label(draw, CX+PAD, CY+PAD, "Aza Index", BLUE)
    aza = data["aza"]
    aza_chg = data["aza_chg"]
    fBig = f(LS_B, 64)
    sw = draw.textlength(str(aza), font=fBig)
    draw.text((CX+CW//2 - int(sw//2), CY+42), str(aza), font=fBig, fill=RED)
    ct(draw, "/100", f(LS_R, 16), CX+CW//2, CY+112, LGRAY)
    ac = data["strength_label"]
    lc2 = {"STRONG": GREEN, "NEUTRAL": YELLOW, "BEARISH": RED, "CRISIS": RED}.get(ac, RED)
    ct(draw, ac, f(LS_B, 18), CX+CW//2, CY+136, lc2)
    chg_str = f"▼{abs(aza_chg)} wk" if aza_chg < 0 else f"▲{aza_chg} wk"
    chg_col = GREEN if aza_chg >= 0 else RED
    ct(draw, chg_str, f(LS_R, 14), CX+CW//2, CY+162, chg_col)
    draw.line([(CX+PAD, CY+186), (CX+CW-PAD, CY+186)], fill=DIVIDER, width=1)

    # Mini component bars
    az = data["aza_components"]
    comps = [
        ("FX Stability",  az["fx"],       YELLOW),
        ("Inflation",     az["inflation"], RED),
        ("Fuel Access",   az["fuel"],      ORANGE),
        ("Crypto Conf.",  az["crypto"],    BLUE),
        ("Stock Mkt",     az["stock"],     GREEN),
    ]
    fCmp = f(LS_R, 12); fCmpV = f(LM_B, 13)
    for i, (lbl, score, col) in enumerate(comps):
        yy = CY + 196 + i * 32
        draw.text((CX+PAD, yy), lbl, font=fCmp, fill=LGRAY)
        rt(draw, str(score), fCmpV, CX+CW-PAD, yy, col)
        progress_bar(draw, CX+PAD, yy+16, CW-PAD*2, 6, score/100, col)

    draw.text((CX+PAD, CY+358), "Full breakdown → Image 4", font=f(LS_R, 11), fill=DGRAY)

    ticker_bar(draw, [
        (f"BTC ${data.get('btc_usd',0):,}", data.get("btc_chg")),
        (f"ETH ${data.get('eth_usd',0):,}", data.get("eth_chg")),
        (f"GOLD ${data.get('gold_usd',0):,}/oz", data.get("gold_chg")),
        (f"BRENT ${data.get('brent',0):.1f}/bbl", data.get("brent_chg")),
        (f"NGX {data.get('ngx',0):,}", data.get("ngx_chg")),
        (f"USD/NGN ₦{data['parallel']:,.0f}", None),
        (f"DXY {data.get('dxy',0)}", data.get("dxy_chg")),
        (f"S&P {data.get('sp500',0):,}", data.get("sp500_chg")),
    ])
    footer(draw, "ExchangeRate-API  •  CoinGecko  •  Binance P2P  •  Bybit P2P  •  Wise  •  EIA  •  Stooq")
    accent_bar(draw, GREEN)
    img.save(out_path, "PNG")
    print(f"[OK] Image 1 saved: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 2 — NIGERIA ECONOMY
# ══════════════════════════════════════════════════════════════════════════════

def render_image2(data, out_path):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    grid(draw)
    page_header(draw, "NIGERIA ECONOMY", "ECONOMY  •  2 OF 4", ORANGE, data["post_time"])

    PAD = 13
    TOP = 104

    # ── FUEL PRICES ────────────────────────────────────────────────────────
    CX, CY, CW, CH = 28, TOP, 258, 275
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "Fuel Prices", ORANGE)
    fL = f(LS_R, 15); fV = f(LM_B, 17); fD = f(LS_R, 12)
    fuel_rows = [
        ("Petrol (PMS)", f"₦{data['petrol']}/L",    data.get("fuel_date", "")),
        ("Diesel (AGO)", f"₦{data['diesel']}/L",    data.get("fuel_date", "")),
        ("Cooking Gas",  f"₦{data['lpg_kg']}/kg",   data.get("fuel_date", "")),
        ("Kerosene",     f"₦{data['kerosene']}/L",  data.get("fuel_date", "")),
    ]
    for i, (lbl, val, upd) in enumerate(fuel_rows):
        yy = CY + 42 + i * 58
        if i > 0:
            draw.line([(CX+PAD, yy-6), (CX+CW-PAD, yy-6)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy), lbl, font=fL, fill=LGRAY)
        rt(draw, val, fV, CX+CW-PAD, yy-2, YELLOW)
        draw.text((CX+PAD, yy+20), f"as of {upd}", font=fD, fill=DGRAY)

    # ── FUEL ACCESSIBILITY ─────────────────────────────────────────────────
    CX2, CY2, CW2, CH2 = 28, TOP+285, 258, 110
    card(draw, CX2, CY2, CW2, CH2, fill=CARD2)
    section_label(draw, CX2+PAD, CY2+PAD, "Fuel Accessibility", ORANGE, 13)
    fFa = f(LM_B, 18)
    fFas = f(LS_R, 13)
    fFax = f(LS_R, 12)
    petrol_v  = data.get("petrol", 0) or 0
    parallel_v = data.get("parallel", 0) or 0
    lpd       = data.get("litres_per_dollar", 0) or 0
    # Line 1: Naira price + dollar equivalent side by side
    draw.text((CX2+PAD, CY2+36), f"₦{petrol_v:,}/L", font=fFa, fill=WHITE)
    rt(draw, f"= {lpd:.2f}L per $1", f(LS_R, 13), CX2+CW2-PAD, CY2+42, LGRAY)
    # Line 2: Cost in Naira to fill tank
    tank_ngn = 50 * petrol_v
    draw.text((CX2+PAD, CY2+62), f"50L tank = ₦{tank_ngn:,}", font=fFas, fill=ORANGE)
    # Line 3: Days wages to fill tank
    draw.text((CX2+PAD, CY2+80), f"= {data.get('tank_days', 0):.1f} days wages  (was {data.get('tank_days_prev', 0):.1f})", font=fFax, fill=RED)

    # ── OIL PRICES ─────────────────────────────────────────────────────────
    CX, CY, CW, CH = 298, TOP, 310, 180
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "Oil Prices", YELLOW)
    fOl = f(LS_R, 16); fOlB = f(LM_B, 17); fOlC = f(LM_R, 14)
    oil_rows = [
        ("Brent Crude", f"${data.get('brent',0):.1f}/bbl", data.get("brent_chg")),
        ("Bonny Light", f"${data.get('bonny',0):.1f}/bbl", data.get("bonny_chg")),
        ("Premium",     f"+${(data.get('bonny',0)-data.get('brent',0)):.1f}/bbl", None),
    ]
    for i, (lbl, val, chg) in enumerate(oil_rows):
        yy = CY + 42 + i * 30
        draw.text((CX+PAD, yy), lbl, font=fOl, fill=LGRAY)
        rt(draw, val, fOlB, CX+CW-PAD-62, yy, WHITE if chg is None else cc(chg))
        if chg is not None:
            rt(draw, cs(chg), fOlC, CX+CW-PAD, yy+2, cc(chg))
    draw.line([(CX+PAD, CY+138), (CX+CW-PAD, CY+138)], fill=DIVIDER, width=1)
    fOp = f(LS_R, 14); fOpV = f(LM_B, 15)
    draw.text((CX+PAD, CY+144), "Nigeria output:", font=fOp, fill=LGRAY)
    rt(draw, f"{data.get('oil_production',0):.2f}M bpd", fOpV, CX+CW-PAD, CY+142, WHITE)
    draw.text((CX+PAD, CY+162), "OPEC quota:", font=fOp, fill=LGRAY)
    rt(draw, "1.50M bpd", fOpV, CX+CW-PAD, CY+160, LGRAY)

    # ── NNPC VS DANGOTE ────────────────────────────────────────────────────
    CX, CY, CW, CH = 298, TOP+190, 310, 195
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "NNPC vs Dangote", ORANGE)
    fDg = f(LS_B, 15); fDgV = f(LM_B, 16); fDgs = f(LS_R, 12)
    # Dangote box
    draw.rounded_rectangle([(CX+PAD, CY+38), (CX+CW-PAD, CY+100)],
                            radius=5, fill="#0A1E0E", outline="#1A3020", width=1)
    draw.text((CX+PAD+8, CY+44), "DANGOTE REFINERY", font=fDg, fill=GREEN)
    draw.text((CX+PAD+8, CY+62), f"{data.get('dangote_output',350):,}K bpd output", font=fDgV, fill=GREEN)
    draw.text((CX+PAD+8, CY+82), f"Cap: 650K bpd  •  as of {data.get('dangote_date','')}", font=fDgs, fill=LGRAY)
    # NNPC box
    draw.rounded_rectangle([(CX+PAD, CY+108), (CX+CW-PAD, CY+166)],
                            radius=5, fill="#1A0E0E", outline="#301818", width=1)
    draw.text((CX+PAD+8, CY+114), "NNPC IMPORTS", font=fDg, fill=RED)
    draw.text((CX+PAD+8, CY+132), f"${data.get('nnpc_import',32.4):.1f}B/yr est.", font=fDgV, fill=RED)
    draw.text((CX+PAD+8, CY+152), "Annual fuel import bill", font=fDgs, fill=LGRAY)
    # Supply bar — fully inside card with breathing room
    bar_y = CY + 174
    progress_bar(draw, CX+PAD, bar_y, CW-PAD*2, 10, 0.54, GREEN)
    draw.text((CX+PAD, bar_y+14), "Dangote 54%", font=f(LS_R, 11), fill=GREEN)
    rt(draw, "NNPC 46%", f(LS_R, 11), CX+CW-PAD, bar_y+14, RED)

    # ── NGX STOCK MARKET ───────────────────────────────────────────────────
    CX, CY, CW, CH = 620, TOP, 268, 185
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "NGX Stock Market", BLUE)
    fNx = f(LM_B, 30)
    draw.text((CX+PAD, CY+42), f"{data.get('ngx',0):,}", font=fNx, fill=WHITE)
    ngx_chg = data.get("ngx_chg", 0)
    draw.text((CX+PAD, CY+82), cs(ngx_chg), font=f(LM_B, 18), fill=cc(ngx_chg))
    rt(draw, "Today", f(LS_R, 14), CX+CW-PAD, CY+84, LGRAY)
    draw.line([(CX+PAD, CY+110), (CX+CW-PAD, CY+110)], fill=DIVIDER, width=1)

    # ── 52-week range bar ──────────────────────────────────────────────────
    ngx_now   = data.get("ngx", 104520)
    ngx_high  = data.get("ngx_52w_high", ngx_now)
    ngx_low   = data.get("ngx_52w_low",  ngx_now)
    ngx_days  = data.get("ngx_52w_days", 1)
    ngx_since = data.get("ngx_52w_since", "today")

    # Label: "52W Range" once we have enough data, else "Range since {date}"
    if ngx_days >= 30:
        range_label = "52W Range:"
    else:
        # Format date nicely e.g. "Since Feb-21"
        try:
            import datetime as _dt
            since_dt = _dt.datetime.strptime(ngx_since, "%Y-%m-%d")
            range_label = f"Since {since_dt.strftime('%b-%d')}:"
        except Exception:
            range_label = "Range:"

    fRng  = f(LS_R,  12)
    fRngV = f(LM_B,  12)
    fRngS = f(LS_R,  11)

    # Row 1: label + low — high
    draw.text((CX+PAD, CY+116), range_label, font=fRng, fill=LGRAY)
    low_str  = f"{ngx_low:,.0f}"
    high_str = f"{ngx_high:,.0f}"
    draw.text((CX+PAD, CY+130), low_str,  font=fRngV, fill=RED)
    rt(draw,              high_str, fRngV, CX+CW-PAD, CY+130, GREEN)

    # Row 2: range bar
    bar_x  = CX + PAD
    bar_y  = CY + 148
    bar_w  = CW - PAD * 2
    bar_h  = 6

    # Draw background track
    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)],
        radius=3, fill=DGRAY
    )

    # Current position marker — clamp between 0 and bar_w
    rng = ngx_high - ngx_low
    if rng > 0:
        pos_ratio = (ngx_now - ngx_low) / rng
    else:
        pos_ratio = 0.5
    pos_ratio = max(0.0, min(1.0, pos_ratio))

    # Draw filled portion up to current position
    filled_w = max(4, int(bar_w * pos_ratio))
    fill_col = GREEN if pos_ratio >= 0.5 else YELLOW
    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + filled_w, bar_y + bar_h)],
        radius=3, fill=fill_col
    )

    # Draw position dot
    dot_x = bar_x + filled_w
    draw.ellipse(
        [(dot_x - 4, bar_y - 2), (dot_x + 4, bar_y + bar_h + 2)],
        fill=WHITE, outline=BG, width=1
    )

    # Row 3: position label
    pct_pos = round(pos_ratio * 100)
    pos_label = f"Now: {pct_pos}% of range"
    draw.text((CX+PAD, CY+160), pos_label, font=fRngS, fill=LGRAY)

    # ── MACRO INDICATORS ───────────────────────────────────────────────────
    CX, CY, CW, CH = 620, TOP+195, 268, 185
    card(draw, CX, CY, CW, CH, fill=CARD2)
    section_label(draw, CX+PAD, CY+PAD, "Macro Indicators", LGRAY)
    fMc = f(LS_R, 15); fMcV = f(LM_B, 17); fMcD = f(LS_R, 12)
    macro_rows = [
        ("Inflation Rate",   f"{data.get('inflation',0):.1f}%",         RED,   data.get("inflation_date","")),
        ("FX Reserves",      f"${data.get('reserves',0):.1f}B",         WHITE, data.get("reserves_date","")),
        ("Oil Production",   f"{data.get('oil_production',0):.2f}M bpd",LGRAY, data.get("oil_production_date","")),
    ]
    for i, (lbl, val, col, upd) in enumerate(macro_rows):
        yy = CY + 40 + i * 52
        if i > 0:
            draw.line([(CX+PAD, yy-6), (CX+CW-PAD, yy-6)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy), lbl, font=fMc, fill=LGRAY)
        rt(draw, val, fMcV, CX+CW-PAD, yy-2, col)
        draw.text((CX+PAD, yy+20), f"as of {upd}", font=fMcD, fill=DGRAY)

    # ── SALARY EROSION ─────────────────────────────────────────────────────
    CX, CY, CW, CH = 900, TOP, 272, 185
    card(draw, CX, CY, CW, CH, fill=CARD3, border="#1A2840")
    section_label(draw, CX+PAD, CY+PAD, "Salary Erosion", RED)
    fSe = f(LS_R, 14); fSeV = f(LM_B, 20)
    draw.text((CX+PAD, CY+40), "₦500k/month in USD:", font=fSe, fill=LGRAY)
    draw.text((CX+PAD, CY+62), "Feb 2025:", font=fSe, fill=LGRAY)
    rt(draw, f"${data['salary_usd_then']:.0f}", fSeV, CX+CW-PAD, CY+58, GREEN)
    draw.text((CX+PAD, CY+92), "Feb 2026:", font=fSe, fill=LGRAY)
    rt(draw, f"${data['salary_usd_now']:.0f}", fSeV, CX+CW-PAD, CY+88, RED)
    loss = data["salary_usd_then"] - data["salary_usd_now"]
    loss_pct = (loss / data["salary_usd_then"]) * 100 if data["salary_usd_then"] else 0
    draw.line([(CX+PAD, CY+122), (CX+CW-PAD, CY+122)], fill=DIVIDER, width=1)
    draw.text((CX+PAD, CY+128), f"Lost ${loss:.0f} ({loss_pct:.0f}%) in USD value", font=f(LS_R, 13), fill=RED)
    draw.text((CX+PAD, CY+146), "Salary unchanged in Naira.", font=f(LS_R, 13), fill=LGRAY)
    draw.text((CX+PAD, CY+164), "Purchasing power fell ~33%.", font=f(LS_R, 13), fill=RED)

    # ── PURCHASING POWER ───────────────────────────────────────────────────
    CX, CY, CW, CH = 900, TOP+195, 272, 190
    card(draw, CX, CY, CW, CH, fill=CARD2)
    section_label(draw, CX+PAD, CY+PAD, "Purchasing Power", LGRAY)
    fPp = f(LS_R, 13); fPpV = f(LM_B, 13)
    draw.text((CX+PAD, CY+36), "What ₦5,000 buys today:", font=fPp, fill=LGRAY)
    # Accurate verified data:
    # Rice 1kg: was ~₦600 (2023), now ~₦2,500+ → ₦5k bought ~8kg, now ~2kg
    # Petrol: direct from live price. ₦5k ÷ pump price per litre
    # Indomie (noodles): was ₦150/pack, now ~₦400 → ₦5k bought 33, now 12
    # Data 1GB: was ₦200-300, now ~₦600-1000 → ₦5k bought ~20, now ~6
    petrol_litres_now  = 5000 / data['petrol'] if data['petrol'] else 0
    petrol_litres_2023 = 5000 / 200  # ₦200/L was 2023 price before subsidy removal
    pp_rows = [
        ("Rice (1kg)",    f"{petrol_litres_2023:.0f}kg", f"{5000/2500:.1f}kg"),
        ("Petrol",        f"{petrol_litres_2023:.0f}L",  f"{petrol_litres_now:.1f}L"),
        ("Indomie (pkt)", "33 packs",                     "12 packs"),
        ("Data (1GB)",    "16+ packs",                    "5–6 packs"),
    ]
    fPpL = f(LS_R, 12); fPpR = f(LM_B, 12)
    # Header row
    draw.text((CX+PAD+90, CY+54), "2023", font=f(LS_R, 11), fill=DGRAY)
    rt(draw, "Now", f(LS_R, 11), CX+CW-PAD, CY+54, DGRAY)
    for i, (lbl, old_v, new_v) in enumerate(pp_rows):
        yy = CY + 68 + i * 28
        draw.line([(CX+PAD, yy-4), (CX+CW-PAD, yy-4)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy+2), lbl, font=fPpL, fill=LGRAY)
        draw.text((CX+PAD+90, yy+2), old_v, font=fPpR, fill=LGRAY)
        rt(draw, new_v, fPpR, CX+CW-PAD, yy+2, RED)
    draw.text((CX+PAD, CY+CH-16), "vs pre-subsidy removal (Jun 2023)", font=f(LS_R, 11), fill=DGRAY)

    ticker_bar(draw, [
        (f"Petrol ₦{data['petrol']}/L", None),
        (f"Diesel ₦{data['diesel']}/L", None),
        (f"Gas ₦{data['lpg_kg']}/kg", None),
        (f"Brent ${data.get('brent',0):.1f}/bbl", data.get("brent_chg")),
        (f"NGX {data.get('ngx',0):,}", data.get("ngx_chg")),
        (f"Inflation {data.get('inflation',0):.1f}%", None),
        (f"Reserves ${data.get('reserves',0):.1f}B", None),
    ])
    footer(draw, "Nairametrics  •  Pricecheck.ng  •  CBN  •  NUPRC  •  NGX  •  EIA")
    accent_bar(draw, ORANGE)
    img.save(out_path, "PNG")
    print(f"[OK] Image 2 saved: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 3 — AFRICA & GLOBAL MARKETS
# ══════════════════════════════════════════════════════════════════════════════

def render_image3(data, out_path):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    grid(draw)
    page_header(draw, "AFRICA & GLOBAL MARKETS", "GLOBAL  •  3 OF 4", PURPLE, data["post_time"])

    PAD = 13
    TOP = 104
    ROW = 28

    # ── NGN VS AFRICA ──────────────────────────────────────────────────────
    CX, CY, CW, CH = 28, TOP, 260, 220
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "NGN vs Africa", BLUE)
    fAf = f(LS_R, 14); fAfV = f(LM_B, 15); fAfC = f(LM_R, 13)
    af = [
        ("KES — Kenya",    data.get("kes_ngn"), data.get("kes_chg")),
        ("GHS — Ghana",    data.get("ghs_ngn"), data.get("ghs_chg")),
        ("ZAR — S.Africa", data.get("zar_ngn"), data.get("zar_chg")),
        ("EGP — Egypt",    data.get("egp_ngn"), data.get("egp_chg")),
        ("XOF — W.Africa", data.get("xof_ngn"), data.get("xof_chg")),
    ]
    for i, (lbl, val, chg) in enumerate(af):
        yy = CY + 40 + i * ROW
        if i > 0:
            draw.line([(CX+PAD, yy-4), (CX+CW-PAD, yy-4)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy), clamp(lbl, draw, fAf, CW*0.55), font=fAf, fill=LGRAY)
        val_str = f"₦{val:.2f}" if val else "N/A"
        rt(draw, val_str, fAfV, CX+CW-PAD-50, yy, WHITE)
        rt(draw, cs(chg), fAfC, CX+CW-PAD, yy+1, cc(chg))

    # ── AFRICAN STOCK MARKETS ──────────────────────────────────────────────
    CX, CY, CW, CH = 28, TOP+230, 260, 150
    card(draw, CX, CY, CW, CH, fill=CARD2)
    section_label(draw, CX+PAD, CY+PAD, "African Stock Mkts", BLUE)
    fAs = f(LS_R, 14); fAsV = f(LM_B, 15); fAsC = f(LM_R, 13)
    afstocks = [
        ("NGX (Nigeria)",  data.get("ngx", 0),       data.get("ngx_chg")),
        ("JSE (S.Africa)", data.get("jse", 0),       data.get("jse_chg")),
        ("NSE (Kenya)",    data.get("nse_k", 0),     data.get("nsek_chg")),
        ("EGX (Egypt)",    data.get("egx", 0),       data.get("egx_chg")),
    ]
    for i, (lbl, val, chg) in enumerate(afstocks):
        yy = CY + 40 + i * 26
        draw.text((CX+PAD, yy), lbl, font=fAs, fill=LGRAY)
        rt(draw, f"{val:,}", fAsV, CX+CW-PAD-52, yy, WHITE)
        rt(draw, cs(chg), fAsC, CX+CW-PAD, yy+1, cc(chg))

    # ── COMMODITIES IN NAIRA ───────────────────────────────────────────────
    CX, CY, CW, CH = 300, TOP, 312, 195
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "Commodities in Naira", YELLOW)
    rate = data["usdt_p2p"]
    fCm = f(LS_R, 14); fCmV = f(LM_B, 16); fCmC = f(LM_R, 13); fCmS = f(LS_R, 12)
    comms = [
        ("Gold",   data.get("gold_usd", 0),  data.get("gold_chg"),  "/oz"),
        ("Silver", data.get("silver_usd", 0),data.get("silver_chg"), "/oz"),
        ("Brent",  data.get("brent", 0),     data.get("brent_chg"),  "/bbl"),
        ("Cocoa",  data.get("cocoa_usd", 0), data.get("cocoa_chg"),  "/ton"),
    ]
    for i, (lbl, usd, chg, unit) in enumerate(comms):
        yy = CY + 40 + i * ROW
        if i > 0:
            draw.line([(CX+PAD, yy-4), (CX+CW-PAD, yy-4)], fill=DIVIDER, width=1)
        ngn_price = usd * rate
        draw.text((CX+PAD, yy), lbl, font=fCm, fill=LGRAY)
        rt(draw, clamp(ngn(ngn_price)+unit, draw, fCmV, CW//2), fCmV, CX+CW-PAD-52, yy, WHITE)
        rt(draw, cs(chg), fCmC, CX+CW-PAD, yy+1, cc(chg))
        draw.text((CX+PAD, yy+16), f"${usd:,.1f}{unit}", font=fCmS, fill=DGRAY)

    # ── AFRICAN OIL OUTPUT ─────────────────────────────────────────────────
    CX, CY, CW, CH = 300, TOP+205, 312, 175
    card(draw, CX, CY, CW, CH, fill=CARD2)
    section_label(draw, CX+PAD, CY+PAD, "African Oil Output", ORANGE)
    fOi = f(LS_R, 14); fOiV = f(LM_B, 15)
    oil_producers = [
        ("Nigeria",  data.get("oil_production", 1.42), 0.3),
        ("Angola",   1.18, -0.1),
        ("Libya",    1.21, 0.8),
        ("Algeria",  0.98, 0.0),
    ]
    for i, (country, mbpd, chg) in enumerate(oil_producers):
        yy = CY + 40 + i * ROW
        if i > 0:
            draw.line([(CX+PAD, yy-4), (CX+CW-PAD, yy-4)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy), country, font=fOi, fill=LGRAY)
        rt(draw, f"{mbpd:.2f}M bpd", fOiV, CX+CW-PAD-52, yy, WHITE)
        rt(draw, cs(chg), f(LM_R, 13), CX+CW-PAD, yy+1, cc(chg))

    # ── GLOBAL INDICES ─────────────────────────────────────────────────────
    CX, CY, CW, CH = 624, TOP, 295, 220
    card(draw, CX, CY, CW, CH)
    section_label(draw, CX+PAD, CY+PAD, "Global Indices", PURPLE)
    fGl = f(LS_R, 14); fGlV = f(LM_B, 15); fGlC = f(LM_R, 13)
    indices = [
        ("S&P 500  (US)", data.get("sp500", 0),   data.get("sp500_chg")),
        ("FTSE 100 (UK)", data.get("ftse", 0),    data.get("ftse_chg")),
        ("DAX      (DE)", data.get("dax", 0),     data.get("dax_chg")),
        ("Nikkei   (JP)", data.get("nikkei", 0),  data.get("nikkei_chg")),
        ("DXY Dollar",    data.get("dxy", 0),     data.get("dxy_chg")),
    ]
    for i, (lbl, val, chg) in enumerate(indices):
        yy = CY + 40 + i * ROW
        if i > 0:
            draw.line([(CX+PAD, yy-4), (CX+CW-PAD, yy-4)], fill=DIVIDER, width=1)
        draw.text((CX+PAD, yy), lbl, font=fGl, fill=LGRAY)
        rt(draw, f"{val:,}", fGlV, CX+CW-PAD-52, yy, WHITE)
        rt(draw, cs(chg), fGlC, CX+CW-PAD, yy+1, cc(chg))
    draw.text((CX+PAD, CY+CH-38), "DXY rises = more Naira pressure.", font=f(LS_R, 13), fill=LGRAY)
    draw.text((CX+PAD, CY+CH-20), "Global sell-off = weaker Naira.", font=f(LS_R, 13), fill=RED)

    # ── COMMODITIES USD + NAIRA RANK ───────────────────────────────────────
    CX, CY, CW, CH = 624, TOP+230, 295, 150
    card(draw, CX, CY, CW, CH, fill=CARD2)
    section_label(draw, CX+PAD, CY+PAD, "Commodities (USD)", YELLOW)
    fCu = f(LS_R, 13); fCuV = f(LM_B, 14)
    cusd = [
        ("Gold",   f"${data.get('gold_usd',0):,}/oz",     data.get("gold_chg")),
        ("Silver", f"${data.get('silver_usd',0):.1f}/oz",  data.get("silver_chg")),
        ("Brent",  f"${data.get('brent',0):.1f}/bbl",      data.get("brent_chg")),
        ("Cocoa",  f"${data.get('cocoa_usd',0):,}/ton",    data.get("cocoa_chg")),
    ]
    for i, (lbl, val, chg) in enumerate(cusd):
        yy = CY + 38 + i * 25
        draw.text((CX+PAD, yy), lbl, font=fCu, fill=LGRAY)
        rt(draw, val, fCuV, CX+CW-PAD-52, yy, WHITE)
        rt(draw, cs(chg), f(LM_R, 12), CX+CW-PAD, yy+1, cc(chg))

    # ── NAIRA GLOBAL RANK ──────────────────────────────────────────────────
    CX, CY, CW, CH = 931, TOP, 241, 220
    card(draw, CX, CY, CW, CH, fill=CARD3, border="#1A2840")
    section_label(draw, CX+PAD, CY+PAD, "Naira Global Rank", BLUE)
    fNg = f(LS_R, 13); fNgV = f(LM_B, 15)
    draw.text((CX+PAD, CY+38), "Naira cost per 1 unit of:", font=fNg, fill=LGRAY)
    pairs = [
        ("vs USD", f"₦{data['parallel']:,.0f}"),
        ("vs EUR", ngn(data.get("eur_ngn"))),
        ("vs GBP", ngn(data.get("gbp_ngn"))),
        ("vs CNY", ngn(data.get("cny_ngn"))),
        ("vs ZAR", f"₦{data.get('zar_ngn',0):.1f}"),
    ]
    for i, (lbl, val) in enumerate(pairs):
        yy = CY + 58 + i * 26
        draw.text((CX+PAD, yy), lbl, font=fNg, fill=LGRAY)
        rt(draw, val, fNgV, CX+CW-PAD, yy-1, WHITE)
    draw.line([(CX+PAD, CY+196), (CX+CW-PAD, CY+196)], fill=DIVIDER, width=1)
    draw.text((CX+PAD, CY+200), "Among weakest African", font=f(LS_R, 12), fill=LGRAY)
    draw.text((CX+PAD, CY+214), "currencies vs USD (2024)", font=f(LS_R, 12), fill=LGRAY)

    # ── NIGERIA STATS ──────────────────────────────────────────────────────
    CX, CY, CW, CH = 931, TOP+230, 241, 150
    card(draw, CX, CY, CW, CH, fill=CARD2)
    section_label(draw, CX+PAD, CY+PAD, "Nigeria Stats", LGRAY)
    fNs = f(LS_R, 13); fNsV = f(LM_B, 14)
    ng_stats = [
        ("Population",    "220M+"),
        ("GDP (USD)",     "$477B"),
        ("Remittances/yr", "~$20B"),
        (f"Poverty ({data.get('poverty_date','2024')})",
         f"{data.get('poverty_rate',40.1):.0f}%  World Bank"),
        (f"Unemploy. ({data.get('unemployment_date','Q3 2025')})",
         f"{data.get('unemployment',4.3):.1f}%*"),
    ]
    for i, (lbl, val) in enumerate(ng_stats):
        yy = CY + 38 + i * 20
        draw.text((CX+PAD, yy), clamp(lbl, draw, fNs, CW*0.5), font=fNs, fill=LGRAY)
        rt(draw, clamp(val, draw, fNsV, CW*0.5-PAD), fNsV, CX+CW-PAD, yy-1, WHITE)
    draw.text((CX+PAD, CY+CH-18), "*NBS 2023 methodology", font=f(LS_R, 11), fill=DGRAY)

    ticker_bar(draw, [
        (f"S&P {data.get('sp500',0):,}", data.get("sp500_chg")),
        (f"FTSE {data.get('ftse',0):,}", data.get("ftse_chg")),
        (f"DAX {data.get('dax',0):,}", data.get("dax_chg")),
        (f"Nikkei {data.get('nikkei',0):,}", data.get("nikkei_chg")),
        (f"DXY {data.get('dxy',0)}", data.get("dxy_chg")),
        (f"Gold ${data.get('gold_usd',0):,}/oz", data.get("gold_chg")),
        (f"Cocoa ${data.get('cocoa_usd',0):,}/ton", data.get("cocoa_chg")),
    ])
    footer(draw, "Stooq  •  CoinGecko  •  MetalPriceAPI  •  ExchangeRate-API  •  World Bank (static)")
    accent_bar(draw, PURPLE)
    img.save(out_path, "PNG")
    print(f"[OK] Image 3 saved: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 4 — AZA INDEX
# ══════════════════════════════════════════════════════════════════════════════

def render_image4(data, out_path):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    grid(draw)
    page_header(draw, "AZA INDEX",
                "AZA INDEX  •  4 OF 4", BLUE,
                f"{data['post_time']}  •  Nigeria Economic Health Score")

    PAD = 14
    az = data["aza_components"]
    aza = data["aza"]
    aza_chg = data["aza_chg"]

    # ── LEFT: BIG SCORE + SPEEDOMETER + LEGEND + SPARKLINE ────────────────
    CX, CY, CW, CH = 28, 104, 376, 454
    card(draw, CX, CY, CW, CH, fill=CARD, border="#1A3050", r=10)

    # Score — more vertical breathing room
    fBig = f(LS_B, 108)
    sw = draw.textlength(str(aza), font=fBig)
    draw.text((CX+CW//2 - int(sw//2), CY+16), str(aza), font=fBig, fill=RED)
    ct(draw, "/100", f(LS_R, 20), CX+CW//2, CY+132, LGRAY)

    # Status badge
    strength = data["strength_label"]
    lc = {"STRONG": GREEN, "NEUTRAL": YELLOW, "BEARISH": RED, "CRISIS": RED}.get(strength, RED)
    fBadge = f(LS_B, 24)
    bw2 = draw.textlength(strength, font=fBadge) + 28
    bx2 = CX+CW//2 - int(bw2//2)
    by2 = CY + 160
    draw.rounded_rectangle([(bx2, by2), (bx2+bw2, by2+32)], radius=16, fill="#2A0A10", outline=lc, width=2)
    ct(draw, strength, fBadge, CX+CW//2, by2+4, lc)

    # Week change — only show if we have real history
    hist_len = len(data.get("aza_hist", []))
    if hist_len <= 1:
        chg_str = "First reading today"
        chg_col = LGRAY
    elif aza_chg < 0:
        chg_str = f"▼{abs(aza_chg)} pts from last week"
        chg_col = RED
    elif aza_chg > 0:
        chg_str = f"▲{aza_chg} pts from last week"
        chg_col = GREEN
    else:
        chg_str = "Unchanged from last week"
        chg_col = LGRAY
    ct(draw, chg_str, f(LS_R, 14), CX+CW//2, CY+202, chg_col)

    # Speedometer — no text on the arc at all
    cx_s = CX + CW//2
    cy_s = CY + 302
    radius = 82
    speedometer(draw, cx_s, cy_s, radius, data["strength_score"], strength, lc)

    # ── COLOUR LEGEND — 4 dots in a clean 2×2 grid below the gauge ─────────
    # Each dot matches the arc colour with its zone name beside it
    legend_items = [
        (RED,    "Crisis   0–24"),
        (ORANGE, "Stressed 25–49"),
        (YELLOW, "Strained 50–74"),
        (GREEN,  "Strong  75–100"),
    ]
    dot_r = 7
    leg_y_start = cy_s + 22
    leg_col_w = CW // 2 - PAD
    fLeg = f(LS_R, 13)
    for i, (dot_col, label) in enumerate(legend_items):
        col_i = i % 2
        row_i = i // 2
        lx = CX + PAD + col_i * leg_col_w
        ly = leg_y_start + row_i * 26
        draw.ellipse([(lx, ly+1), (lx+dot_r*2, ly+1+dot_r*2)], fill=dot_col)
        draw.text((lx + dot_r*2 + 6, ly), label, font=fLeg, fill=LGRAY)

    # 7-day sparkline — pushed down to use remaining space
    hist  = data.get("aza_hist", [])
    dates = data.get("aza_dates_short", [])
    sl_top = leg_y_start + 2*26 + 14
    ct(draw, "7-day trend", f(LS_R, 13), CX+CW//2, sl_top, LGRAY)

    if not hist:
        # First run — no history yet, show a message
        ct(draw, "Building history...", f(LS_R, 12), CX+CW//2, sl_top+30, DGRAY)
        ct(draw, "Updates 3× daily", f(LS_R, 11), CX+CW//2, sl_top+48, DGRAY)
    else:
        sl_x = CX+PAD+8; sl_y = sl_top+18; sl_w = CW-PAD*2-16; sl_h = 46
        mn_h = min(hist); mx_h = max(hist); rng_h = max(mx_h - mn_h, 1)
        bw_s = max(4, (sl_w // max(len(hist), 1)) - 4)
        for i, val in enumerate(hist):
            bh_s = int(((val - mn_h) / rng_h) * (sl_h - 10)) + 10
            bx_s = sl_x + i * (bw_s + 4)
            by_s = sl_y + sl_h - bh_s
            cb = RED if val < 25 else (ORANGE if val < 50 else (YELLOW if val < 75 else GREEN))
            draw.rectangle([(bx_s, by_s), (bx_s+bw_s, sl_y+sl_h)], fill=cb)
            ct(draw, str(val), f(LM_B, 11), bx_s+bw_s//2, by_s-15, WHITE)
            if i < len(dates):
                ct(draw, dates[i], f(LS_R, 9), bx_s+bw_s//2, sl_y+sl_h+4, DGRAY)

    # ── MID: COMPONENT BREAKDOWN ───────────────────────────────────────────
    CX, CY, CW, CH = 418, 104, 388, 290
    card(draw, CX, CY, CW, CH, fill=CARD2)
    draw.text((CX+PAD, CY+14), "COMPONENT BREAKDOWN", font=f(LS_B, 16), fill=LGRAY)
    draw.line([(CX+PAD, CY+36), (CX+CW-PAD, CY+36)], fill=DIVIDER, width=1)
    comps = [
        ("FX Stability",   az["fx"],       YELLOW, "30%", "Parallel/CBN spread"),
        ("Inflation",      az["inflation"], RED,    "25%", "NBS headline rate"),
        ("Fuel Access",    az["fuel"],      ORANGE, "20%", "Litres per $1"),
        ("Crypto Conf.",   az["crypto"],    BLUE,   "15%", "P2P premium over CBN"),
        ("Stock Momentum", az["stock"],     GREEN,  "10%", "NGX daily trend"),
    ]
    for i, (lbl, score, col, wt, note) in enumerate(comps):
        yy = CY + 48 + i * 48
        draw.text((CX+PAD, yy), lbl, font=f(LS_R, 16), fill=WHITE)
        draw.text((CX+PAD, yy+19), note, font=f(LS_R, 12), fill=DGRAY)
        rt(draw, wt, f(LS_R, 13), CX+CW-PAD-46, yy+2, LGRAY)
        rt(draw, str(score), f(LM_B, 18), CX+CW-PAD, yy-2, col)
        progress_bar(draw, CX+PAD, yy+34, CW-PAD*2, 7, score/100, col)

    # ── MID BOT: TODAY'S READINGS ──────────────────────────────────────────
    CX2, CY2, CW2, CH2 = 418, 404, 388, 158
    card(draw, CX2, CY2, CW2, CH2, fill=CARD3, border="#1A2840")
    draw.text((CX2+PAD, CY2+14), "TODAY'S READINGS", font=f(LS_B, 15), fill=LGRAY)
    draw.line([(CX2+PAD, CY2+34), (CX2+CW2-PAD, CY2+34)], fill=DIVIDER, width=1)
    readings = [
        ("Parallel/CBN spread",  f"{data.get('spread_pct',0):.1f}%",           YELLOW),
        ("Inflation rate",        f"{data.get('inflation',0):.1f}%",            RED),
        ("Fuel: litres per $1",   f"{data.get('litres_per_dollar',0):.2f}L",    ORANGE),
        ("USDT P2P premium",      f"{data.get('spread_pct',0):.1f}% over CBN",  BLUE),
        ("NGX momentum",          cs(data.get("ngx_chg")),                      cc(data.get("ngx_chg"))),
    ]
    for i, (lbl, val, col) in enumerate(readings):
        yy = CY2 + 44 + i * 23
        draw.text((CX2+PAD, yy), lbl, font=f(LS_R, 14), fill=LGRAY)
        rt(draw, val, f(LM_B, 15), CX2+CW2-PAD, yy-1, col)

    # ── RIGHT: SCORE INTERPRETATION ────────────────────────────────────────
    CX, CY, CW, CH = 820, 104, 352, 454
    card(draw, CX, CY, CW, CH, fill=CARD2)
    draw.text((CX+PAD, CY+14), "WHAT YOUR SCORE MEANS", font=f(LS_B, 15), fill=LGRAY)
    draw.line([(CX+PAD, CY+34), (CX+CW-PAD, CY+34)], fill=DIVIDER, width=1)

    zones = [
        (75, 100, "STRONG",   "#001E10", GREEN,
         "Economy breathing well.",
         "Naira stable, inflation low.",
         "Good time to save in Naira."),
        (50, 74,  "STRAINED", "#221A00", YELLOW,
         "Pressure building.",
         "Watch parallel rate closely.",
         "Dollar hedge advisable."),
        (25, 49,  "STRESSED", "#221000", ORANGE,
         "Everyday Nigerians feeling it.",
         "Wages eroding vs inflation.",
         "Act to protect savings now."),
        (0,  24,  "CRISIS",   "#220000", RED,
         "Emergency economic conditions.",
         "Severe purchasing power loss.",
         "Protect assets urgently."),
    ]

    # Determine active zone
    active = 3
    if aza >= 75: active = 0
    elif aza >= 50: active = 1
    elif aza >= 25: active = 2

    zone_h = 100
    zone_gap = 8
    for i, (lo, hi, label, bg, col, l1, l2, l3) in enumerate(zones):
        zy = CY + 42 + i * (zone_h + zone_gap)
        is_active = (i == active)
        z_fill = bg if is_active else CARD3
        z_border = col if is_active else DIVIDER
        draw.rounded_rectangle([(CX+PAD, zy), (CX+CW-PAD, zy+zone_h)],
                                radius=6, fill=z_fill, outline=z_border,
                                width=2 if is_active else 1)
        # Coloured left strip
        draw.rounded_rectangle([(CX+PAD, zy), (CX+PAD+4, zy+zone_h)],
                                radius=3, fill=col)
        draw.text((CX+PAD+12, zy+8), f"{lo}–{hi}", font=f(LS_R, 12), fill=col)
        draw.text((CX+PAD+55, zy+6), label, font=f(LS_B, 15),
                  fill=col if is_active else DGRAY)
        if is_active:
            rt(draw, "◀ NOW", f(LS_B, 12), CX+CW-PAD-8, zy+8, col)
        tc = LGRAY if is_active else DGRAY
        for j, line in enumerate([l1, l2, l3]):
            draw.text((CX+PAD+12, zy+28+j*20), line, font=f(LS_R, 12), fill=tc)

    ticker_bar(draw, [
        (f"Aza Index {aza}/100", None),
        (f"FX Stability {az['fx']}/100", None),
        (f"Inflation {az['inflation']}/100", None),
        (f"Fuel Access {az['fuel']}/100", None),
        (f"Crypto {az['crypto']}/100", None),
        (f"Stocks {az['stock']}/100", None),
    ])
    footer(draw, "All Aza Index components derived from live data — see Images 1–3 for raw data")
    accent_bar(draw, BLUE)
    img.save(out_path, "PNG")
    print(f"[OK] Image 4 saved: {out_path}")


def render_all(data, output_dir):
    """Render all 4 images to output_dir"""
    os.makedirs(output_dir, exist_ok=True)
    render_image1(data, os.path.join(output_dir, "img1_markets.png"))
    render_image2(data, os.path.join(output_dir, "img2_economy.png"))
    render_image3(data, os.path.join(output_dir, "img3_global.png"))
    render_image4(data, os.path.join(output_dir, "img4_aza.png"))
    return [
        os.path.join(output_dir, "img1_markets.png"),
        os.path.join(output_dir, "img2_economy.png"),
        os.path.join(output_dir, "img3_global.png"),
        os.path.join(output_dir, "img4_aza.png"),
    ]
