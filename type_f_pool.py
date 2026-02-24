"""
type_f_pool.py — Type F institutional engagement posts for NairaIntel.

Strategy:
  - Mostly NAME-MENTIONS (no @tag) to avoid spam flags and keep posts credible
  - Selective @tagging ONLY when citing that institution's own published data
  - Written like sharp, informed commentary — not cheerleading
  - Live data anchors keep posts fresh every cycle
  - Rotates through 14-day window same as Type A

Slot: 12:00 WAT (new slot added to TEXT_POST_HOURS)
Also occasional inclusion at 17:00 WAT (alternating with Type B)

Accounts mapped:
  CBN         → @cenbank         (tag when citing MPR, reserves, official rate)
  NBS         → name-mention only (no verified handle confirmed)
  NNPC        → @nnpclimited      (tag when citing production/pump price data)
  FIRS        → @NigeriaRevenue   (tag when citing tax/revenue data)
  SEC Nigeria → @SECNigeria       (tag when citing NGX/capital market data)
  EFCC        → @officialEFCC     (tag when citing recovery figures)
  ICPC        → @icpcnigeria      (tag when citing corruption data)
  FMDQ        → @FMDQGroup        (tag when citing FX/bond market data)
  DMO         → @DMONigeria       (tag when citing debt figures)
  Nairametrics → @Nairametrics    (mention in media-bait posts)
  TechCabal   → @TechCabal        (mention in fintech posts)
  BusinessDay → @BusinessDayNg   (mention in economy posts)
  Stears      → @StearsData       (mention in data posts)
  Proshare    → @proshare         (mention in market posts)

Categories:
  cbn_policy      — CBN decisions, rates, monetary policy
  nnpc_oil        — NNPC, oil production, fuel supply
  efcc_recovery   — EFCC asset recovery, financial crime
  dmo_debt        — DMO, sovereign debt, T-bills
  firs_revenue    — FIRS, tax collection, fiscal
  sec_markets     — SEC, NGX, capital markets
  media_amplifier — Posts crafted to be cited/RT'd by financial media
  institutional   — Multi-institution accountability posts
  praise_milestone — Genuine milestone acknowledgments (RT bait)

Tag discipline:
  TAG  → used when the fact comes directly from that institution's data
  NAME → name mentioned but no @, for general commentary
"""

# ─── Account handles (confirmed) ─────────────────────────────────────────────
HANDLES = {
    "cbn":          "@cenbank",
    "nnpc":         "@nnpclimited",
    "firs":         "@NigeriaRevenue",
    "sec":          "@SECNigeria",
    "efcc":         "@officialEFCC",
    "icpc":         "@icpcnigeria",
    "fmdq":         "@FMDQGroup",
    "dmo":          "@DMONigeria",
    "nairametrics": "@Nairametrics",
    "techcabal":    "@TechCabal",
    "businessday":  "@BusinessDayNg",
    "stears":       "@StearsData",
    "proshare":     "@proshare",
}

# ─── Type F Fact Pool ─────────────────────────────────────────────────────────
# Format matches facts_pool.py: text template + placeholders + category
# "tag" field: True = include @handle in post. False = name-mention only.
# Keep ALL posts under ~240 chars to leave room for NairaIntel tag.

