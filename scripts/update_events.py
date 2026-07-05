"""
update_events.py
Calls Claude API with web search to find new healthcare events in India
relevant to Fertiva Pro (IVF clinic management SaaS).
Merges new events into data/events.json, preserving existing ones.
"""

import json
import os
import sys
from datetime import datetime, date
import anthropic

# ── Config ────────────────────────────────────────────────────────────────────
EVENTS_FILE = "data/events.json"
TODAY = date.today().isoformat()
CURRENT_YEAR = date.today().year
NEXT_YEAR = CURRENT_YEAR + 1

SEARCH_PROMPT = f"""
Today is {TODAY}. You are a research assistant for Muthu, the solo founder of 
Fertiva Pro — an AI-powered IVF clinic management SaaS platform built in India 
(Coimbatore, Tamil Nadu). Fertiva Pro is a B2B software sold to standalone IVF 
clinics and fertility centres across India.

Your task: Search the web and find ALL upcoming healthcare events, conferences, 
expos, awards, and competitions in India (and occasionally globally) that are 
relevant to Fertiva Pro's GTM strategy. Look for events from today ({TODAY}) 
through the next 12 months.

SEARCH FOR:
1. IVF / fertility / ART / reproductive medicine conferences in India (ISAR, IFS, 
   FOGSI, regional chapters)
2. Healthcare IT / HealthTech / digital health summits and expos in India
3. Medical equipment exhibitions in India (Medicall cities, India Med Expo, India Health)
4. Healthcare startup awards and competitions in India (Medverse, DPIIT NSA, 
   Medicall Innovation Award, GDHS Innovation Award, etc.)
5. Hospital management and growth summits (Medverse, CII health, FICCI health)
6. Any new IVF/fertility specific awards or innovation challenges

FOR EACH EVENT FIND:
- Exact name, dates, location, city
- Official website URL
- Registration/application deadlines
- Participation options (visitor fee, delegate fee, stall/exhibit cost, award application fee)
- Whether it's free or paid, and approximate costs in INR
- Priority recommendation for Fertiva Pro (must-attend / strong-value / award / situational / skip)

Return ONLY a valid JSON array. No markdown, no explanation, no backticks.
Each event must follow EXACTLY this schema:

[
  {{
    "id": <unique integer, use timestamp-based: YYYYMMDD + 2-digit sequence>,
    "name": "Full Event Name",
    "date": "YYYY-MM-DD",
    "dateDisplay": "Mon DD–DD, YYYY",
    "location": "Venue, City",
    "month": "Month YYYY",
    "priority": "must-attend|strong-value|award|situational|skip",
    "tags": ["t-ivf"|"t-ht"|"t-ai"|"t-si"|"t-gen"|"t-award"],
    "about": "2-3 sentence description of the event.",
    "keyFacts": ["fact 1", "fact 2", "fact 3"],
    "participation": [
      {{
        "icon": "🎟️",
        "name": "Option name (e.g. Visitor Entry)",
        "fee": "FREE or ₹X,XXX",
        "feeClass": "fee-free|fee-paid|fee-contact",
        "detail": "What this includes and how to register.",
        "verdict": "do|consider|skip",
        "verdictLabel": "✓ Recommended action|⚠ Consider if...|✗ Skip because...",
        "deadline": "Register by DATE or null",
        "deadlineDate": "YYYY-MM-DD or null"
      }}
    ],
    "attendYes": true,
    "reasons": [
      "Reason 1 why Fertiva Pro should attend/apply",
      "Reason 2"
    ],
    "note": "💡 Action: Specific next step Muthu should take TODAY.",
    "urls": [
      {{
        "label": "Button label",
        "url": "https://official-url.com",
        "cls": "btn-primary|btn-secondary|btn-award"
      }}
    ],
    "source": "where you found this (URL)",
    "lastUpdated": "{TODAY}"
  }}
]

IMPORTANT RULES:
- Only include events from {TODAY} onwards (no past events)
- Only events in India unless it's an award/competition Fertiva Pro can apply to remotely
- Be specific about fees — if unknown write "Contact organiser" 
- If a stall/exhibit fee is very high (>₹2L) for a general audience event, mark verdict as "skip"
- IVF/fertility specific events always get priority "must-attend" or "strong-value"
- Award competitions with free/low application fees always get "do" verdict
- Include at least 8 events, maximum 20 events
- All dates must be in the future relative to {TODAY}
- Ensure JSON is valid — no trailing commas, properly escaped strings
"""

