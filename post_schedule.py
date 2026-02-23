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
TEXT_POST_HOURS = [6, 9, 11, 14, 16, 18, 21, 23]

# Which content type runs at each hour
HOUR_TO_TYPE = {
    6:  "A",
    9:  "B",
    11: "C",
    14: "A",
    16: "B",
    18: "C",
    21: "A",
    23: "B",
}

# Which A-fact categories run at which slots (for variety)
# 3 Type A slots per day — morning, afternoon, evening
SLOT_CATEGORIES = {
    6:  ["devaluation", "history", "wages", "comparison", "fiscal"],
    14: ["fuel", "oil", "gdp", "debt", "trade", "agriculture"],
    21: ["engagement", "crypto", "fintech", "banking", "japa", "demographics"],
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


def is_text_post_hour(hour=None):
    """Returns True if the current WAT hour is a text post slot."""
    if hour is None:
        hour = datetime.datetime.now().hour
    return hour in TEXT_POST_HOURS


def get_slot_type(hour=None):
    """Returns 'A', 'B', or 'C' for the given hour, or None if not a text post slot."""
    if hour is None:
        hour = datetime.datetime.now().hour
    return HOUR_TO_TYPE.get(hour)


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