TYPE_F_FACTS = [

    # ══ CBN / MONETARY POLICY ══════════════════════════════════════════════

    {
        "text": "The Central Bank raised interest rates 9 times between 2022 and 2024 — from 11.5% to 27.5%.\n\nInflation today: {inflation}%\n\nHigher rates alone can't fix a supply-side inflation problem.\n\n{cbn_tag} 🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "cbn_policy",
        "tag": "cbn",
        "note": "TAG — citing CBN's own MPR decisions"
    },
    {
        "text": "The CBN's official exchange rate today: ₦{cbn}/$1.\nParallel market: ₦{parallel}/$1.\nSpread: {spread_pct:.1f}%\n\nThe Central Bank of Nigeria has narrowed the gap significantly since the 2023 float — but the gap persists.\n\n🏦 NairaIntel",
        "placeholders": ["cbn", "parallel", "spread_pct"],
        "category": "cbn_policy",
        "tag": None,
        "note": "NAME — general CBN commentary, no need to tag"
    },
    {
        "text": "Central Bank of Nigeria FX reserves: ${reserves:.1f}B\n\nPeak was $62B in 2008.\nToday: ${reserves:.1f}B\n\nReserves have held relatively stable — but at ₦{parallel}/$1, the naira still reflects structural FX pressure, not a reserves problem.\n\n{cbn_tag} 🏦 NairaIntel",
        "placeholders": ["reserves", "parallel"],
        "category": "cbn_policy",
        "tag": "cbn",
        "note": "TAG — citing CBN-published reserves figure"
    },
    {
        "text": "The Central Bank of Nigeria introduced the BDC ban in 2021, reversed it in 2023, floated the naira, and is now managing a {spread_pct:.1f}% parallel market spread.\n\nMonetary policy in a volatile economy requires constant recalibration.\n\n$1 = ₦{parallel} today.\n\n🏦 NairaIntel",
        "placeholders": ["parallel", "spread_pct"],
        "category": "cbn_policy",
        "tag": None,
        "note": "NAME — historical commentary, no tag needed"
    },
    {
        "text": "Governor Cardoso has overseen 850+ basis points of rate hikes since taking office in 2023.\n\nMPR today: 27.5%\nInflation: {inflation}%\n\nReal rate: {tbill_real:.1f}%\n\nThe tightening cycle may finally be working — food inflation is showing early signs of easing.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "cbn_policy",
        "tag": None,
        "note": "NAME — individual mention, no tag"
    },

    # ══ NNPC / OIL & FUEL ══════════════════════════════════════════════════

    {
        "text": "Nigeria produces ~1.4M barrels of oil per day.\n\nAt ${brent:.0f}/barrel, that is roughly ${daily_oil_rev:.0f}M/day in potential gross revenue.\n\nYet petrol at the pump is ₦{petrol}/L.\n\nThe gap between oil producer and fuel consumer is one of Nigeria's sharpest contradictions.\n\n{nnpc_tag} 🛢 NairaIntel",
        "placeholders": ["brent", "petrol"],
        "category": "nnpc_oil",
        "tag": "nnpc",
        "note": "TAG — citing NNPC production data"
    },
    {
        "text": "NNPC Limited became a commercial entity in 2022 — no longer a government agency.\n\nMeant to attract investment and accountability.\n\nOil output: ~1.4M bpd vs 2.4M bpd peak in 2010.\n\nThe structure changed. The results are pending.\n\n🛢 NairaIntel",
        "placeholders": [],
        "category": "nnpc_oil",
        "tag": None,
        "note": "NAME — general NNPC commentary"
    },
    {
        "text": "Dangote Refinery (650k bpd) + NNPC domestic mandate = no more petrol imports — in theory.\n\nAt full capacity, pump prices like ₦{petrol}/L could stabilise.\n\nUntil then, every import litre costs ₦{parallel} per dollar.\n\n{nnpc_tag} 🛢 NairaIntel",
        "placeholders": ["petrol", "parallel"],
        "category": "nnpc_oil",
        "tag": "nnpc",
        "note": "TAG — citing NNPC's mandate"
    },
    {
        "text": "Nigeria flares billions in gas value annually.\n\nThat wasted energy could power homes and factories.\n\nThe end-flaring pledge has been made multiple times.\n\nLPG today: ₦{lpg_kg}/kg — the market price for gas being burned off offshore.\n\n🔥 NairaIntel",
        "placeholders": ["lpg_kg"],
        "category": "nnpc_oil",
        "tag": None,
        "note": "NAME — accountability commentary, no tag"
    },

    # ══ EFCC / FINANCIAL CRIME ══════════════════════════════════════════════

    {
        "text": "The EFCC recovered over $1.2B in assets between 2015 and 2023.\n\nAt ₦{parallel}/$1 that is ₦{efcc_recovery_ngn:.1f} trillion in naira terms.\n\nFinancial crime recovery matters — but capital flight and illicit flows still cost Nigeria far more annually.\n\n{efcc_tag} 💰 NairaIntel",
        "placeholders": ["parallel"],
        "category": "efcc_recovery",
        "tag": "efcc",
        "note": "TAG — citing EFCC's own published recovery figures"
    },
    {
        "text": "The EFCC has prosecuted thousands of cases and recovered hundreds of billions since 2003.\n\nYet Nigeria's corruption perception index has barely moved in 20 years.\n\nEnforcement is necessary. Systemic change is slower.\n\n⚖️ NairaIntel",
        "placeholders": [],
        "category": "efcc_recovery",
        "tag": None,
        "note": "NAME — general commentary, no tag"
    },
    {
        "text": "Every $1 of illicit financial flow out of Nigeria costs the country ₦{parallel} in lost FX.\n\nThe African Union estimates Africa loses $88B/year to illicit flows.\n\nNigeria accounts for a significant share.\n\nWhat the EFCC recovers is a fraction of what leaves.\n\n💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "efcc_recovery",
        "tag": None,
        "note": "NAME — broad commentary"
    },
    {
        "text": "{efcc_tag} has arraigned dozens of bureau de change operators for FX manipulation since the naira float.\n\nThe parallel rate today: ₦{parallel}/$1.\nCBN official: ₦{cbn}/$1.\n\nEnforcement alone won't close a {spread_pct:.0f}% spread rooted in structural FX scarcity.\n\n⚖️ NairaIntel",
        "placeholders": ["parallel", "cbn", "spread_pct"],
        "category": "efcc_recovery",
        "tag": "efcc",
        "note": "TAG — EFCC action directly cited"
    },

    # ══ DMO / SOVEREIGN DEBT ══════════════════════════════════════════════

    {
        "text": "Nigeria's external debt: $42.3B\n\nAt ₦{parallel}/$1 that is ₦{external_debt_ngn:.1f} trillion.\n\nEvery time the naira falls ₦100, the naira cost of that debt rises by ~₦4.2 trillion — without borrowing a single dollar more.\n\n{dmo_tag} 💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "dmo_debt",
        "tag": "dmo",
        "note": "TAG — citing DMO-published debt figure"
    },
    {
        "text": "The Debt Management Office currently offers 91-day T-bills at ~20% per annum.\n\nInflation: {inflation}%\n\nReal return: {tbill_real:.1f}%\n\nFor the first time in years, T-Bills are barely beating inflation. A narrow window for naira savers.\n\n{dmo_tag} 💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "dmo_debt",
        "tag": "dmo",
        "note": "TAG — citing DMO T-bill rates"
    },
    {
        "text": "Nigeria's debt service-to-revenue ratio was over 90% in 2023.\n\nThe Debt Management Office is actively working to restructure the profile — moving from short-term to longer-dated instruments.\n\nAt {inflation}% inflation, the cost of rolling debt stays high.\n\n💸 NairaIntel",
        "placeholders": ["inflation"],
        "category": "dmo_debt",
        "tag": None,
        "note": "NAME — general DMO commentary"
    },

    # ══ FIRS / TAX & REVENUE ══════════════════════════════════════════════

    {
        "text": "Nigeria's tax-to-GDP ratio: ~10%.\nSub-Saharan Africa average: ~15%.\nOECD average: ~34%.\n\nThe Federal Inland Revenue Service collected ₦19.4 trillion in 2023 — a record.\n\nBut with 77% of Nigerians in the informal sector, the tax base remains narrow.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": [],
        "category": "firs_revenue",
        "tag": "firs",
        "note": "TAG — citing FIRS collection data"
    },
    {
        "text": "Nigeria earns more from taxes than oil for the first time in recent history.\n\nFIRS revenue exceeded NNPC remittances in 2023.\n\nA structural shift — but at {inflation}% inflation, the real value of tax revenue is eroding.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "firs_revenue",
        "tag": None,
        "note": "NAME — general FIRS commentary"
    },
    {
        "text": "The Federal Inland Revenue Service targets ₦34.5 trillion in tax revenue for 2025.\n\nThat is roughly $22B at today's rate of ₦{parallel}/$1.\n\nFor context: Nigeria's entire 2024 budget was ~$30B.\n\nTax reform is the next frontier.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": ["parallel"],
        "category": "firs_revenue",
        "tag": "firs",
        "note": "TAG — citing FIRS target"
    },

    # ══ SEC / CAPITAL MARKETS ══════════════════════════════════════════════

    {
        "text": "NGX All-Share Index: {ngx:,}\n\nMarket cap: ₦500B in 2000 → ₦60 trillion+ today.\n\nIn USD terms, the gain is much smaller — naira devaluation erodes dollar returns.\n\nSEC has pushed reforms to attract foreign capital back.\n\n{sec_tag} 📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "sec_markets",
        "tag": "sec",
        "note": "TAG — citing SEC's market development mandate"
    },
    {
        "text": "Foreign investors fled Nigerian equities when the naira was under managed float.\n\nSince the 2023 float, foreign portfolio inflows to NGX have gradually returned.\n\nNGX today: {ngx:,} | $1 = ₦{parallel}\n\nFX predictability is the price of foreign capital.\n\n📈 NairaIntel",
        "placeholders": ["ngx", "parallel"],
        "category": "sec_markets",
        "tag": None,
        "note": "NAME — general SEC/NGX commentary"
    },

    # ══ FMDQ / FX MARKET ══════════════════════════════════════════════════

    {
        "text": "The FMDQ Exchange is where Nigeria's official FX rates are set — through Willing Buyer Willing Seller transactions.\n\nToday's FMDQ rate: ₦{cbn}/$1\nParallel: ₦{parallel}/$1\nSpread: {spread_pct:.1f}%\n\nA {spread_pct:.0f}% gap means the official market still doesn't fully clear FX demand.\n\n{fmdq_tag} 📊 NairaIntel",
        "placeholders": ["cbn", "parallel", "spread_pct"],
        "category": "cbn_policy",
        "tag": "fmdq",
        "note": "TAG — FMDQ sets official FX rate, direct citation"
    },
    {
        "text": "Nigeria's fixed income market — T-bills, FGN bonds, commercial paper — is managed through the FMDQ Exchange.\n\nT-bill yield: ~20%\nInflation: {inflation}%\nReal yield: {tbill_real:.1f}%\n\nFor institutional investors, Nigeria's debt market is now among the highest-yielding in Africa.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "dmo_debt",
        "tag": None,
        "note": "NAME — FMDQ general commentary"
    },

    # ══ MEDIA AMPLIFIER POSTS (designed to be cited/shared by financial media) ══

    {
        "text": "NairaIntel data summary — {yr}:\n\n💵 $1 = ₦{parallel}\n⛽ Petrol: ₦{petrol}/L\n📈 Inflation: {inflation}%\n📊 NGX: {ngx:,}\n🥇 Gold: ${gold_usd:,}/oz\n\nData updated live. Track the numbers that matter.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "petrol", "inflation", "ngx"],
        "category": "media_amplifier",
        "tag": None,
        "note": "No tag — data summary for media to cite"
    },
    {
        "text": "Three numbers that define Nigeria's economy right now:\n\n1. ₦{parallel} — what $1 costs in the parallel market\n2. {inflation}% — what inflation is doing to your savings\n3. ₦{petrol}/L — what it costs to keep the economy moving\n\nEvery other number flows from these three.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "inflation", "petrol"],
        "category": "media_amplifier",
        "tag": None,
        "note": "No tag — clean data post for media sharing"
    },
    {
        "text": "Nigeria economic scorecard:\n\nFX rate (parallel): ₦{parallel}/$1\nCBN-parallel spread: {spread_pct:.1f}%\nInflation: {inflation}%\nFX Reserves: ${reserves:.1f}B\nOil production: ~1.4M bpd\nPetrol pump price: ₦{petrol}/L\n\nUpdated live. 📊 NairaIntel",
        "placeholders": ["parallel", "spread_pct", "inflation"],
        "category": "media_amplifier",
        "tag": None,
        "note": "No tag — dashboard post"
    },
    {
        "text": "A thread of numbers Nairametrics, BusinessDay, and Stears readers track every day:\n\n$1 = ₦{parallel}\nInflation = {inflation}%\nPetrol = ₦{petrol}/L\nNGX = {ngx:,}\n\nWe post these live, 3x daily with images.\n\nFollow @NairaIntel for the data.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "inflation", "petrol", "ngx"],
        "category": "media_amplifier",
        "tag": None,
        "note": "NAME-mention media bait — no tag"
    },

    # ══ ACCOUNTABILITY / MULTI-INSTITUTION ════════════════════════════════

    {
        "text": "Since subsidy removal in June 2023:\n\n📉 Naira: ₦460 → ₦{parallel} (-{deval_from_2023:.0f}%)\n⛽ Petrol: ₦185 → ₦{petrol}/L\n📈 Inflation: 22% → {inflation}%\n\nThe reform was necessary. The pain is real.\n\nCBN, NNPC, and DMO are all managing the aftermath.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "deval_from_2023", "petrol", "inflation"],
        "category": "institutional",
        "tag": None,
        "note": "NAME — multi-institution, no single tag"
    },
    {
        "text": "Nigeria's economic reform checklist:\n\n✅ Fuel subsidy removed\n✅ Naira floated\n✅ CBN rate hikes (11.5% → 27.5%)\n⏳ Electricity sector privatisation\n⏳ Tax reform bill\n⏳ Port efficiency\n❌ Inflation still at {inflation}%\n\nProgress is real. The work is unfinished.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "institutional",
        "tag": None,
        "note": "NAME — accountability overview"
    },
    {
        "text": "The agencies that move Nigeria's economy:\n\nCentral Bank → sets MPR at 27.5%\nNNPC → manages oil at ~1.4M bpd\nDMO → services $42B in debt\nFIRS → collecting record taxes\nSEC → overseeing NGX at {ngx:,}\n\nCoordination between them determines your ₦{parallel} rate.\n\n📊 NairaIntel",
        "placeholders": ["ngx", "parallel"],
        "category": "institutional",
        "tag": None,
        "note": "NAME — coordination overview, no single institution to tag"
    },

    # ══ PRAISE / MILESTONE POSTS (genuine, RT-worthy) ════════════════════

    {
        "text": "The CBN has published real-time FX data openly since 2024 — a transparency upgrade that analysts and researchers have noted.\n\nToday's official rate: ₦{cbn}/$1.\nParallel: ₦{parallel}/$1.\n\nData transparency is a precondition for market confidence.\n\n{cbn_tag} 📊 NairaIntel",
        "placeholders": ["cbn", "parallel"],
        "category": "praise_milestone",
        "tag": "cbn",
        "note": "TAG — genuine CBN transparency praise"
    },
    {
        "text": "Nigeria's NGX returned over 40% in naira terms in 2023 — one of the best-performing African exchanges that year.\n\nNGX today: {ngx:,}\n\nFor investors who stayed in Nigerian equities through the volatility, the patience paid off.\n\n{sec_tag} 📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "praise_milestone",
        "tag": "sec",
        "note": "TAG — NGX/SEC milestone"
    },
    {
        "text": "Nigeria processed over ₦600 trillion in NIP (instant payment) transactions in 2023.\n\nThat is one of the highest digital payment volumes in Africa — built on infrastructure the Central Bank mandated.\n\nFinancial infrastructure works quietly, then suddenly.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "praise_milestone",
        "tag": None,
        "note": "NAME — CBN payment infrastructure, no need to tag"
    },
    {
        "text": "FIRS collected a record ₦19.4 trillion in taxes in 2023 — up from ₦10.1 trillion in 2021.\n\nAt {inflation}% inflation some of that growth is nominal — but volumes also grew.\n\nBroadening the tax base is the structural fix Nigeria's fiscal problem needs.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "praise_milestone",
        "tag": "firs",
        "note": "TAG — citing FIRS record collection milestone"
    },
    {
        "text": "Nigeria's first Eurobond was in 2011. Since then: $15B+ raised internationally.\n\nAt ₦{parallel}/$1, servicing those dollar debts costs far more in naira than at issuance.\n\nEvery devaluation makes old debt more expensive.\n\n{dmo_tag} 💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "praise_milestone",
        "tag": "dmo",
        "note": "TAG — DMO milestone, balanced with cost reality"
    },

    # ══ JAPA / DIASPORA ANGLE ════════════════════════════════════════════

    {
        "text": "Nigeria received $19.5B in diaspora remittances in 2023.\n\nAt ₦{parallel}/$1, the diaspora sent home ₦{remittance_ngn:.1f} trillion.\n\nDiaspora Nigerians are the country's second-largest source of foreign exchange — after oil.\n\nEvery japa wave increases this number.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "institutional",
        "tag": None,
        "note": "NAME — diaspora angle, no specific institution to tag"
    },
    {
        "text": "For every Nigerian professional who japa'd this year:\n\nTheir UK salary at ₦{parallel}/$1 is now worth ₦{uk_salary_naira:,}/month.\n\nVs average Nigerian formal salary: ~₦300,000/month.\n\nThe exchange rate turns the brain drain into a remittance engine.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "institutional",
        "tag": None,
        "note": "NAME — engagement post, no tag"
    },

    # ══ ICPC / GOVERNANCE ════════════════════════════════════════════════

    {
        "text": "The Independent Corrupt Practices Commission was established in 2000 — two years before the EFCC.\n\nICPC focuses on public sector corruption specifically.\n\nAt {inflation}% inflation, the cost of governance failure is felt at every fuel station, market, and hospital.\n\n⚖️ NairaIntel",
        "placeholders": ["inflation"],
        "category": "efcc_recovery",
        "tag": None,
        "note": "NAME — ICPC general commentary"
    },
    {
        "text": "Corruption cost estimates for Nigeria range from $18B to $32B annually.\n\nAt ₦{parallel}/$1 that is ₦{corruption_cost_ngn:.1f}–{corruption_cost_ngn_hi:.1f} trillion.\n\nFor context, Nigeria's entire federal budget is ~₦28 trillion.\n\nThe ICPC and EFCC together are fighting a structural, not episodic, problem.\n\n⚖️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "efcc_recovery",
        "tag": None,
        "note": "NAME — broad accountability post"
    },
]


