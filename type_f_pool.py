"""
type_f_pool.py — Type F institutional engagement posts for NairaIntel.

Strategy:
  - POSITIVE or NEUTRAL tone only — official accounts will only engage with
    posts that cite their data, celebrate milestones, or present facts they
    are proud of. No criticism, no irony, no implied failure.
  - Mostly NAME-MENTIONS (no @tag) to avoid spam flags
  - Selective @tagging ONLY when citing that institution's own published data
    AND the framing is clearly positive or neutral
  - Live data anchors keep posts fresh every cycle

Slot: 12:00 WAT daily

Tag discipline:
  TAG  → institution cited positively with their own data
  NAME → mentioned by name, no @, neutral/educational framing
  NONE → no mention at all, clean data post

NOTE: All negative/critical posts that were originally drafted for Type F
have been moved to facts_pool.py (Type A) where the audience is everyday
Nigerians, not institutions. See bottom of file for the full list.
"""

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

TYPE_F_FACTS = [

    # ══ CBN / MONETARY POLICY ══════════════════════════════════════════════

    {
        "text": "Central Bank of Nigeria FX reserves: ${reserves:.1f}B\n\nAt current import levels that covers ~{import_cover:.0f} months of imports — above the IMF 3-month minimum.\n\nReserves provide the buffer that keeps the naira from free fall.\n\n{cbn_tag} 🏦 NairaIntel",
        "placeholders": ["reserves"],
        "category": "cbn_policy",
        "tag": "cbn",
    },
    {
        "text": "The Central Bank of Nigeria has published real-time FX data openly since 2024.\n\nToday's official rate: ₦{cbn}/$1\n\nTransparency in FX pricing is a foundational step toward market confidence and foreign investor trust.\n\n{cbn_tag} 📊 NairaIntel",
        "placeholders": ["cbn"],
        "category": "cbn_policy",
        "tag": "cbn",
    },
    {
        "text": "The CBN's official rate today: ₦{cbn}/$1\nParallel market: ₦{parallel}/$1\nSpread: {spread_pct:.1f}%\n\nThe gap has narrowed significantly from the 60%+ spread seen in 2022.\n\nFX unification is a process, not a single event.\n\n🏦 NairaIntel",
        "placeholders": ["cbn", "parallel", "spread_pct"],
        "category": "cbn_policy",
        "tag": None,
    },
    {
        "text": "Governor Cardoso inherited a central bank managing a 60%+ parallel market premium.\n\nToday that spread is {spread_pct:.1f}%.\n\nMPR: 27.5% | Reserves: ${reserves:.1f}B | Official rate: ₦{cbn}/$1\n\nMonetary stabilisation is a long road and the direction is right.\n\n🏦 NairaIntel",
        "placeholders": ["spread_pct", "reserves", "cbn"],
        "category": "cbn_policy",
        "tag": None,
    },
    {
        "text": "Nigeria processed over ₦600 trillion in NIP (instant payment) transactions in 2023.\n\nAmong the highest digital payment volumes in Africa — built on infrastructure the Central Bank of Nigeria mandated.\n\nFinancial infrastructure compounds quietly, then suddenly.\n\n{cbn_tag} 🏦 NairaIntel",
        "placeholders": [],
        "category": "cbn_policy",
        "tag": "cbn",
    },

    # ══ NNPC / OIL ══════════════════════════════════════════════════════════

    {
        "text": "Nigeria produces ~1.4M barrels of oil per day.\n\nAt ${brent:.0f}/barrel that is roughly ${daily_oil_rev:.0f}M/day in gross revenue.\n\nOil remains the anchor of Nigeria's foreign exchange earnings.\n\n{nnpc_tag} 🛢 NairaIntel",
        "placeholders": ["brent"],
        "category": "nnpc_oil",
        "tag": "nnpc",
    },
    {
        "text": "NNPC Limited became a commercial entity in 2022 — structured to operate like a global energy company.\n\nThe transition opened the door to private investment in upstream and midstream oil and gas.\n\nOil output today: ~1.4M bpd.\n\n{nnpc_tag} 🛢 NairaIntel",
        "placeholders": [],
        "category": "nnpc_oil",
        "tag": "nnpc",
    },
    {
        "text": "The Dangote Refinery (650,000 bpd) is the largest single-train refinery in the world.\n\nWhen operating at full capacity alongside the NNPC domestic supply mandate, Nigeria's petrol import bill goes to zero.\n\nAt ₦{parallel}/$1, that saves billions in FX every year.\n\n🛢 NairaIntel",
        "placeholders": ["parallel"],
        "category": "nnpc_oil",
        "tag": None,
    },
    {
        "text": "Nigeria has the largest natural gas reserves in Africa.\n\nThe gas monetisation policy aims to turn stranded reserves into LNG exports and domestic power generation.\n\nLPG today: ₦{lpg_kg}/kg. The infrastructure investment is building.\n\n🔥 NairaIntel",
        "placeholders": ["lpg_kg"],
        "category": "nnpc_oil",
        "tag": None,
    },

    # ══ EFCC / FINANCIAL CRIME RECOVERY ════════════════════════════════════

    {
        "text": "The EFCC recovered over $1.2B in stolen assets between 2015 and 2023.\n\nAt ₦{parallel}/$1 that is ₦{efcc_recovery_ngn:.1f} trillion returned to the public purse.\n\nAsset recovery at scale is one of the most direct ways to rebuild national wealth.\n\n{efcc_tag} 💰 NairaIntel",
        "placeholders": ["parallel"],
        "category": "efcc_recovery",
        "tag": "efcc",
    },
    {
        "text": "The EFCC has secured thousands of convictions since 2003 — making it one of the most active anti-corruption agencies in Africa.\n\nInternational cooperation has expanded its reach beyond Nigerian borders.\n\n{efcc_tag} ⚖️ NairaIntel",
        "placeholders": [],
        "category": "efcc_recovery",
        "tag": "efcc",
    },
    {
        "text": "The EFCC has repatriated hundreds of millions of dollars in stolen assets from foreign jurisdictions back to Nigeria.\n\nInternational asset recovery requires years of legal work across multiple countries.\n\nEvery dollar returned is a dollar the economy gets back.\n\n{efcc_tag} ⚖️ NairaIntel",
        "placeholders": [],
        "category": "efcc_recovery",
        "tag": "efcc",
    },
    {
        "text": "Nigeria and the United States have collaborated on multiple asset repatriation agreements.\n\nRecovered funds repatriated from foreign accounts go directly to the federal account.\n\nAt ₦{parallel}/$1, every dollar recovered matters to the FX picture.\n\n⚖️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "efcc_recovery",
        "tag": None,
    },

    # ══ DMO / SOVEREIGN DEBT ════════════════════════════════════════════════

    {
        "text": "The Debt Management Office currently offers 91-day T-bills at ~20% per annum.\n\nInflation: {inflation}%\nReal return: {tbill_real:.1f}%\n\nNigerian T-bills are now offering positive real returns — a first in several years.\n\n{dmo_tag} 💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "dmo_debt",
        "tag": "dmo",
    },
    {
        "text": "Nigeria's first Eurobond was issued in 2011 — opening international capital markets to the country for the first time.\n\nThe Debt Management Office has since raised $15B+ from global investors.\n\nInternational market access is a vote of confidence in Nigeria's creditworthiness.\n\n{dmo_tag} 💸 NairaIntel",
        "placeholders": [],
        "category": "dmo_debt",
        "tag": "dmo",
    },
    {
        "text": "The Debt Management Office has been actively extending Nigeria's debt maturity profile — shifting from short-term to longer-dated instruments.\n\nLonger maturities reduce refinancing pressure and give the economy room to grow into its obligations.\n\n{dmo_tag} 📊 NairaIntel",
        "placeholders": [],
        "category": "dmo_debt",
        "tag": "dmo",
    },
    {
        "text": "Nigeria's fixed income market offers some of the highest real yields in Africa right now.\n\nT-bill yield: ~20% | Inflation: {inflation}% | Real yield: {tbill_real:.1f}%\n\nManaged through the FMDQ Exchange with CBN oversight.\n\nFor naira investors, the window is open.\n\n{fmdq_tag} 📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "dmo_debt",
        "tag": "fmdq",
    },

    # ══ FIRS / TAX & REVENUE ════════════════════════════════════════════════

    {
        "text": "The Federal Inland Revenue Service collected ₦19.4 trillion in 2023 — a new record.\n\nUp from ₦10.1 trillion in 2021. That is 92% growth in two years.\n\nNigeria's tax administration is delivering.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": [],
        "category": "firs_revenue",
        "tag": "firs",
    },
    {
        "text": "Nigeria now earns more from taxes than from oil — a structural shift that took decades to arrive.\n\nFIRS revenue exceeded NNPC remittances in 2023.\n\nA diversified revenue base is the foundation of a resilient economy.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": [],
        "category": "firs_revenue",
        "tag": "firs",
    },
    {
        "text": "The Federal Inland Revenue Service targets ₦34.5 trillion in tax revenue for 2025.\n\nAt ₦{parallel}/$1 that is roughly $22B — equivalent to most of Nigeria's annual federal budget.\n\nTax reform is the most durable path to fiscal independence.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": ["parallel"],
        "category": "firs_revenue",
        "tag": "firs",
    },

    # ══ SEC / CAPITAL MARKETS ════════════════════════════════════════════════

    {
        "text": "Nigeria's NGX returned over 40% in naira terms in 2023 — one of the best-performing stock exchanges in Africa that year.\n\nNGX today: {ngx:,}\n\nPatient investors in Nigerian equities have been rewarded.\n\n{sec_tag} 📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "sec_markets",
        "tag": "sec",
    },
    {
        "text": "Nigeria's NGX crossed 100,000 points for the first time in 2024.\n\nA milestone 64 years in the making since the exchange opened in 1960.\n\nNGX today: {ngx:,}\n\nThe Nigerian stock market is the largest in West Africa.\n\n{sec_tag} 📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "sec_markets",
        "tag": "sec",
    },
    {
        "text": "The Securities and Exchange Commission has introduced reforms to deepen Nigeria's capital market — expanded commodities trading, CSCS digital upgrade, and rules to attract foreign portfolio investors.\n\nNGX today: {ngx:,}\n\n{sec_tag} 📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "sec_markets",
        "tag": "sec",
    },
    {
        "text": "Foreign portfolio investors have gradually returned to Nigerian equities since the 2023 naira float.\n\nNGX today: {ngx:,} | $1 = ₦{parallel}\n\nFX predictability draws capital. Naira stability is a market development tool.\n\n📈 NairaIntel",
        "placeholders": ["ngx", "parallel"],
        "category": "sec_markets",
        "tag": None,
    },

    # ══ FMDQ / FX MARKET ════════════════════════════════════════════════════

    {
        "text": "The FMDQ Exchange manages Nigeria's official FX window through Willing Buyer Willing Seller transactions.\n\nToday's FMDQ rate: ₦{cbn}/$1\n\nA transparent, market-determined rate is the foundation of FX confidence.\n\n{fmdq_tag} 📊 NairaIntel",
        "placeholders": ["cbn"],
        "category": "cbn_policy",
        "tag": "fmdq",
    },

    # ══ MEDIA AMPLIFIER ══════════════════════════════════════════════════════

    {
        "text": "NairaIntel live data — {yr}:\n\n💵 $1 = ₦{parallel}\n⛽ Petrol: ₦{petrol}/L\n📈 Inflation: {inflation}%\n📊 NGX: {ngx:,}\n🥇 Gold: ${gold_usd:,}/oz\n🛢 Brent: ${brent}/bbl\n\nUpdated 3x daily.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "petrol", "inflation", "ngx"],
        "category": "media_amplifier",
        "tag": None,
    },
    {
        "text": "Nigeria economic snapshot:\n\nFX (parallel): ₦{parallel}/$1\nCBN official: ₦{cbn}/$1\nInflation: {inflation}%\nFX Reserves: ${reserves:.1f}B\nPetrol: ₦{petrol}/L\nNGX: {ngx:,}\n\nTracked and published live by @NairaIntel.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "cbn", "inflation", "petrol", "ngx"],
        "category": "media_amplifier",
        "tag": None,
    },
    {
        "text": "Three numbers that define Nigeria's economy today:\n\n₦{parallel} — cost of $1 in the parallel market\n{inflation}% — annual inflation rate\n₦{petrol}/L — petrol pump price\n\nEvery financial decision in Nigeria flows from these three.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "inflation", "petrol"],
        "category": "media_amplifier",
        "tag": None,
    },
    {
        "text": "The numbers Nairametrics, BusinessDay, and Stears readers track every day:\n\n$1 = ₦{parallel} | Inflation = {inflation}% | NGX = {ngx:,}\n\nWe publish these live with charts, 3x daily.\n\nFollow @NairaIntel for the data.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "inflation", "ngx"],
        "category": "media_amplifier",
        "tag": None,
    },

    # ══ DIASPORA / REMITTANCES ═══════════════════════════════════════════════

    {
        "text": "Nigeria received $19.5B in diaspora remittances in 2023.\n\nAt ₦{parallel}/$1 the diaspora sent home ₦{remittance_ngn:.1f} trillion — more than most state governments' annual budgets combined.\n\nThe Nigerian diaspora is one of the most powerful economic forces in Africa.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "institutional",
        "tag": None,
    },
    {
        "text": "A Nigerian professional abroad sending home £500/month:\n\nAt ₦{parallel}/$1 that is ₦{remit_500_ngn:,}/month into a Nigerian household.\n\nRemittances have become the most direct, efficient poverty-reduction tool in the economy.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "institutional",
        "tag": None,
    },

    # ══ REFORM PROGRESS ══════════════════════════════════════════════════════

    {
        "text": "Nigeria's economic reform wins since 2023:\n\n✅ Fuel subsidy removed\n✅ Naira floated\n✅ CBN rate normalised (27.5% MPR)\n✅ Tax revenue now exceeds oil revenue\n✅ FX spread narrowed from 60%+ to {spread_pct:.0f}%\n✅ FX data published openly\n\nThe foundation is being rebuilt.\n\n📊 NairaIntel",
        "placeholders": ["spread_pct"],
        "category": "institutional",
        "tag": None,
    },
    {
        "text": "The institutions rebuilding Nigeria's economy:\n\nCentral Bank → FX unification + rate normalisation\nNNPC → commercial restructuring + refinery\nFIRS → record tax collection\nDMO → debt maturity extension\nSEC → capital market deepening\n\n📊 NairaIntel",
        "placeholders": [],
        "category": "institutional",
        "tag": None,
    },

    # ══ FINTECH MILESTONES ═══════════════════════════════════════════════════

    {
        "text": "Nigeria's fintech ecosystem is valued at over $5B.\n\nFlutterwave, Paystack, Moniepoint, Interswitch — all built on infrastructure the CBN and SEC helped regulate into existence.\n\nRegulation enabled innovation here.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "praise_milestone",
        "tag": None,
    },
    {
        "text": "The CBN's cashless policy launched in 2012 is delivering results:\n\n₦600 trillion+ in annual NIP transactions\n100M+ monthly USSD transactions on feature phones\nMobile money reaching the previously unbanked\n\nPolicy with a decade-long payoff.\n\n{cbn_tag} 🏦 NairaIntel",
        "placeholders": [],
        "category": "praise_milestone",
        "tag": "cbn",
    },
    {
        "text": "FIRS collected ₦19.4 trillion in 2023 — placing Nigeria among Africa's fastest-growing tax revenue stories.\n\nFrom ₦10.1 trillion in 2021 to ₦19.4 trillion in 2023.\n\n92% growth in two years.\n\n{firs_tag} 📊 NairaIntel",
        "placeholders": [],
        "category": "praise_milestone",
        "tag": "firs",
    },
]


