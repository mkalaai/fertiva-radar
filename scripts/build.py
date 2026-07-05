"""
build.py
Reads data/events.json and injects it into index.template.html
to produce the final index.html served by GitHub Pages.
"""

import json
import os
import sys
from datetime import date

TEMPLATE_FILE = "index.template.html"
OUTPUT_FILE   = "index.html"
EVENTS_FILE   = "data/events.json"
UPDATE_FILE   = "data/last_update.json"

def main():
    # Load events
    if not os.path.exists(EVENTS_FILE):
        print(f"Error: {EVENTS_FILE} not found. Run update_events.py first.")
        sys.exit(1)

    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)

    # Load update metadata
    last_update = date.today().isoformat()
    if os.path.exists(UPDATE_FILE):
        with open(UPDATE_FILE, "r") as f:
            meta = json.load(f)
            last_update = meta.get("updated", last_update)

    # Load template
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: {TEMPLATE_FILE} not found.")
        sys.exit(1)

    with open(TEMPLATE_FILE, "r") as f:
        template = f.read()

    # Inject events JSON and metadata
    events_json = json.dumps(events, ensure_ascii=False)
    
    output = template.replace(
        "/* %%EVENTS_DATA%% */",
        f"const EVENTS = {events_json};"
    ).replace(
        "%%LAST_UPDATED%%",
        last_update
    ).replace(
        "%%EVENT_COUNT%%",
        str(len(events))
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write(output)

    print(f"✅ Built {OUTPUT_FILE} with {len(events)} events (last updated: {last_update})")

if __name__ == "__main__":
    main()
