# Fertiva Event Radar 🏥

An auto-updating healthcare conference and award tracker for **Fertiva Pro** GTM strategy.

Every Sunday, a GitHub Actions bot uses Claude AI + web search to find new healthcare events in India and automatically updates the site.

**Live URL:** `https://YOUR-USERNAME.github.io/fertiva-radar`

---

## 🚀 One-Time Setup (10 minutes)

### Step 1: Create the repository

1. Go to [github.com](https://github.com) → click **New repository**
2. Name it: `fertiva-radar`
3. Set to **Public** (required for free GitHub Pages)
4. Click **Create repository**

### Step 2: Upload all files

Upload this entire folder structure to your repo:
```
fertiva-radar/
├── .github/
│   └── workflows/
│       └── update-events.yml
├── data/
│   └── events.json
├── scripts/
│   ├── update_events.py
│   └── build.py
├── index.template.html
├── index.html              ← pre-built, served immediately
└── README.md
```

**Easiest way:** Drag and drop all files into the GitHub web UI, or use:
```bash
git init
git add .
git commit -m "Initial deploy"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/fertiva-radar.git
git push -u origin main
```

### Step 3: Add your Anthropic API key

1. In your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: your Anthropic API key (get one at console.anthropic.com)
5. Click **Add secret**

### Step 4: Enable GitHub Pages

1. In your repo → **Settings** → **Pages**
2. Under **Source** → select **Deploy from a branch**
3. Branch: `main` | Folder: `/ (root)`
4. Click **Save**

Wait ~2 minutes, then visit: `https://YOUR-USERNAME.github.io/fertiva-radar`

### Step 5: Test the automation (optional)

1. Go to **Actions** tab in your repo
2. Click **Update Fertiva Events**
3. Click **Run workflow** → **Run workflow**
4. Watch it run live — takes ~2–3 minutes

---

## 🔄 How Auto-Update Works

```
Every Sunday 6:00 AM IST
       ↓
GitHub Actions triggers
       ↓
Claude API searches the web for new healthcare events
       ↓
New events merged into data/events.json
       ↓
build.py injects events into index.html
       ↓
Changes committed and pushed automatically
       ↓
GitHub Pages serves updated site instantly
```

**Cost:** Claude API calls cost approximately ₹40–80 per week (52 runs/year ≈ ₹2,500–4,000/year).

---

## ✏️ Manual Event Management

To add or edit events manually without waiting for the bot:

1. Edit `data/events.json` directly on GitHub (click the file → pencil icon)
2. Add your event following the schema below
3. Commit the change
4. The site updates in ~30 seconds

Then run `python3 scripts/build.py` locally (or trigger the workflow manually) to regenerate `index.html`.

### Event Schema

```json
{
  "id": 20260801,
  "name": "Event Name",
  "date": "2026-08-01",
  "dateDisplay": "Aug 1–2, 2026",
  "location": "Venue, City",
  "month": "August 2026",
  "priority": "must-attend",
  "tags": ["t-ivf", "t-si"],
  "about": "2-3 sentence description.",
  "keyFacts": ["fact 1", "fact 2"],
  "participation": [
    {
      "icon": "🎟️",
      "name": "Option name",
      "fee": "FREE or ₹X,XXX",
      "feeClass": "fee-free",
      "detail": "What this includes.",
      "verdict": "do",
      "verdictLabel": "✓ Recommended action",
      "deadline": "Register by DATE",
      "deadlineDate": "2026-07-30"
    }
  ],
  "attendYes": true,
  "reasons": ["Reason 1", "Reason 2"],
  "note": "💡 Action: Next step to take.",
  "urls": [
    { "label": "Button label", "url": "https://url.com", "cls": "btn-primary" }
  ],
  "source": "https://where-you-found-it.com",
  "lastUpdated": "2026-07-05"
}
```

**Priority values:** `must-attend` | `strong-value` | `award` | `situational` | `skip`  
**Tag values:** `t-ivf` | `t-ht` | `t-ai` | `t-si` | `t-gen` | `t-award`  
**Fee class:** `fee-free` | `fee-paid` | `fee-contact`  
**Verdict:** `do` | `consider` | `skip`  
**URL cls:** `btn-primary` | `btn-secondary` | `btn-award`

---

## 📁 File Reference

| File | Purpose |
|------|---------|
| `index.html` | **Live site** — auto-generated, do not edit manually |
| `index.template.html` | HTML template with `%%EVENTS_DATA%%` placeholder |
| `data/events.json` | **Source of truth** for all events — edit this |
| `data/last_update.json` | Auto-generated metadata (update date, counts) |
| `scripts/update_events.py` | Calls Claude API to find new events |
| `scripts/build.py` | Injects events.json into template → index.html |
| `.github/workflows/update-events.yml` | GitHub Actions schedule |

---

## 🛠️ Troubleshooting

**Site not showing up?**  
→ Check Settings → Pages is configured and wait 2–3 minutes after first push.

**Workflow failing?**  
→ Check Actions tab for error logs. Most common issue: `ANTHROPIC_API_KEY` secret not set.

**Events not updating?**  
→ Trigger manually via Actions → Update Fertiva Events → Run workflow.

**Want to change the update schedule?**  
→ Edit `.github/workflows/update-events.yml` → change the cron expression.  
→ `30 0 * * 0` = Every Sunday 6:00 AM IST  
→ `30 0 * * 1` = Every Monday 6:00 AM IST

---

Built for **Fertiva Pro** by HumanITech, Coimbatore.