def load_existing_events():
    if not os.path.exists(EVENTS_FILE):
        return []
    with open(EVENTS_FILE, "r") as f:
        return json.load(f)

def merge_events(existing, new_events):
    """
    Merge new events into existing list.
    - Remove events whose date has passed
    - Add new events not already present (matched by name similarity)
    - Keep manually curated events that weren't found by search
    """
    today = date.today()

    # Remove past events
    active_existing = []
    removed = []
    for e in existing:
        try:
            event_date = date.fromisoformat(e["date"])
            if event_date >= today:
                active_existing.append(e)
            else:
                removed.append(e["name"])
        except (KeyError, ValueError):
            active_existing.append(e)  # keep if date is malformed

    if removed:
        print(f"Removed {len(removed)} past events: {', '.join(removed)}")

    # Find new events not already in existing (by name similarity)
    existing_names = {e["name"].lower().strip() for e in active_existing}
    truly_new = []
    for ne in new_events:
        name_lower = ne["name"].lower().strip()
        # Check for substring match to catch slight name variations
        is_duplicate = any(
            name_lower in ex or ex in name_lower
            for ex in existing_names
        )
        if not is_duplicate:
            truly_new.append(ne)
            print(f"  ✅ NEW EVENT FOUND: {ne['name']}")

    if not truly_new:
        print("No new events found this week.")
    else:
        print(f"Adding {len(truly_new)} new events.")

    # Combine and sort by date
    merged = active_existing + truly_new
    merged.sort(key=lambda e: e.get("date", "9999-99-99"))

    # Update lastUpdated for new events
    for e in truly_new:
        e["lastUpdated"] = TODAY

    return merged, len(truly_new), len(removed)

def call_claude_for_events(client):
    print("Calling Claude API with web search...")
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": SEARCH_PROMPT}]
    )

    # Extract text content from response
    full_text = ""
    for block in response.content:
        if block.type == "text":
            full_text += block.text

    if not full_text.strip():
        print("Warning: Claude returned no text content.")
        return []

    # Parse JSON — strip any accidental markdown
    text = full_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    # Find JSON array
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        print(f"Warning: No JSON array found in response. Raw response snippet:\n{text[:500]}")
        return []

    json_str = text[start:end]
    
    try:
        events = json.loads(json_str)
        print(f"Claude returned {len(events)} events.")
        return events
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Problematic JSON snippet:\n{json_str[:500]}")
        return []

def validate_event(e):
    """Basic validation — ensure required fields exist."""
    required = ["id", "name", "date", "location", "priority", "about", "participation"]
    for field in required:
        if field not in e:
            return False, f"Missing field: {field}"
    
    # Validate date format
    try:
        date.fromisoformat(e["date"])
    except ValueError:
        return False, f"Invalid date: {e['date']}"
    
    # Validate priority
    valid_priorities = {"must-attend", "strong-value", "award", "situational", "skip"}
    if e["priority"] not in valid_priorities:
        return False, f"Invalid priority: {e['priority']}"
    
    return True, "ok"

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load existing events
    existing = load_existing_events()
    print(f"Loaded {len(existing)} existing events from {EVENTS_FILE}")

    # Get new events from Claude
    new_events_raw = call_claude_for_events(client)

    # Validate new events
    valid_new = []
    for e in new_events_raw:
        ok, reason = validate_event(e)
        if ok:
            valid_new.append(e)
        else:
            print(f"  ⚠ Skipping invalid event '{e.get('name', 'unknown')}': {reason}")

    print(f"Valid new events from Claude: {len(valid_new)}")

    # Merge
    merged, added, removed = merge_events(existing, valid_new)
    print(f"Final event count: {len(merged)} (added: {added}, removed: {removed})")

    # Save
    os.makedirs("data", exist_ok=True)
    with open(EVENTS_FILE, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(merged)} events to {EVENTS_FILE}")

    # Write a summary for the commit message
    with open("data/last_update.json", "w") as f:
        json.dump({
            "updated": TODAY,
            "total": len(merged),
            "added": added,
            "removed": removed
        }, f, indent=2)

if __name__ == "__main__":
    main()