# ══ POSTS MOVED OUT OF TYPE F ══════════════════════════════════════════════════
# These were removed because their framing is negative or critical.
# Official accounts will not engage with them. They belong in Type A (facts_pool)
# where the audience is everyday Nigerians who feel these realities:
#
# MOVED TO facts_pool.py category "cbn":
#   - "Higher rates alone can't fix supply-side inflation" (tagged @cenbank)
#   - "BDC ban reversed, floating, spread persists"
#   - "Enforcement alone won't close FX spread rooted in structural scarcity"
#
# MOVED TO facts_pool.py category "oil":
#   - "NNPC structure changed. Results pending."
#
# MOVED TO facts_pool.py category "governance":
#   - "EFCC recovery is a fraction of what illicit flows take out"
#   - "Corruption index barely moved in 20 years"
#   - "Cost of governance failure felt at every fuel station"
#   - "Corruption costs $18-32B annually"
#
# MOVED TO facts_pool.py category "debt":
#   - "Debt service-to-revenue ratio was over 90% in 2023"
#   - "Every devaluation makes old dollar debt more expensive"
#
# MOVED TO facts_pool.py category "fiscal":
#   - "FIRS revenue growth partly nominal due to inflation"
#
# MOVED TO facts_pool.py category "reform":
#   - "Reform checklist with ❌ Inflation still 33%"
# ==============================================================================