def get_type_f_count():
    return len(TYPE_F_FACTS)


def get_type_f_by_category(category):
    return [i for i, f in enumerate(TYPE_F_FACTS) if f["category"] == category]


def render_type_f(index, live_data):
    """
    Render a Type F post with live data and optional handle injection.
    Returns formatted tweet text or None on failure.
    """
    if index >= len(TYPE_F_FACTS):
        return None

    fact = TYPE_F_FACTS[index]
    template = fact["text"]
    tag_key  = fact.get("tag")

    # ── Resolve @handle or empty string ──────────────────────────────────────
    handle_str = HANDLES.get(tag_key, "") if tag_key else ""

    # Build named handle placeholders (cbn_tag, nnpc_tag, etc.)
    tag_subs = {f"{k}_tag": v for k, v in HANDLES.items()}
    # Override with empty string if this post doesn't use this tag
    # (prevents accidental tag injection from stray placeholders)
    if tag_key:
        tag_subs[f"{tag_key}_tag"] = HANDLES[tag_key]
    # All other _tag placeholders become empty so they don't appear
    for k in HANDLES:
        if k != tag_key:
            tag_subs[f"{k}_tag"] = ""

    # ── Live data values ──────────────────────────────────────────────────────
    parallel  = live_data.get("parallel", 1559)
    inflation = live_data.get("inflation", 33.2)
    petrol    = live_data.get("petrol", 897)
    ngx       = live_data.get("ngx", 104520)
    yr        = live_data.get("yr", 2026)
    cbn       = live_data.get("cbn", 1342)
    brent     = live_data.get("brent", 75)
    gold_usd  = live_data.get("gold_usd", 2930)
    reserves  = live_data.get("reserves", 34.2)
    spread_pct = live_data.get("spread_pct", 16.1)
    lpg_kg    = live_data.get("lpg_kg", 1200)

    # Derived values
    deval_from_2023   = round(((parallel - 460) / 460) * 100, 1)
    deval_from_2015   = round(((parallel - 197) / 197) * 100, 1)
    external_debt_ngn = round(42.3e9 * parallel / 1e12, 1)   # in trillions
    remittance_ngn    = round(19.5 * parallel / 1e6, 1)   # $19.5B in trillions
    tbill_real        = round(20 - inflation, 1)
    daily_oil_rev     = round(1.4e6 * (brent * 0.2) / 1e6, 0)  # Nigeria's ~20% net
    efcc_recovery_ngn = round(1.2 * parallel / 1e3, 1)   # $1.2B in trillions
    uk_salary_naira   = round(3500 * parallel, 0)         # ~£3,500/month avg UK
    corruption_cost_ngn    = round(18 * parallel / 1e6, 1)
    corruption_cost_ngn_hi = round(32 * parallel / 1e6, 1)

    subs = {
        # Live market
        "parallel":    parallel,
        "inflation":   inflation,
        "petrol":      petrol,
        "ngx":         ngx,
        "yr":          yr,
        "cbn":         cbn,
        "brent":       brent,
        "gold_usd":    gold_usd,
        "reserves":    reserves,
        "spread_pct":  spread_pct,
        "lpg_kg":      lpg_kg,
        # Derived
        "deval_from_2023":        deval_from_2023,
        "deval_from_2015":        deval_from_2015,
        "external_debt_ngn":      external_debt_ngn,
        "remittance_ngn":         remittance_ngn,
        "tbill_real":             tbill_real,
        "daily_oil_rev":          daily_oil_rev,
        "efcc_recovery_ngn":      efcc_recovery_ngn,
        "uk_salary_naira":        uk_salary_naira,
        "corruption_cost_ngn":    corruption_cost_ngn,
        "corruption_cost_ngn_hi": corruption_cost_ngn_hi,
        # Handle tags
        **tag_subs,
    }

    try:
        rendered = template.format_map(subs)
        # Clean up any double-spaces left by empty tag substitutions
        import re
        rendered = re.sub(r'\n\n\n+', '\n\n', rendered)
        rendered = re.sub(r'  +', ' ', rendered)
        rendered = rendered.strip()
        return rendered
    except KeyError as e:
        print(f"[WARN] type_f_pool: missing key {e} in fact {index}")
        return None
