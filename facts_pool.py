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

    # ── NAIRA MILESTONES (more) ───────────────────────────────────────────────

    {
        "text": "The naira was once so strong that Nigerians studying in the UK sent money BACK home.\n\nIn 1980 ₦1 = $1.52.\n\nToday ₦{parallel:,.0f} = $1.\n\nA complete reversal in one generation.\n\n📉 NairaIntel",
        "placeholders": ["parallel"],
        "category": "devaluation"
    },
    {
        "text": "The first time Nigeria officially devalued the naira was 1986 under IBB's structural adjustment.\n\nThe official rate went from ₦0.89/$ to ₦4/$.\n\nBy {yr} it stands at ₦{parallel:,.0f}/$.\n\nEvery adjustment promised growth. Most delivered pain first.\n\n📉 NairaIntel",
        "placeholders": ["parallel", "yr"],
        "category": "devaluation"
    },
    {
        "text": "Nigeria has had more currency crises than most African nations.\n\n1986. 1992. 1999. 2008. 2015. 2016. 2020. 2023. 2024.\n\nEach one blamed on oil prices, politics, or speculators.\n\nEach one paid for by ordinary Nigerians.\n\n$1 = ₦{parallel:,.0f} today.\n\n📉 NairaIntel",
        "placeholders": ["parallel"],
        "category": "devaluation"
    },
    {
        "text": "In June 2023, the CBN unified Nigeria's exchange rate windows.\n\nWithin 48 hours, ₦460 became ₦750.\n\nWithin 6 months, it was ₦1,500.\n\nToday: ₦{parallel:,.0f}.\n\nUnification was the right call. The transition cost millions their savings.\n\n📉 NairaIntel",
        "placeholders": ["parallel"],
        "category": "devaluation"
    },

    # ── PETROL (more) ─────────────────────────────────────────────────────────

    {
        "text": "Nigeria is Africa's largest oil producer.\n\nYet for 60 years it imported refined petrol.\n\nThe irony: crude oil pumped from Nigerian soil, shipped abroad, refined, shipped back, sold to Nigerians.\n\nDangote Refinery is the attempted fix.\n\nPetrol today: ₦{petrol:,}/L.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },
    {
        "text": "Nigeria spent ₦9.7 trillion on petrol subsidy in 2022 alone.\n\nThat is:\n— 3x the health budget\n— 4x the education budget\n— More than all infrastructure spending combined\n\nSubsidy removed June 2023.\nPetrol now: ₦{petrol:,}/L.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },
    {
        "text": "When petrol subsidy ended in June 2023, Nigerians were told prices would settle.\n\nPetrol was ₦185/L.\nIt hit ₦617/L within days.\nToday: ₦{petrol:,}/L.\n\nFor a Lagos bus driver spending ₦15,000/day on fuel, this was a pay cut.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },
    {
        "text": "Okada (motorcycle taxi) fares in Lagos roughly tripled between 2022 and 2024.\n\nNot because riders got greedy.\n\nBecause petrol went from ₦185/L to ₦{petrol:,}/L.\n\nEverything connects to the pump price.\n\n⛽ NairaIntel",
        "placeholders": ["petrol"],
        "category": "fuel"
    },

    # ── COMPARISON WITH PEERS (more) ─────────────────────────────────────────

    {
        "text": "GDP per capita comparison — sub-Saharan Africa:\n\n🇳🇬 Nigeria: ~$2,100\n🇬🇭 Ghana: ~$2,400\n🇿🇦 South Africa: ~$6,200\n🇧🇼 Botswana: ~$7,800\n🇰🇪 Kenya: ~$2,100\n\nNigeria — biggest economy. Not richest citizens.\n\nInflation today: {inflation}%.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "comparison"
    },
    {
        "text": "Rwanda's economy has grown every year since 2000, averaging 7% growth.\n\nNigeria's economy has contracted 3 times since 2014.\n\nRwanda: no oil. Strong institutions. Low inflation.\n\nNigeria: abundant oil. Weak institutions. {inflation}% inflation.\n\nResources are not destiny.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "comparison"
    },
    {
        "text": "Ethiopia became one of the world's fastest-growing economies from 2005-2019.\n\nNo oil. No mineral windfall.\n\nJust manufacturing, agriculture, and infrastructure investment.\n\nNigeria earns billions from oil.\nInflation is {inflation}%.\n\nGrowth strategy matters more than resources.\n\n📊 NairaIntel",
        "placeholders": ["inflation"],
        "category": "comparison"
    },
    {
        "text": "Cost of living index (lower = cheaper):\n\n🇳🇬 Lagos: 34\n🇬🇭 Accra: 40\n🇿🇦 Johannesburg: 47\n🇬🇧 London: 78\n🇺🇸 New York: 100\n\nLagos appears cheap — but at ₦{parallel:,.0f}/$1 and {inflation}% inflation, it is expensive on a naira salary.\n\n📊 NairaIntel",
        "placeholders": ["parallel", "inflation"],
        "category": "comparison"
    },

    # ── BANKING (more) ────────────────────────────────────────────────────────

    {
        "text": "Soludo's 2005 bank consolidation reduced Nigerian banks from 89 to 25.\n\nThe goal: stronger, more stable banks.\n\nBy 2009, some of those \"stronger\" banks needed a $4B bailout.\n\nReform is necessary. Execution is everything.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "banking"
    },
    {
        "text": "Nigeria's banking sector holds over ₦100 trillion in assets.\n\nAt ₦{parallel:,.0f}/$1 that is roughly $67B.\n\nFor comparison, JPMorgan alone holds $3.9 trillion in assets.\n\nNigeria's entire banking system is 1.7% of one US bank.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "banking"
    },
    {
        "text": "The average Nigerian uses 2.3 bank accounts.\n\nReason: different accounts for salary, savings, transfers, and crypto.\n\nNot financial sophistication — it is working around the system's limitations.\n\nInflation: {inflation}%. Account holders: finding ways.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "banking"
    },
    {
        "text": "In 2021, Flutterwave processed $9B in transactions.\n\nIn 2022, it was $16B.\n\nBy 2023, over $26B.\n\nNigerian fintech is processing more value annually than some African central banks hold in reserves.\n\n$1 = ₦{parallel:,.0f} and the payment rails keep growing.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "fintech"
    },
    {
        "text": "USSD banking (*737#, *894#, *901# etc.) reached 80M+ Nigerians before smartphones were common.\n\nNigeria built financial inclusion on feature phones, not apps.\n\nToday fintech apps dominate — but USSD still processes billions monthly for the unsmartphoned.\n\n🏦 NairaIntel",
        "placeholders": [],
        "category": "fintech"
    },
    {
        "text": "The CBN introduced BVN (Bank Verification Number) in 2014.\n\n60M+ Nigerians enrolled.\n\nIt was the backbone that made digital banking, fintech, and credit scoring possible.\n\nOne policy. A decade of compounding impact.\n\n$1 = ₦{parallel:,.0f} today.\n\n🏦 NairaIntel",
        "placeholders": ["parallel"],
        "category": "banking"
    },

    # ── CRYPTO & DIGITAL (more) ───────────────────────────────────────────────

    {
        "text": "When the CBN banned crypto in 2021, Nigerians moved to P2P.\n\nBinance P2P Nigeria became one of the busiest P2P markets globally.\n\nThe ban didn't stop crypto — it pushed it underground and made it harder to regulate.\n\nP2P rate today: ₦{parallel:,.0f}/$1.\n\n₿ NairaIntel",
        "placeholders": ["parallel"],
        "category": "crypto"
    },
    {
        "text": "Nigeria's crypto adoption ranked 2nd globally in 2022 (Chainalysis index).\n\nThis wasn't speculation — it was Nigerians protecting savings from {inflation}% inflation and naira devaluation.\n\nNecessity drives adoption faster than any marketing campaign.\n\n₿ NairaIntel",
        "placeholders": ["inflation"],
        "category": "crypto"
    },
    {
        "text": "USDT (Tether) is effectively Nigeria's second dollar.\n\nMillions of Nigerians hold USDT as a dollar savings account.\n\nNo bank account needed. No CBN approval needed.\n\nAt ₦{parallel:,.0f}/$1, stability has a price — and the market found a way.\n\n₿ NairaIntel",
        "placeholders": ["parallel"],
        "category": "crypto"
    },

    # ── JAPA / EMIGRATION (more) ──────────────────────────────────────────────

    {
        "text": "The UK introduced a Nigeria-specific Graduate visa route in 2021.\n\nApplications from Nigerians rose 600% in two years.\n\nNigeria now sends more students to UK universities than any other African country.\n\nInflation: {inflation}%. Brain drain: accelerating.\n\n✈️ NairaIntel",
        "placeholders": ["inflation"],
        "category": "japa"
    },
    {
        "text": "A Nigerian accountant earns ~₦300,000/month in Lagos.\n\nThe same qualification earns ~£3,500/month in the UK.\n\nAt today's rate: £3,500 = ₦{uk_salary_naira:,.0f}/month.\n\nThat is {uk_multiplier:.0f}x the Nigerian salary.\n\nThe math of Japa is brutal.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "japa",
        "custom_calc": "uk_salary_naira"
    },
    {
        "text": "Canada admitted 23,000+ Nigerian immigrants in 2023.\n\nMore than any year in history.\n\nMost are aged 25-40 — Nigeria's most productive demographic.\n\nEvery departure is ₦{parallel:,.0f}/$1 made real by a one-way ticket.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "japa"
    },
    {
        "text": "The irony of Japa:\n\nNigeria trains doctors, nurses, engineers, accountants.\nThey move abroad.\nThey send remittances back.\nRemittances now exceed $20B/year — more than oil revenue in some quarters.\n\nNigeria exports human capital. Imports dollars.\n\n$1 = ₦{parallel:,.0f}.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "japa"
    },

    # ── DEBT & FISCAL (more) ──────────────────────────────────────────────────

    {
        "text": "Nigeria's federal budget for {yr}:\n\n~₦35 trillion total\n~₦8 trillion debt service\n~₦3 trillion education\n~₦1 trillion health\n\nThe country spends 8x more paying debt than educating its children.\n\nInflation: {inflation}%.\n\n💸 NairaIntel",
        "placeholders": ["inflation", "yr"],
        "category": "debt"
    },
    {
        "text": "Nigeria's debt profile:\n\nDomestic debt: ~₦67 trillion\nExternal debt: ~$42B\n\nAt ₦{parallel:,.0f}/$1, external debt alone = ₦{external_debt_ngn:.1f} trillion.\n\nWhen the naira falls, the dollar debt grows — automatically, without borrowing a kobo more.\n\n💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "debt",
        "custom_calc": "external_debt_ngn"
    },
    {
        "text": "Nigeria borrowed $3.4B from the World Bank in 2023 for development projects.\n\nAt ₦{parallel:,.0f}/$1, repayment in naira will cost far more than the original loan value by maturity.\n\nDollar debt + falling naira = the compounding trap.\n\n💸 NairaIntel",
        "placeholders": ["parallel"],
        "category": "debt"
    },

    # ── POVERTY & INEQUALITY (more) ───────────────────────────────────────────

    {
        "text": "The richest 5 Nigerians have more wealth than the bottom 40% of the population combined.\n\nThat is 90M+ people.\n\nHigh inequality + high inflation ({inflation}%) + currency devaluation = the poorest pay the most.\n\n🔴 NairaIntel",
        "placeholders": ["inflation"],
        "category": "poverty"
    },
    {
        "text": "Access to electricity by country:\n\n🇳🇬 Nigeria: 57% of population\n🇰🇪 Kenya: 75%\n🇬🇭 Ghana: 85%\n🇿🇦 South Africa: 85%\n🇷🇼 Rwanda: 48%\n\nWithout power, businesses can't grow.\nWithout businesses, jobs don't come.\n\nInflation: {inflation}%.\n\n⚡ NairaIntel",
        "placeholders": ["inflation"],
        "category": "infrastructure"
    },
    {
        "text": "Nigeria's informal economy is estimated at 65% of total GDP.\n\nMost workers earn cash. Pay no tax. Access no credit.\n\nThey also feel inflation hardest — no employer benefits, no salary increments.\n\n{inflation}% inflation hits informal workers first and worst.\n\n💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "poverty"
    },

    # ── AGRICULTURE (more) ────────────────────────────────────────────────────

    {
        "text": "Nigeria's rice import bill: over $1B per year.\n\nIrony: the Niger Delta and Middle Belt can grow rice abundantly.\n\nBut poor roads, insecurity, and lack of storage mean imports are cheaper.\n\nAt ₦{parallel:,.0f}/$1 those imports cost more naira every year.\n\n🌾 NairaIntel",
        "placeholders": ["parallel"],
        "category": "agriculture"
    },
    {
        "text": "Tomato price in Lagos, 2024: ₦2,000+ per small basket.\n\nThe same basket was ₦300-500 in 2020.\n\nA 300-400% increase in 4 years.\n\nClimate shocks + naira collapse + rising diesel costs = food inflation that hurts the poorest most.\n\nInflation: {inflation}%.\n\n🍅 NairaIntel",
        "placeholders": ["inflation"],
        "category": "agriculture"
    },
    {
        "text": "In the 1960s Nigeria exported groundnut pyramids that were world-famous.\n\nKano's groundnut pyramids were so large they appeared in National Geographic.\n\nToday Nigeria imports groundnut products.\n\nWhat happened between then and now is the story of oil, neglect, and missed diversification.\n\n🌾 NairaIntel",
        "placeholders": [],
        "category": "agriculture"
    },

    # ── INFRASTRUCTURE (more) ─────────────────────────────────────────────────

    {
        "text": "Lagos to Abuja by road: ~9 hours.\nLagos to Abuja by air: ~1 hour.\n\nThere is no functioning train service between Nigeria's two largest cities.\n\nThe Abuja-Kaduna rail is operational.\nThe Lagos-Ibadan rail is operational.\n\nBut Lagos-Abuja rail? Still a project.\n\nLogistics costs are inflation costs.\n\n🚂 NairaIntel",
        "placeholders": [],
        "category": "infrastructure"
    },
    {
        "text": "Nigeria's road network is 195,000km.\n\nOnly 60,000km is paved.\n\nOnly 40% of that is in good condition.\n\nBad roads = high transport costs.\nHigh transport costs = expensive food.\nExpensive food = inflation.\n\nToday: {inflation}%.\n\n🛣️ NairaIntel",
        "placeholders": ["inflation"],
        "category": "infrastructure"
    },
    {
        "text": "Every Lagos resident spends an average of 3-4 hours in traffic daily.\n\nThat is 750-1,000 hours per year — lost.\n\nEstimated economic cost of Lagos traffic: $9B annually.\n\nThis invisible tax is baked into every Lagos business cost.\n\n$1 = ₦{parallel:,.0f} today.\n\n🚗 NairaIntel",
        "placeholders": ["parallel"],
        "category": "infrastructure"
    },

    # ── DEMOGRAPHICS (more) ───────────────────────────────────────────────────

    {
        "text": "Nigeria will have 400M people by 2050.\n\nThat is more than the entire current population of the United States.\n\nFor context:\n• US GDP: $27 trillion\n• Nigeria's GDP today: ~$253B\n\nThe gap that must close in 25 years is staggering.\n\nInflation today: {inflation}%.\n\n👥 NairaIntel",
        "placeholders": ["inflation"],
        "category": "demographics"
    },
    {
        "text": "Lagos has a population of 15-20M depending on estimate.\n\nIt generates about 25% of Nigeria's entire GDP.\n\nOne city. 25% of the economy.\n\nIf Lagos were a country it would be one of Africa's top 5 economies.\n\n$1 = ₦{parallel:,.0f} today.\n\n👥 NairaIntel",
        "placeholders": ["parallel"],
        "category": "demographics"
    },
    {
        "text": "Nigeria's youth (under 30) make up 60%+ of the population.\n\nThey are the most educated generation in Nigerian history.\n\nThey are also the most likely to leave.\n\nRetaining them requires growth faster than inflation ({inflation}%) and opportunity faster than Japa.\n\n👥 NairaIntel",
        "placeholders": ["inflation"],
        "category": "demographics"
    },

    # ── HISTORY (more) ────────────────────────────────────────────────────────

    {
        "text": "Nigeria had 6 military coups between 1966 and 1993.\n\nEach disrupted economic policy mid-execution.\n\nNo long-term economic plan survived more than one government.\n\nPolitical stability is the foundation all other growth rests on.\n\nInflation today: {inflation}%.\n\n📅 NairaIntel",
        "placeholders": ["inflation"],
        "category": "history"
    },
    {
        "text": "The Nigerian Civil War (1967-1970) killed 1-3M people, mostly from starvation.\n\nThe Biafra blockade created a food crisis that changed Nigeria's relationship with food security forever.\n\nToday food inflation sits well above overall CPI.\n\nThe hunger of the past echoes in the prices of today.\n\n📅 NairaIntel",
        "placeholders": [],
        "category": "history"
    },
    {
        "text": "Nigeria's first economic boom came in the 1970s oil decade.\n\nGDP grew 8-10% annually.\n\nThe government response: import everything, build big, spend fast.\n\nWhen oil prices crashed in 1981, there was nothing left.\n\nBoom without savings = bust without cushion.\n\n$1 = ₦{parallel:,.0f} today.\n\n📅 NairaIntel",
        "placeholders": ["parallel"],
        "category": "history"
    },
    {
        "text": "Operation Feed the Nation launched in 1976 under Obasanjo.\n\nGreen Revolution launched in 1980 under Shagari.\n\nBoth aimed to make Nigeria food self-sufficient.\n\nBoth wound down when oil money returned.\n\nToday Nigeria imports over $7B in food annually.\n\nInflation: {inflation}%.\n\n📅 NairaIntel",
        "placeholders": ["inflation"],
        "category": "history"
    },

    # ── OIL & ENERGY (more) ───────────────────────────────────────────────────

    {
        "text": "Nigeria flares more gas than any other country in Africa.\n\nGas flaring = burning money.\n\nEstimated annual value of flared gas: $2-3B.\n\nAt ₦{parallel:,.0f}/$1 that is ₦{flare_naira:,.0f} trillion burned into the sky every year.\n\n🔥 NairaIntel",
        "placeholders": ["parallel"],
        "category": "oil",
        "custom_calc": "flare_naira"
    },
    {
        "text": "The Petroleum Industry Act (PIA) was signed in 2021 after 20 years of debate.\n\nIt restructured NNPC into NNPC Ltd — a commercial entity.\n\nWhether it delivers on investment is still being decided.\n\nPetrol today: ₦{petrol:,}/L.\n\n🛢 NairaIntel",
        "placeholders": ["petrol"],
        "category": "oil"
    },
    {
        "text": "NNPC Ltd posted its first-ever profit in 2022: $1.07B.\n\nBefore commercialisation, NNPC was famous for losing money despite selling oil.\n\nProfitability is one step. Transparency and reinvestment are the next.\n\nBrent today: the anchor of Nigeria's income.\n\n🛢 NairaIntel",
        "placeholders": [],
        "category": "oil"
    },

    # ── NGX / INVESTMENT (more) ───────────────────────────────────────────────

    {
        "text": "The NGX All-Share Index was 20,730 in January 2010.\n\nIt peaked at 100,000+ in 2024 for the first time.\n\nNominal return over 14 years: ~400%.\n\nBut the naira also fell ~600% in that period.\n\nNGX today: {ngx:,}.\n\nMeasure returns in the currency you spend.\n\n📈 NairaIntel",
        "placeholders": ["ngx"],
        "category": "ngx"
    },
    {
        "text": "Treasury Bills vs inflation — Nigeria edition:\n\n91-day T-Bill yield: ~20%\nCurrent inflation: {inflation}%\nReal yield: {tbill_real:.1f}%\n\nFor once, government paper may actually beat inflation.\n\nBut only if you have large lump sums — minimum entry is typically ₦50M through primary dealers.\n\n💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "savings",
        "custom_calc": "tbill_real"
    },
    {
        "text": "Lagos Stock Exchange (now NGX) listed its first company in 1961.\n\nToday over 155 companies are listed.\n\nMarket cap: ~₦58 trillion.\n\nAt ₦{parallel:,.0f}/$1 that is ~$39B.\n\nFor context, Apple alone is worth $3.4 trillion.\n\nGrowth runway is massive.\n\n📈 NairaIntel",
        "placeholders": ["parallel"],
        "category": "ngx"
    },

    # ── ENGAGEMENT (more) ─────────────────────────────────────────────────────

    {
        "text": "A tale of two strategies:\n\nPerson A: ₦1M in 2020 → kept in naira savings at 10%/yr → ₦1.46M today\nPerson B: ₦1M in 2020 → converted to $ at ₦360 → $2,778 → ₦{converted_ngn:,.0f} today\n\nSame start. Same year. Very different ending.\n\n💭 NairaIntel",
        "placeholders": ["parallel"],
        "category": "engagement",
        "custom_calc": "converted_ngn"
    },
    {
        "text": "The most important financial skill in Nigeria:\n\n1. Earn in naira\n2. Convert to stable asset immediately\n3. Spend naira as needed\n4. Repeat\n\nIt sounds simple.\n\nAt {inflation}% inflation and ₦{parallel:,.0f}/$1, the difference is everything.\n\n💭 NairaIntel",
        "placeholders": ["inflation", "parallel"],
        "category": "engagement"
    },
    {
        "text": "What ₦1,000,000 buys in Nigeria:\n\n2010: A small car\n2015: A decent motorcycle\n2020: A used okada or 6 months rent (Surulere)\n2024: ~1 month rent (mainland Lagos)\nToday: {million_naira_petrol:.0f} litres of petrol\n\n₦1M. Shrinking world.\n\n$1 = ₦{parallel:,.0f}.\n\n💸 NairaIntel",
        "placeholders": ["petrol", "parallel"],
        "category": "engagement",
        "custom_calc": "million_naira_petrol"
    },
    {
        "text": "Nigerians are among the most entrepreneurial people on earth.\n\nOver 40M small businesses operate in Nigeria.\n\nYet most can't access bank credit.\n\nMost operate with generators, water trucks, and private security.\n\nThey thrive despite the system — not because of it.\n\nInflation: {inflation}%.\n\n💪 NairaIntel",
        "placeholders": ["inflation"],
        "category": "engagement"
    },
    {
        "text": "The average Nigerian household spends 56-60% of income on food.\n\nFor comparison: UK households spend ~10%.\n\nWhen food inflation runs at 30%+, a Nigerian family effectively loses 17-18% of ALL their income to food price increases alone.\n\nInflation: {inflation}%.\n\n🍽️ NairaIntel",
        "placeholders": ["inflation"],
        "category": "engagement"
    },
    {
        "text": "Dollars under the mattress in Nigeria are not eccentric — they are rational.\n\n{inflation}% inflation\n₦{parallel:,.0f} to $1\nBank savings at 4-13%\n\nThe naira loses purchasing power faster than most accounts can compensate.\n\nUntil that changes, the mattress stays stacked.\n\n💵 NairaIntel",
        "placeholders": ["inflation", "parallel"],
        "category": "engagement"
    },

    # ── REMITTANCES (more) ────────────────────────────────────────────────────

    {
        "text": "A Nigerian in Canada sending $500 home monthly:\n\n2015: Recipient got ₦98,500\n2020: ₦180,000\n2023: ₦230,000\n2024: ₦750,000\nToday: ₦{remit_500:,.0f}\n\nThe diaspora's naira power has never been stronger.\n\nFor the sender the amount is the same. For the receiver — a lifeline.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "remittances",
        "custom_calc": "remit_500"
    },
    {
        "text": "Western Union and MoneyGram used to dominate Nigeria remittances.\n\nNow Chipper Cash, Lemfi, Grey, and Wise have eaten their lunch.\n\nNigerian fintech didn't just serve the domestic market — it solved diaspora payments globally.\n\n$1 = ₦{parallel:,.0f}.\n\n✈️ NairaIntel",
        "placeholders": ["parallel"],
        "category": "remittances"
    },

    # ── WAGES & PURCHASING POWER (more) ──────────────────────────────────────

    {
        "text": "Nigeria's minimum wage is ₦70,000/month (2024).\n\nCost of living for one adult in Lagos: ₦150,000-250,000/month minimum.\n\nMinimum wage covers ~30-50% of basic survival costs in the city.\n\nThe gap is filled by hustle, family support, and debt.\n\nInflation: {inflation}%.\n\n💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "wages"
    },
    {
        "text": "A civil servant on grade level 10 earns ~₦150,000/month.\n\nAt ₦{parallel:,.0f}/$1 that is ${civil_servant_usd:.0f}/month.\n\nThe UN poverty line is $2.15/day.\n\nA grade level 10 civil servant earns ${civil_servant_usd:.0f}/month.\n\nThey are not poor by the metric. But they cannot afford Lagos.\n\n💰 NairaIntel",
        "placeholders": ["parallel"],
        "category": "wages",
        "custom_calc": "civil_servant_usd"
    },

    # ── CBN / POLICY (more) ───────────────────────────────────────────────────

    {
        "text": "The CBN raised interest rates 9 times between 2022 and 2024.\n\nFrom 11.5% to 27.5%.\n\nTheory: higher rates slow inflation.\nNigerian reality: {inflation}% inflation persists because most of it is supply-side, not demand-driven.\n\nRate hikes alone can't fix supply-side inflation.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "cbn"
    },
    {
        "text": "The CBN's Ways & Means lending to the federal government:\n\n₦22.7 trillion lent 2020-2023.\n\nThis is the central bank printing money to fund government spending.\n\nResult: money supply expanded. Inflation followed.\n\nToday: {inflation}%. The bill arrived.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "cbn"
    },
    {
        "text": "CBN's Monetary Policy Rate (MPR):\n\n2020: 11.5%\n2022: 16.5%\n2023: 18.75%\n2024: 27.5%\n\nInflation today: {inflation}%\n\nReal interest rate: {tbill_real:.1f}%\n\nFor the first time in years, savers who can access T-Bills or money market funds are beating inflation — barely.\n\n🏦 NairaIntel",
        "placeholders": ["inflation"],
        "category": "cbn",
        "custom_calc": "tbill_real"
    },

    # ── PROPERTY (more) ───────────────────────────────────────────────────────

    {
        "text": "Average house price in Lagos vs income:\n\nA modest 2-bedroom in Surulere: ₦30-50M\nAverage formal sector salary: ₦300-500k/month\nMonths to save (100%): 60-166 months\nYears: 5-14 years of full salary saved\n\nAt {inflation}% inflation those savings shrink yearly.\n\nHomeownership in Lagos: a moving target.\n\n🏠 NairaIntel",
        "placeholders": ["inflation"],
        "category": "property"
    },
    {
        "text": "Lagos property prices in dollars are cheaper than they were in 2014.\n\n2014: A Lekki apartment at ₦60M = $375,000 (₦160/$1)\n2025: Same apartment at ₦200M = $133,000 (₦1,500/$1)\n\nFor dollar holders, Nigerian real estate has never been more affordable.\n\nFor naira earners, the naira price is out of reach.\n\n$1 = ₦{parallel:,.0f}.\n\n🏠 NairaIntel",
        "placeholders": ["parallel"],
        "category": "property"
    },

    # ── SAVINGS & INVESTMENT (more) ───────────────────────────────────────────

    {
        "text": "Dollar-denominated investment options in Nigeria:\n\n📈 Risevest (US stocks): ~10% annual return in USD\n📈 Bamboo (US ETFs): market returns in USD\n📈 Trove: US and Nigerian stocks in USD\n\nIn naira terms, any USD gain is amplified by devaluation.\n\n$1 = ₦{parallel:,.0f} today.\n\n💰 NairaIntel",
        "placeholders": ["parallel"],
        "category": "savings"
    },
    {
        "text": "The rule of 72: divide 72 by your annual return to find how many years to double your money.\n\nPiggyVest at 13%: doubles in 5.5 years\nBut inflation at {inflation}%: halves your purchasing power in {inflation_half:.1f} years\n\nYour money is in a race it may not be winning.\n\n💰 NairaIntel",
        "placeholders": ["inflation"],
        "category": "savings",
        "custom_calc": "inflation_half"
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
    uk_salary_naira = round(3500 * parallel, 0)
    uk_multiplier   = round(uk_salary_naira / 300000, 1)
    flare_naira     = round(2.5 * parallel / 1000, 2)
    converted_ngn   = round(2778 * parallel, 0)
    million_naira_petrol = round(1000000 / petrol, 1) if petrol else 0
    remit_500       = round(500 * parallel, 0)
    civil_servant_usd = round(150000 / parallel, 1) if parallel else 0
    inflation_half  = round(72 / inflation, 1) if inflation else 0
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
        "uk_salary_naira":     uk_salary_naira,
        "uk_multiplier":       uk_multiplier,
        "flare_naira":         flare_naira,
        "converted_ngn":       converted_ngn,
        "million_naira_petrol": million_naira_petrol,
        "remit_500":           remit_500,
        "civil_servant_usd":   civil_servant_usd,
        "inflation_half":      inflation_half,
    }

    try:
        rendered = template.format_map(subs)
        return rendered
    except KeyError as e:
        print(f"[WARN] facts_pool: missing key {e} in fact {index}")
        return None
