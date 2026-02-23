"""
facts_pool.py — Type A static + dynamic-anchor facts for NairaIntel text posts.

Each fact is a dict:
  "text"      : the tweet template (under 240 chars to leave room for NairaIntel tag)
  "placeholders": list of keys this fact uses from live_data
  "category"  : for rotation logic (avoid same category back-to-back)

Placeholders available (all calculated live at post time):
  {parallel}          — current USD/NGN parallel rate e.g. 1499
  {cbn}               — CBN official rate
  {inflation}         — current inflation % e.g. 33.2
  {petrol}            — petrol price ₦/L
  {deval_pct}         — % devaluation from NGN's peg of ₦0.66/$1 in 1973
  {deval_from_2015}   — % change from ₦197 in Jan 2015
  {deval_from_2020}   — % change from ₦360 in Jan 2020
  {deval_from_2023}   — % change from ₦460 in Jan 2023 (pre-float)
  {salary_usd}        — ₦500k/month in USD at today's rate
  {petrol_cost_50L}   — cost to fill 50L tank today in Naira
  {yr}                — current year
  {ngx}               — NGX All-Share Index today
"""

FACTS = [

    # ── NAIRA DEVALUATION HISTORY ────────────────────────────────────────────

    {
        "text": "In 1973, $1 = ₦0.66. Today $1 = ₦{parallel}.\n\nThe naira has lost {deval_pct}% of its value against the dollar in 50 years.\n\n📉 NairaIntel",
        "placeholders": ["parallel", "deval_pct"],
        "category": "devaluation"
    },
    {
        "text": "January 2015: $1 = ₦197.\nToday: $1 = ₦{parallel}.\n\nThe naira has fallen {deval_from_2015}% in 10 years.\n\nA ₦500k salary that was worth $2,538 is now worth ₦{salary_usd}.\n\n📉 NairaIntel",
        "placeholders": ["parallel", "deval_from_2015", "salary_usd"],
        "category": "devaluation"
    },
    {
        "text": "January 2020: $1 = ₦360.\nToday: $1 = ₦{parallel}.\n\nThe naira fell {deval_from_2020}% in just 5 years.\n\nThat's faster than most war economies.\n\n📉 NairaIntel",
        "placeholders": ["parallel", "deval_from_2020"],
        "category": "devaluation"
    },
    {
        "text": "May 2023 (pre-float): $1 = ₦460.\nToday: $1 = ₦{parallel}.\n\nThe naira lost {deval_from_2023}% in under 2 years after the subsidy removal.\n\n📉 NairaIntel",
        "placeholders": ["parallel", "deval_from_2023"],
        "category": "devaluation"
    },
    {
        "text": "The naira has been officially devalued 9 times since 1973.\n\n1973 → 1986 → 1992 → 1999 → 2015 → 2016 → 2020 → 2023 → 2024.\n\nToday: $1 = ₦{parallel}.\n\n📉 NairaIntel",
        "placeholders": ["parallel"],
        "category": "devaluation"
    },
    {
        "text": "In 1960 (independence), ₦1 was worth more than $1.\n\nToday you need ₦{parallel} to buy $1.\n\nThat is a collapse of more than 99.9% in 65 years.\n\n📉 NairaIntel",
        "placeholders": ["parallel"],
        "category": "devaluation"
    },
    {
        "text": "The naira was pegged at ₦1 = $1.52 in 1980.\n\nBy 1993 it had fallen to ₦22/$1.\nBy 2016 it was ₦305/$1.\nBy {yr} it is ₦{parallel}/$1.\n\nEvery decade, a new floor.\n\n📉 NairaIntel",
        "placeholders": ["parallel", "yr"],
        "category": "devaluation"
    },
    {
        "text": "A Nigerian who kept $1,000 under the bed in 2015 has ₦{parallel_1000:,} today.\n\nA Nigerian who kept the naira equivalent (₦197,000) under the bed has ₦197,000 today — worth just $131.\n\nDollar vs naira storage: not even close.\n\n💵 NairaIntel",
        "placeholders": ["parallel"],
        "category": "devaluation",
        "custom_calc": "parallel_1000"
    },

    # ── PETROL / FUEL HISTORY ────────────────────────────────────────────────

    {
        "text": "Petrol price history in Nigeria:\n\n2003: ₦26/L\n2012: ₦97/L\n2016: ₦145/L\n2020: ₦162/L\nMay 2023: ₦185/L\nJune 2023: ₦617/L\nToday: ₦{petrol}/L\n\nSubsidy removal changed everything.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },
    {
        "text": "In 2003, ₦1,000 bought 38 litres of petrol.\n\nToday ₦1,000 buys {litres_per_1k:.1f} litres.\n\nSame money. Less fuel. More hunger.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel",
        "custom_calc": "litres_per_1k"
    },
    {
        "text": "Before June 2023, Nigeria had the cheapest petrol in West Africa at ₦185/L.\n\nToday at ₦{petrol}/L, it is among the most expensive relative to average wages.\n\nSubsidy removal: the experiment continues.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },
    {
        "text": "Nigeria spent ₦4.4 trillion on petrol subsidy in 2022 alone.\n\nThat is more than the entire education budget.\n\nSubsidy is gone now. Petrol is ₦{petrol}/L.\n\nWas it worth it? Still debated.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },
    {
        "text": "Filling a 50-litre tank today costs ₦{petrol_cost_50L:,}.\n\nIn 2020 it cost ₦8,100.\nIn 2022 it cost ₦9,250.\nIn June 2023 it cost ₦30,850.\nToday: ₦{petrol_cost_50L:,}.\n\nFor the average worker, this is 9+ days wages.\n\n⛽ NairaIntel",
        "placeholders": ["petrol_cost_50L"],
        "category": "fuel"
    },

    # ── GDP & ECONOMY SIZE ───────────────────────────────────────────────────

    {
        "text": "Nigeria's GDP per capita at independence in 1960: ~$1,100.\nSouth Korea's in 1960: ~$900.\n\nToday:\nNigeria: ~$2,100\nSouth Korea: ~$35,000\n\nSame starting line. 65 years later.\n\n📊 NairaIntel",
        "placeholders": [],
        "category": "gdp"
    },
    {
        "text": "Nigeria became Africa's largest economy in 2014 after rebasing its GDP.\n\nIt overtook South Africa literally overnight — on paper.\n\nThe economy went from $270B to $510B without a single new factory.\n\n📊 NairaIntel",
        "placeholders": [],
        "category": "gdp"
    },
    {
        "text": "Nigeria has the largest economy in Africa by GDP.\n\nBut GDP per capita ranks below Botswana, Namibia, and even Cabo Verde.\n\nBig economy. Unequal distribution.\n\nInflation today: {inflation}%.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "gdp"
    },
    {
        "text": "Nigeria's GDP shrank in USD terms from $577B (2014) to $253B (2023).\n\nNot because the economy produced less — but because the naira collapsed.\n\nCurrency matters as much as output.\n\n$1 = ₦{parallel} today.\n\n📊 NairaIntel",
        "placeholders": ["parallel"],
        "category": "gdp"
    },
    {
        "text": "Egypt overtook Nigeria as Africa's largest economy in 2023.\n\nFor 9 years Nigeria held the crown it rebased itself into in 2014.\n\nThe naira's fall did what no competitor could.\n\n📊 NairaIntel",
        "placeholders": [],
        "category": "gdp"
    },

    # ── INFLATION HISTORY ────────────────────────────────────────────────────

    {
        "text": "Nigeria's inflation history:\n\n2015: 9%\n2017: 18%\n2020: 15%\n2022: 21%\n2023: 29%\nJan 2025: 24%\nToday: {inflation}%\n\nThe CBN target is 6-9%.\n\nWe are {inflation_vs_target:.0f}x above target.\n\n📈 NairaIntel",
        "placeholders": ["inflation"],
        "category": "inflation"
    },
    {
        "text": "At {inflation}% inflation, ₦100,000 today will have the purchasing power of ₦{inflation_erosion:,.0f} in 12 months.\n\nYour money needs to grow faster than inflation just to stay still.\n\n📈 NairaIntel",
        "placeholders": ["inflation"],
        "category": "inflation"
    },
    {
        "text": "Nigeria's inflation peaked at 47.6% in September 1994.\n\nToday it is {inflation}%.\n\nHigh — but we have been here before. The question is how long we stay.\n\n📈 NairaIntel",
        "placeholders": ["inflation"],
        "category": "inflation"
    },
    {
        "text": "Food inflation in Nigeria has stayed above 30% for most of 2024-2025.\n\nFor a family spending 60% of income on food, 30% food inflation means their real spending power fell 18% from food costs alone.\n\nOverall inflation: {inflation}%.\n\n🍚 NairaIntel",
        "placeholders": ["inflation"],
        "category": "inflation"
    },

    # ── WAGES & PURCHASING POWER ─────────────────────────────────────────────

    {
        "text": "Nigeria's minimum wage:\n\n1981: ₦100/month ($153)\n2000: ₦3,500/month ($35)\n2011: ₦18,000/month ($119)\n2019: ₦30,000/month ($83)\n2024: ₦70,000/month (~$47)\n\nIn dollar terms, workers earn less than 40 years ago.\n\n💰 NairaIntel",
        "placeholders": [],
        "category": "wages"
    },
    {
        "text": "Nigeria's new minimum wage is ₦70,000/month.\n\nAt today's rate of ₦{parallel}/$1, that is ${min_wage_usd:.0f}/month.\n\nThe UN poverty line is $2.15/day = $65.15/month.\n\nMinimum wage workers earn ${min_wage_usd:.0f}/month.\n\n💰 NairaIntel",
        "placeholders": ["parallel"],
        "category": "wages",
        "custom_calc": "min_wage_usd"
    },
    {
        "text": "A ₦500,000/month salary in Nigeria:\n\n2020: worth $1,389\n2022: worth $1,087\n2023 (pre-float): worth $1,087\n2024 (post-float): worth $556\nToday: worth ${salary_usd}\n\nSame naira. Less dollar.\n\n💰 NairaIntel",
        "placeholders": ["salary_usd"],
        "category": "wages"
    },
    {
        "text": "In Kenya, a $500/month salary is considered middle class.\nIn Nigeria, $500/month requires earning ₦{parallel_500:,}/month.\n\nThat is roughly 7x Nigeria's minimum wage.\n\n$1 = ₦{parallel} today.\n\n💰 NairaIntel",
        "placeholders": ["parallel"],
        "category": "wages",
        "custom_calc": "parallel_500"
    },

    # ── BANKING & FINTECH ────────────────────────────────────────────────────

    {
        "text": "Nigeria has the largest fintech ecosystem in Africa.\n\nOver 200 licensed fintech companies.\nFlutterwave valued at $3B.\nPaystack acquired by Stripe for $200M in 2020.\nMoniepoint hit 10M+ users in 2024.\n\nYet 38% of Nigerians remain unbanked.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "fintech"
    },
    {
        "text": "Paystack was founded in 2015.\nAcquired by Stripe in 2020 for ~$200M.\nAt the time, $1 = ₦360.\n\nThe founders' naira proceeds from that deal are now worth {paystack_deval:.0f}% less in dollar terms.\n\nEven exits aren't safe from devaluation.\n\n$1 = ₦{parallel} today.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "fintech",
        "custom_calc": "paystack_deval"
    },
    {
        "text": "Nigeria processes over $24B in mobile money transactions annually.\n\nYet most of it goes through bank apps, not mobile wallets.\n\nWe skipped the M-Pesa stage and went straight to app banking.\n\nUnique path. Real results.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "fintech"
    },
    {
        "text": "The CBN introduced the cashless policy in 2012.\n\nToday Nigeria is one of the most active mobile payment markets in Africa.\n\nPOS agents, USSD banking, and app transfers have replaced cash for millions.\n\nInflation: {inflation}%. Fintech: growing.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "fintech"
    },
    {
        "text": "Nigerian banks collected ₦923.4B in fees and charges in 2023.\n\nThat is money paid just to move your own money.\n\nAt today's rate that is $614M — extracted from customers every year.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "banking"
    },

    # ── OIL & ENERGY ─────────────────────────────────────────────────────────

    {
        "text": "Nigeria earned $93B from oil in 2022.\n\nYet fuel was being subsidised and the naira was collapsing.\n\nOil wealth + currency collapse = the Nigerian paradox.\n\nBrent crude today: still the anchor of everything.\n\n🛢 NairaIntel",
        "placeholders": [],
        "category": "oil"
    },
    {
        "text": "Nigeria has the largest natural gas reserves in Africa.\n\nYet millions cook with firewood.\nLPG (cooking gas) now costs ₦{lpg_per_kg:,}/kg.\n\nA nation sitting on gas that can't afford to use it.\n\n🔥 NairaIntel",
        "placeholders": [],
        "category": "oil"
    },
    {
        "text": "Nigeria has been an OPEC member since 1971.\n\nIn that time, oil has earned Nigeria over $1.5 trillion.\n\nYet the country's external debt stands at over $42B.\n\nWhere did the trillion go?\n\n🛢 NairaIntel",
        "placeholders": [],
        "category": "oil"
    },
    {
        "text": "The Dangote Refinery has a capacity of 650,000 barrels/day.\n\nIf running at full capacity, it would make Nigeria self-sufficient in petrol AND an exporter.\n\nToday's pump price: ₦{petrol}/L.\nFull capacity is the target.\n\n🏭 NairaIntel",
        "placeholders": ["petrol"],
        "category": "oil"
    },
    {
        "text": "Nigeria's oil production peaked at 2.4M barrels/day in 2010.\n\nToday it is around 1.4M bpd — 40% below peak.\n\nPipeline vandalism, ageing infrastructure, and underinvestment.\n\nEvery barrel lost is naira lost.\n\n🛢 NairaIntel",
        "placeholders": [],
        "category": "oil"
    },

    # ── STOCK MARKET / NGX ───────────────────────────────────────────────────

    {
        "text": "The Nigerian Stock Exchange opened in 1960 — the same year as independence.\n\nToday the NGX All-Share Index stands at {ngx:,}.\n\nFrom pennies to hundreds of thousands in 65 years — but inflation-adjusted returns tell a different story.\n\n📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "ngx"
    },
    {
        "text": "The NGX All-Share Index crashed 70% between March 2008 and March 2009 during the global financial crisis.\n\nIt took 15 years to fully recover in nominal terms.\n\nToday it stands at {ngx:,}.\n\nPatience is the Nigerian investor's edge.\n\n📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "ngx"
    },
    {
        "text": "Investing in NGX stocks in naira terms has beaten inflation in several years.\n\nBut in dollar terms, the naira devaluation wipes most gains.\n\nNGX today: {ngx:,}.\n$1 today: ₦{parallel}.\n\nWhich currency you measure in changes everything.\n\n📈 NairaIntel",
        "placeholders": ["ngx", "parallel"],
        "category": "ngx"
    },

    # ── DEBT & FISCAL ────────────────────────────────────────────────────────

    {
        "text": "Nigeria's debt service cost in 2023 was ₦8.3 trillion.\n\nTotal revenue was ₦9.1 trillion.\n\nThat means 91% of government revenue went to paying debt.\n\nAt {inflation}% inflation, the cost of new debt keeps rising.\n\n💸 NairaIntel",
        "placeholders": ["inflation"],
        "category": "debt"
    },
    {
        "text": "Nigeria's external debt: over $42 billion.\n\nAt ₦{parallel}/$1, that is ₦{external_debt_ngn:,.0f} trillion in naira terms.\n\nEvery time the naira weakens, the debt load in naira grows — without borrowing a single dollar more.\n\n💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "debt",
        "custom_calc": "external_debt_ngn"
    },
    {
        "text": "In 2015, Nigeria's debt-to-GDP ratio was 12%.\n\nBy 2023 it was over 37%.\n\nStill lower than many developed countries. But growing faster.\n\n$1 = ₦{parallel} today.\n\n💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "debt"
    },

    # ── TRADE & REMITTANCES ──────────────────────────────────────────────────

    {
        "text": "Nigeria receives more remittances than any other country in sub-Saharan Africa.\n\nOver $20B in 2023.\n\nAt ₦{parallel}/$1, diaspora Nigerians sent home ₦{remittance_ngn:.1f} trillion.\n\nThe diaspora is Nigeria's second-largest forex earner.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "remittances",
        "custom_calc": "remittance_ngn"
    },
    {
        "text": "For every $1 a Nigerian in the UK sends home, the recipient gets ₦{parallel}.\n\nIn 2015 they would have gotten ₦197.\n\nThe same dollar buys {deval_from_2015}% more naira than it did 10 years ago.\n\nDevaluation: bad for savings. Good for receiving remittances.\n\n✈️ NairaIntel",
        "placeholders": ["parallel", "deval_from_2015"],
        "category": "remittances"
    },

    # ── CRYPTO & DIGITAL ASSETS ──────────────────────────────────────────────

    {
        "text": "Nigeria is one of the top 3 countries in the world for crypto adoption by volume.\n\nIn a country with 33%+ inflation and a volatile currency, crypto isn't speculation — it is survival finance.\n\nInflation today: {inflation}%.\n\n₿ NairaIntel",
        "placeholders": ["inflation"],
        "category": "crypto"
    },
    {
        "text": "The CBN banned crypto transactions by banks in February 2021.\n\nIn December 2023, it reversed the ban.\n\nIn between, Nigerians traded billions on P2P platforms anyway.\n\nUSDT P2P today: ₦{parallel}.\n\n₿ NairaIntel",
        "placeholders": ["parallel"],
        "category": "crypto"
    },
    {
        "text": "Binance was banned in Nigeria in February 2024.\n\nTigran Gambaryan, a US Binance executive, was detained for months.\n\nYet Nigerians remain among the world's most active crypto traders.\n\nThe market always finds a way.\n\nP2P rate today: ₦{parallel}/$1.\n\n₿ NairaIntel",
        "placeholders": ["parallel"],
        "category": "crypto"
    },

    # ── COMPARISONS WITH PEERS ───────────────────────────────────────────────

    {
        "text": "In 2000:\nGhana Cedi: 7,000/USD\nNigeria Naira: 101/USD\n\nNigeria had the stronger currency.\n\nToday:\nGhana Cedi: ~15/USD\nNigeria Naira: ₦{parallel}/USD\n\nGhana reformed. Nigeria devalued more.\n\n📊 NairaIntel",
        "placeholders": ["parallel"],
        "category": "comparison"
    },
    {
        "text": "Kenya's inflation: ~5%\nGhana's inflation: ~22%\nNigeria's inflation: {inflation}%\nEgypt's inflation: ~25%\n\nWest Africa is dealing with a regional inflation crisis — but Nigeria's is among the highest.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "comparison"
    },
    {
        "text": "South Africa's Reserve Bank targets 3-6% inflation.\nKenya targets 2.5-7.5%.\nNigeria's CBN target is 6-9%.\n\nActual Nigerian inflation today: {inflation}%.\n\nThat is {inflation_vs_target:.0f}x the upper target.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "comparison"
    },

    # ── PROVOCATIVE / ENGAGEMENT ─────────────────────────────────────────────

    {
        "text": "Two Nigerians both earn ₦500,000/month.\n\nOne keeps it in a savings account at 8% interest.\nOne converts to dollars immediately.\n\nAt {inflation}% inflation, the saver loses money in real terms.\nThe dollar holder gains if the naira weakens.\n\nWhich would you choose?\n\n💭 NairaIntel",
        "placeholders": ["inflation"],
        "category": "engagement"
    },
    {
        "text": "If you had ₦1,000,000 in January 2020:\n\nKept in bank: still ₦1,000,000+ interest. Worth ~$667 today.\nBought dollars: ~$2,778. Still $2,778 today.\nBought BTC (~$7,200/BTC): 0.386 BTC. Worth ~$26,000 today.\n\nSame million. Very different outcomes.\n\n💭 NairaIntel",
        "placeholders": [],
        "category": "engagement"
    },
    {
        "text": "The question every Nigerian faces:\n\nEarn in naira. Think in dollars.\nSave in naira. Lose to inflation.\nSave in dollars. Gain from devaluation.\n\nBut what if you can only earn in naira?\n\nThat is the real Nigerian financial puzzle.\n\n$1 = ₦{parallel} today.\n\n💭 NairaIntel",
        "placeholders": ["parallel"],
        "category": "engagement"
    },
    {
        "text": "In 1986 Nigeria introduced the structural adjustment program.\n\nIn 2023 Nigeria removed fuel subsidy.\n\nBoth caused immediate pain and were sold as long-term cures.\n\nInflation today: {inflation}%.\nPetrol today: ₦{petrol}/L.\n\nThe experiment continues.\n\n💭 NairaIntel",
        "placeholders": ["inflation", "petrol"],
        "category": "engagement"
    },
    {
        "text": "3 things that happened since the naira was floated in June 2023:\n\n1. Dollar went from ₦460 to ₦{parallel}\n2. Petrol went from ₦185/L to ₦{petrol}/L\n3. Inflation went from 22% to {inflation}%\n\nReform or collapse? Still depends who you ask.\n\n💭 NairaIntel",
        "placeholders": ["parallel", "petrol", "inflation"],
        "category": "engagement"
    },

    # ── POVERTY & DEVELOPMENT ────────────────────────────────────────────────

    {
        "text": "Nigeria has the second-largest number of people living in extreme poverty in the world — after India, a country with 7x the population.\n\nOver 100 million Nigerians live on under $2.15/day.\n\nAt ₦{parallel}/$1 that is under ₦{poverty_line_naira:.0f}/day.\n\n🔴 NairaIntel",
        "placeholders": ["parallel"],
        "category": "poverty",
        "custom_calc": "poverty_line_naira"
    },
    {
        "text": "Nigeria's poverty rate was 40% in 2019 (pre-COVID).\n\nAfter COVID, currency collapse, and subsidy removal — economists estimate it is now above 45-50%.\n\nGrowth without distribution is the story of Nigerian oil wealth.\n\n🔴 NairaIntel",
        "placeholders": [],
        "category": "poverty"
    },

    # ── FX RESERVES & CBN ────────────────────────────────────────────────────

    {
        "text": "Nigeria's FX reserves peaked at $62B in 2008.\n\nToday they stand at ~$34B.\n\nThe CBN uses reserves to defend the naira — but with $1 = ₦{parallel}, defence has limits.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "reserves"
    },
    {
        "text": "At current import levels, Nigeria's FX reserves cover about 5-6 months of imports.\n\nThe IMF recommends 3 months minimum. Nigeria exceeds that.\n\nBut at ₦{parallel}/$1, every import costs more naira than last year.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "reserves"
    },

    # ── AGRICULTURE ──────────────────────────────────────────────────────────

    {
        "text": "Nigeria spends over $3B a year importing wheat — for bread, noodles, and pasta.\n\nYet Nigeria has 70M hectares of arable land, most of it unused.\n\nAt ₦{parallel}/$1, every bag of imported flour is more expensive than last year.\n\n🌾 NairaIntel",
        "placeholders": ["parallel"],
        "category": "agriculture"
    },
    {
        "text": "Nigeria was once the world's largest exporter of groundnuts, palm oil, and cocoa.\n\nOil was discovered in 1956. By the 1970s, agriculture was abandoned.\n\nNow Nigeria imports food it once exported.\n\nToday inflation stands at {inflation}%.\n\n🌾 NairaIntel",
        "placeholders": ["inflation"],
        "category": "agriculture"
    },
    {
        "text": "The 2023 floods destroyed over ₦1 trillion in crops across Nigeria's food belt states.\n\nAgua, Benue, Anambra, Delta, Bayelsa.\n\nFood supply shock + naira collapse = the inflation cocktail Nigeria is still drinking.\n\nInflation today: {inflation}%.\n\n🌾 NairaIntel",
        "placeholders": ["inflation"],
        "category": "agriculture"
    },

    # ── ELECTRICITY & INFRASTRUCTURE ─────────────────────────────────────────

    {
        "text": "Nigeria has a population of 220M+.\n\nTotal installed electricity capacity: ~13,000MW.\n\nGermany (84M people) has 250,000MW+.\n\nBusiness owners spend billions yearly on generators.\n\nThe hidden tax on every Nigerian enterprise.\n\n⚡ NairaIntel",
        "placeholders": [],
        "category": "infrastructure"
    },
    {
        "text": "The average Nigerian business spends 30-40% of operating costs on diesel for generators.\n\nDiesel today: ₦{diesel}/L (if current data available).\n\nThis invisible cost is baked into every price you pay.\n\n⚡ NairaIntel",
        "placeholders": [],
        "category": "infrastructure"
    },
    {
        "text": "Nigeria loses an estimated $29B annually due to inadequate power supply.\n\nThat is more than the entire federal capital budget.\n\nLight a country and the economy grows. Darken it and it shrinks.\n\nThe math is simple. The solution is not.\n\n⚡ NairaIntel",
        "placeholders": [],
        "category": "infrastructure"
    },

    # ── POPULATION & DEMOGRAPHICS ────────────────────────────────────────────

    {
        "text": "Nigeria's population:\n\n1960: 45M\n1980: 73M\n2000: 123M\n2020: 206M\n{yr}: ~220M+\n\nBy 2050, Nigeria is projected to have 400M people.\n\nEvery economic indicator gets harder to move with more people to serve.\n\n👥 NairaIntel",
        "placeholders": ["yr"],
        "category": "demographics"
    },
    {
        "text": "Nigeria has the youngest population of any major economy.\n\nMedian age: 18 years.\nUSA: 38. Germany: 46. Japan: 49.\n\nYouth is Nigeria's biggest asset — if the economy can absorb them.\n\nUnemployment among under-35s: ~40%.\n\n👥 NairaIntel",
        "placeholders": [],
        "category": "demographics"
    },
    {
        "text": "Nigeria produces ~700,000 university graduates per year.\n\nThe economy creates an estimated 200,000-300,000 formal jobs per year.\n\nThe gap is filled by informal work, emigration, and hustle.\n\nJapa is not a trend. It is a rational response.\n\n👥 NairaIntel",
        "placeholders": [],
        "category": "demographics"
    },

    # ── JAPA / EMIGRATION ────────────────────────────────────────────────────

    {
        "text": "An estimated 1.7M Nigerians applied for UK, US, or Canadian visas in 2023.\n\nThat is roughly the population of a mid-size Nigerian city — every single year.\n\nAt ₦{parallel}/$1, the cost of staying has become the cost of leaving.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "japa"
    },
    {
        "text": "Nigeria loses more doctors to emigration than it trains each year.\n\nA Nigerian doctor earns ~₦400,000/month here.\nThe same doctor earns ~$8,000/month in the UK.\n\nAt ₦{parallel}/$1, that is ₦{doctor_uk_naira:,.0f}/month vs ₦400k.\n\nThe math writes itself.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "japa",
        "custom_calc": "doctor_uk_naira"
    },
    {
        "text": "The word 'Japa' entered mainstream Nigerian vocabulary around 2022.\n\nIt means to flee or escape — Yoruba slang turned national anthem.\n\nIn 2023, over 16,000 Nigerian nurses registered to work abroad.\n\nInflation: {inflation}%. Brain drain: accelerating.\n\n✈️ NairaIntel",
        "placeholders": ["inflation"],
        "category": "japa"
    },

    # ── CBN POLICIES ─────────────────────────────────────────────────────────

    {
        "text": "The CBN has had 6 governors since 2000:\n\nSoludo (2004-2009) — bank consolidation\nSanusi (2009-2014) — exposed NNPC $20B missing\nEmefiele (2014-2023) — naira crash, forex crisis\nCardoso (2023-present) — float and tighten\n\nEach era left its mark.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "cbn"
    },
    {
        "text": "The CBN spent years maintaining a fixed exchange rate.\n\nIn June 2023 it allowed the naira to float.\n\nIn months the naira went from ₦460 to ₦1,500+.\n\nToday: ₦{parallel}/$1.\n\nFixed vs float: both come with a price.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "cbn"
    },
    {
        "text": "The CBN printed ₦22.7 trillion between 2020-2023 to fund government deficits.\n\nThis is widely cited as a key driver of the inflation surge from 15% to 33%.\n\nMoney printing + supply shocks = the inflation we have today: {inflation}%.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "cbn"
    },

    # ── HISTORICAL MILESTONES ────────────────────────────────────────────────

    {
        "text": "The naira was introduced on January 1, 1973.\n\nIt replaced the Nigerian pound at a rate of 2:1.\n\nAt introduction: ₦1 = $1.52.\nToday: ₦{parallel} = $1.\n\n52 years from strength to struggle.\n\n📅 NairaIntel",
        "placeholders": ["parallel"],
        "category": "history"
    },
    {
        "text": "Nigeria's first oil well: Oloibiri, Bayelsa State, 1956.\n\nFirst oil export: 1958.\nJoined OPEC: 1971.\n\nIn 70 years of oil wealth, the naira has gone from ₦0.66/$1 to ₦{parallel}/$1.\n\nOil giveth. Mismanagement taketh away.\n\n🛢 NairaIntel",
        "placeholders": ["parallel"],
        "category": "history"
    },
    {
        "text": "The 1994 Abacha economic crisis:\n\n• Naira crashed from ₦22 to ₦85/dollar on the parallel market\n• Inflation hit 57%\n• Fuel queues stretched for miles\n\nToday: ₦{parallel}/$1. Inflation: {inflation}%.\n\nHistory doesn't repeat — but it rhymes.\n\n📅 NairaIntel",
        "placeholders": ["parallel", "inflation"],
        "category": "history"
    },
    {
        "text": "During the oil boom of the 1970s, Nigeria had a trade surplus and was debt-free.\n\nBy 1986, Nigeria was at the IMF for a structural adjustment loan.\n\n16 years from boom to bust.\n\nOil prices fell. Spending didn't.\n\nSound familiar?\n\n📅 NairaIntel",
        "placeholders": [],
        "category": "history"
    },

    # ── SAVINGS & INVESTMENT ─────────────────────────────────────────────────

    {
        "text": "Nigerian bank savings accounts pay 4-13% interest.\n\nInflation is {inflation}%.\n\nIf your savings earn 10% and inflation is {inflation}%, your real return is {real_return:.1f}%.\n\nNegative. Your money loses value even while growing.\n\n💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "savings",
        "custom_calc": "real_return"
    },
    {
        "text": "A Nigerian who invested ₦1M in NGX equities in January 2020 would have roughly ₦3-4M today in nominal terms.\n\nBut the naira fell {deval_from_2020}% in the same period.\n\nNominal gain. Real loss in dollar terms.\n\nNGX today: {ngx:,}.\n\n📈 NairaIntel",
        "placeholders": ["deval_from_2020", "ngx"],
        "category": "savings"
    },

    # ── PROPERTY & REAL ESTATE ───────────────────────────────────────────────

    {
        "text": "A 3-bedroom flat in Lekki Phase 1, Lagos:\n\n2015: ~₦30M ($152,000)\n2020: ~₦45M ($125,000)\n2023: ~₦80M ($174,000)\n2025: ~₦150M+ ($100,000)\n\nRises in naira. Falls in dollars.\n\nReal estate: hedge or trap?\n\n🏠 NairaIntel",
        "placeholders": [],
        "category": "property"
    },
    {
        "text": "Rent in Lagos has increased 300-500% since 2020 for most areas.\n\nLandlords price in naira — but mentally anchor to dollar replacement cost.\n\nAt ₦{parallel}/$1, rebuilding a house costs more naira each year.\n\nRent inflation is inflation on steroids.\n\n🏠 NairaIntel",
        "placeholders": ["parallel"],
        "category": "property"
    },

    # ── TRADE ────────────────────────────────────────────────────────────────

    {
        "text": "Nigeria imports over $7B in food annually.\n\nRice, wheat, sugar, fish.\n\nAt ₦{parallel}/$1, every imported bag of rice costs {rice_dollar_cost:.0f}% more naira than in 2020 when $1 = ₦360.\n\nThe fork is the frontline of the currency war.\n\n🍚 NairaIntel",
        "placeholders": ["parallel"],
        "category": "trade",
        "custom_calc": "rice_dollar_cost"
    },
    {
        "text": "Nigeria's non-oil exports are less than $5B per year.\n\nOil accounts for over 85% of export earnings.\n\nA country that exports only one thing is one price crash away from crisis.\n\nBrent today: benchmark for everything.\n\n🛢 NairaIntel",
        "placeholders": [],
        "category": "trade"
    },

    # ── ADDITIONAL ENGAGEMENT & THOUGHT PIECES ───────────────────────────────

    {
        "text": "Things ₦1,000 could buy in Nigeria:\n\n2010: 6L petrol + 1kg rice + 2 Indomie\n2020: 6L petrol or 1kg rice\n2023: 1.6L petrol\nToday: {litres_per_1k:.1f}L petrol\n\nSame note. Shrinking world.\n\n💸 NairaIntel",
        "placeholders": ["petrol"],
        "category": "engagement",
        "custom_calc": "litres_per_1k"
    },
    {
        "text": "The most searched financial terms in Nigeria in 2024:\n\n1. Dollar to naira today\n2. How to send money to Nigeria\n3. BTC to naira\n4. Best dollar savings account Nigeria\n5. How to invest in dollars\n\nSearch trends = economic anxiety made visible.\n\n$1 = ₦{parallel} today.\n\n💭 NairaIntel",
        "placeholders": ["parallel"],
        "category": "engagement"
    },
    {
        "text": "The IMF forecasts Nigeria's economy will grow 3.2% in {yr}.\n\nBut with inflation at {inflation}% and population growth at 2.4%, real per-capita growth is near zero.\n\nGrowing — but not fast enough to feel it.\n\n📊 NairaIntel",
        "placeholders": ["inflation", "yr"],
        "category": "gdp"
    },
    {
        "text": "Nigeria's tax-to-GDP ratio is about 6%.\n\nThe global average is 15%.\nSouth Africa: 26%.\nUK: 33%.\n\nA government that can't collect tax can't build infrastructure.\n\nInflation fills the gap instead.\n\nToday: {inflation}%.\n\n💸 NairaIntel",
        "placeholders": ["inflation"],
        "category": "fiscal"
    },
    {
        "text": "Nigeria introduced Treasury Bills in 1960.\n\nToday 91-day T-Bills yield around 18-22%.\n\nInflation: {inflation}%.\n\nReal yield: roughly {tbill_real:.1f}%.\n\nGovernment borrowing at inflation-beating rates. Citizens earning less.\n\n💸 NairaIntel",
        "placeholders": ["inflation"],
        "category": "fiscal",
        "custom_calc": "tbill_real"
    },
]


def get_fact_count():
    return len(FACTS)


def get_facts_by_category(category):
    return [i for i, f in enumerate(FACTS) if f["category"] == category]


def get_categories():
    return list(set(f["category"] for f in FACTS))


def render_fact(index, live_data):
    """
    Render a fact template with live data values.
    Returns the formatted tweet text, or None if rendering fails.
    """
    if index >= len(FACTS):
        return None

    fact = FACTS[index]
    template = fact["text"]

    # Build substitution dict from live_data
    parallel  = live_data.get("parallel", 1499)
    inflation = live_data.get("inflation", 33.2)
    petrol    = live_data.get("petrol", 897)
    ngx       = live_data.get("ngx", 104520)
    yr        = live_data.get("yr", 2026)
    salary_usd = live_data.get("salary_usd", 333)

    # Pre-computed dynamic values
    deval_pct       = round(((parallel - 0.66) / 0.66) * 100, 1)
    deval_from_2015 = round(((parallel - 197) / 197) * 100, 1)
    deval_from_2020 = round(((parallel - 360) / 360) * 100, 1)
    deval_from_2023 = round(((parallel - 460) / 460) * 100, 1)
    petrol_cost_50L = 50 * petrol
    inflation_vs_target = round(inflation / 9, 1)
    real_return     = round(11 - inflation, 1)   # assuming 11% savings rate
    tbill_real      = round(20 - inflation, 1)   # assuming 20% T-bill yield
    inflation_erosion = round(100000 * (1 - (1 / (1 + inflation/100))), 0)

    # Custom calcs
    litres_per_1k   = round(1000 / petrol, 2) if petrol else 0
    min_wage_usd    = round(70000 / parallel, 1) if parallel else 0
    parallel_500    = round(500 * parallel, 0)
    parallel_1000   = round(1000 * parallel, 0)
    doctor_uk_naira = round(8000 * parallel, 0)
    external_debt_ngn = round(42.3 * parallel / 1000, 2)   # in trillions
    remittance_ngn  = round(20 * parallel / 1000, 1)       # $20B in trillions
    paystack_deval  = round(((parallel - 360) / 360) * 100, 1)
    poverty_line_naira = round(2.15 * parallel, 0)
    rice_dollar_cost = round(((parallel - 360) / 360) * 100, 1)
    lpg_per_kg      = live_data.get("lpg_kg", 1200)

    subs = {
        "parallel":            parallel,
        "cbn":                 live_data.get("cbn", 1346),
        "inflation":           inflation,
        "petrol":              petrol,
        "ngx":                 ngx,
        "yr":                  yr,
        "salary_usd":          salary_usd,
        "deval_pct":           deval_pct,
        "deval_from_2015":     deval_from_2015,
        "deval_from_2020":     deval_from_2020,
        "deval_from_2023":     deval_from_2023,
        "petrol_cost_50L":     petrol_cost_50L,
        "inflation_vs_target": inflation_vs_target,
        "real_return":         real_return,
        "tbill_real":          tbill_real,
        "inflation_erosion":   inflation_erosion,
        "litres_per_1k":       litres_per_1k,
        "min_wage_usd":        min_wage_usd,
        "parallel_500":        parallel_500,
        "parallel_1000":       parallel_1000,
        "doctor_uk_naira":     doctor_uk_naira,
        "external_debt_ngn":   external_debt_ngn,
        "remittance_ngn":      remittance_ngn,
        "paystack_deval":      paystack_deval,
        "poverty_line_naira":  poverty_line_naira,
        "rice_dollar_cost":    rice_dollar_cost,
        "lpg_per_kg":          lpg_per_kg,
        "diesel":              live_data.get("diesel", 1450),
    }

    try:
        rendered = template.format_map(subs)
        return rendered
    except KeyError as e:
        print(f"[WARN] facts_pool: missing key {e} in fact {index}")
        return None
