"""
post_schedule.py — 14-day rotation schedule for NairaIntel text posts.

Schedule: 8 text posts/day at 06, 09, 11, 14, 16, 18, 21, 23 WAT
Image posts (08, 13, 19 WAT) are handled separately by main.py / post.yml

14-day cycle:
  Day 1-14, each day has 8 slots
  Total = 112 slots per cycle

Slot → Content type mapping:
  06:00  Type A  (historical fact)
  09:00  Type B  (live data insight)
  11:00  Type C  (weekly scraped — bank rates / fintech)
  14:00  Type A  (historical fact)
  16:00  Type B  (live data insight)
  18:00  Type C  (weekly scraped — bank charges / rates)
  21:00  Type A  (historical fact — evening, more engagement-focused)
  23:00  Type B  (live data insight)
"""

import datetime
import json
import os

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.json")

# WAT hours that get text posts
TEXT_POST_HOURS = [6, 9, 11, 12, 14, 16, 18, 21, 23]

# Which content type runs at each hour.
# Hours 6 and 23 rotate between their base type and Type D (rate snapshots).
# Hour 21 is Type E (engagement questions).
# Hour 12 is Type F (institutional engagement posts).
# Actual type resolved dynamically by get_slot_type() using cycle day.
HOUR_TO_TYPE = {
    6:  "A",   # odd cycle days → D (rate snapshot), even → A (fact)
    9:  "B",
    11: "C",
    12: "F",   # institutional engagement — CBN, NNPC, EFCC, DMO, media bait
    14: "A",
    16: "B",
    18: "C",
    21: "E",   # engagement question every evening
    23: "B",   # odd cycle days → D (rate snapshot), even → B (insight)
}

# Hours that alternate with Type D on odd cycle days
RATE_SNAPSHOT_HOURS = {6, 23}

# Which A-fact categories run at which slots (for variety)
# 3 Type A slots per day — morning, afternoon, evening
SLOT_CATEGORIES = {
    6:  ["devaluation", "history", "wages", "comparison", "fiscal"],
    14: ["fuel", "oil", "gdp", "debt", "trade", "agriculture"],
    21: ["engagement", "crypto", "fintech", "banking", "japa", "demographics"],
}

# Which F-fact categories prefer at which slots (for variety)
# Can be extended if more F slots are added
F_SLOT_CATEGORIES = {
    12: ["cbn_policy", "nnpc_oil", "efcc_recovery", "dmo_debt",
         "firs_revenue", "sec_markets", "media_amplifier",
         "institutional", "praise_milestone"],
}


def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_cycle_day():
    """
    Returns which day (1-14) of the 14-day cycle today is.
    Anchored to a fixed epoch date stored in cache.
    If not set, sets it to today as day 1.
    """
    cache = load_cache()
    epoch_str = cache.get("text_post_epoch")

    if not epoch_str:
        # First run — set epoch to today
        today_str = datetime.date.today().isoformat()
        cache["text_post_epoch"] = today_str
        save_cache(cache)
        return 1

    epoch = datetime.date.fromisoformat(epoch_str)
    today = datetime.date.today()
    days_elapsed = (today - epoch).days
    cycle_day = (days_elapsed % 14) + 1   # 1-indexed, 1 to 14
    return cycle_day


def resolve_slot(now_wat=None, force_hour=None):
    """
    Returns (should_post, slot_hour) where:
      - should_post: True if we are within the posting window of a scheduled slot
      - slot_hour:   the canonical slot hour to use for content-type lookup

    Logic:
      GitHub Actions crons can fire up to ~30 min late, occasionally more.
      We allow up to 90 minutes after a slot's scheduled time.
      This means if the 21:00 WAT slot fires at 22:29 WAT we still post —
      but if it fires at 22:30+ we skip (too close to the 23:00 slot).

    Also guards against double-posting: the cache tracks the last slot posted
    per day, so even if a cron fires twice we won't post the same slot twice.
    """
    if force_hour is not None:
        # Manual override — trust it completely
        slot_hour = int(force_hour)
        return (slot_hour in TEXT_POST_HOURS), slot_hour

    if now_wat is None:
        WAT = datetime.timezone(datetime.timedelta(hours=1))
        now_wat = datetime.datetime.now(tz=WAT)

    current_minutes = now_wat.hour * 60 + now_wat.minute

    best_slot = None
    best_delta = None

    for slot_hour in TEXT_POST_HOURS:
        slot_minutes = slot_hour * 60
        delta = current_minutes - slot_minutes   # positive = we're past the slot

        # Only consider slots we're AFTER (delta >= 0) and within 60 min
        if 0 <= delta <= 60:
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_slot = slot_hour

    if best_slot is None:
        return False, None

    return True, best_slot