def get_type_f_count():
    return len(TYPE_F_FACTS)


def get_type_f_by_category(category):
    return [i for i, f in enumerate(TYPE_F_FACTS) if f["category"] == category]


def render_type_f(index, live_data):
    if index >= len(TYPE_F_FACTS):
        return None

    fact     = TYPE_F_FACTS[index]
    template = fact["text"]
    tag_key  = fact.get("tag")

    tag_subs = {f"{k}_tag": "" for k in HANDLES}
    if tag_key and tag_key in HANDLES:
        tag_subs[f"{tag_key}_tag"] = HANDLES[tag_key]

    parallel   = live_data.get("parallel", 1559)
    inflation  = live_data.get("inflation", 33.2)
    petrol     = live_data.get("petrol", 897)
    ngx        = live_data.get("ngx", 104520)
    yr         = live_data.get("yr", 2026)
    cbn        = live_data.get("cbn", 1342)
    brent      = live_data.get("brent", 75)
    gold_usd   = live_data.get("gold_usd", 2930)
    reserves   = live_data.get("reserves", 34.2)
    spread_pct = live_data.get("spread_pct", 16.1)
    lpg_kg     = live_data.get("lpg_kg", 1200)

    tbill_real        = round(20 - inflation, 1)
    daily_oil_rev     = round(1.4e6 * (brent * 0.2) / 1e6, 0)
    efcc_recovery_ngn = round(1.2e9 * parallel / 1e12, 1)
    remittance_ngn    = round(19.5e9 * parallel / 1e12, 1)
    uk_salary_naira   = round(3500 * parallel, 0)
    import_cover      = round(reserves / 50 * 12, 0)
    min_wage_usd      = round(70000 / parallel, 1)
    poverty_line_ngn  = round(2.15 * parallel, 0)
    remit_500_ngn     = round(500 * parallel, 0)

    subs = {
        "parallel":          parallel,
        "inflation":         inflation,
        "petrol":            petrol,
        "ngx":               ngx,
        "yr":                yr,
        "cbn":               cbn,
        "brent":             brent,
        "gold_usd":          gold_usd,
        "reserves":          reserves,
        "spread_pct":        spread_pct,
        "lpg_kg":            lpg_kg,
        "tbill_real":        tbill_real,
        "daily_oil_rev":     daily_oil_rev,
        "efcc_recovery_ngn": efcc_recovery_ngn,
        "remittance_ngn":    remittance_ngn,
        "uk_salary_naira":   uk_salary_naira,
        "import_cover":      import_cover,
        "min_wage_usd":      min_wage_usd,
        "poverty_line_ngn":  poverty_line_ngn,
        "remit_500_ngn":     remit_500_ngn,
        **tag_subs,
    }

    try:
        import re
        rendered = template.format_map(subs)
        rendered = re.sub(r'\n\n\n+', '\n\n', rendered)
        rendered = re.sub(r'  +', ' ', rendered)
        return rendered.strip()
    except KeyError as e:
        print(f"[WARN] type_f_pool: missing key {e} in fact {index}")
        return None