def is_text_post_hour(hour=None, now_wat=None):
    """Returns True if current time is within posting window of a slot.
    Pass hour to use legacy exact-match behaviour (e.g. for force_hour).
    """
    if hour is not None:
        return hour in TEXT_POST_HOURS
    should_post, _ = resolve_slot(now_wat=now_wat)
    return should_post


def get_slot_type(hour=None, now_wat=None, cache=None):
    """Returns 'A', 'B', 'C', 'D', or 'E' for the resolved slot, or None.

    Hours in RATE_SNAPSHOT_HOURS alternate between base type and Type D:
      - Odd cycle days  → Type D (rate snapshot)
      - Even cycle days → base type (A or B)
    """
    if hour is None:
        _, hour = resolve_slot(now_wat=now_wat)
    if hour is None:
        return None
    base = HOUR_TO_TYPE.get(hour)
    if base in ("E", "F"):
        return base
    if hour in RATE_SNAPSHOT_HOURS:
        cycle_day = get_cycle_day()
        if cycle_day % 2 == 1:   # odd day → rate snapshot
            return "D"
    return base


def get_next_fact_index(cache, preferred_categories=None):
    """
    Pick the next unused Type A fact index from the pool.
    Avoids repeating facts within a 14-day window.
    Prefers facts from preferred_categories if supplied.
    """
    from facts_pool import FACTS, get_facts_by_category

    used = set(cache.get("text_post_used_facts", []))
    total = len(FACTS)

    # Build candidate list
    if preferred_categories:
        candidates = []
        for cat in preferred_categories:
            candidates.extend(get_facts_by_category(cat))
        # Remove used ones
        candidates = [i for i in candidates if i not in used]
        # If all preferred are used, open to all unused
        if not candidates:
            candidates = [i for i in range(total) if i not in used]
    else:
        candidates = [i for i in range(total) if i not in used]

    # If everything used, reset and start over
    if not candidates:
        cache["text_post_used_facts"] = []
        candidates = list(range(total))

    # Pick first available (deterministic — avoids randomness for reproducibility)
    chosen = candidates[0]
    used_list = cache.get("text_post_used_facts", [])
    used_list.append(chosen)
    cache["text_post_used_facts"] = used_list
    return chosen


def get_type_b_template_index(cache, hour):
    """
    Pick the next Type B template for the given hour slot.
    Rotates through templates without repeating the same one within 7 days.
    """
    key = f"text_post_b_idx_{hour}"
    used = cache.get("text_post_used_b", [])
    from text_poster import TYPE_B_TEMPLATES
    total = len(TYPE_B_TEMPLATES)
    candidates = [i for i in range(total) if i not in used]
    if not candidates:
        cache["text_post_used_b"] = []
        candidates = list(range(total))
    chosen = candidates[0]
    used_b = cache.get("text_post_used_b", [])
    used_b.append(chosen)
    cache["text_post_used_b"] = used_b
    return chosen


def get_type_c_template_index(cache, hour):
    """
    Pick the next Type C template for the given hour slot.
    Type C posts alternate between bank charges and savings rates.
    """
    from text_poster import TYPE_C_TEMPLATES
    total = len(TYPE_C_TEMPLATES)
    used = cache.get("text_post_used_c", [])
    candidates = [i for i in range(total) if i not in used]
    if not candidates:
        cache["text_post_used_c"] = []
        candidates = list(range(total))
    chosen = candidates[0]
    used_c = cache.get("text_post_used_c", [])
    used_c.append(chosen)
    cache["text_post_used_c"] = used_c
    return chosen


def get_next_f_index(cache, preferred_categories=None):
    """
    Pick the next unused Type F fact index from the pool.
    Avoids repeating posts within a 14-day window.
    Prefers posts from preferred_categories if supplied.
    """
    from type_f_pool import TYPE_F_FACTS, get_type_f_by_category

    used = set(cache.get("text_post_used_f", []))
    total = len(TYPE_F_FACTS)

    if preferred_categories:
        candidates = []
        for cat in preferred_categories:
            candidates.extend(get_type_f_by_category(cat))
        candidates = [i for i in candidates if i not in used]
        if not candidates:
            candidates = [i for i in range(total) if i not in used]
    else:
        candidates = [i for i in range(total) if i not in used]

    # Full rotation reset
    if not candidates:
        cache["text_post_used_f"] = []
        candidates = list(range(total))

    chosen = candidates[0]
    used_list = cache.get("text_post_used_f", [])
    used_list.append(chosen)
    cache["text_post_used_f"] = used_list
    return chosen
