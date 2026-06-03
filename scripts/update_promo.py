#!/usr/bin/env python3
import json, os, subprocess, sys
from datetime import datetime
from html import escape

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BADGES = ["LATEST EPISODES", "NEW RELEASES", "NOW AIRING", "EPISODES"]

def pick_badge():
    return BADGES[datetime.now().toordinal() % len(BADGES)]

def get_all():
    result = subprocess.run(
        [sys.executable, os.path.join(REPO, "scripts", "get_latest.py")],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    data = json.loads(result.stdout)
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(data["error"])
    return data

def thumb_style():
    return "width:44px;height:44px;object-fit:cover;border-radius:6px;flex-shrink:0"

def generate(items):
    if not items:
        raise RuntimeError("No items to promote")
    hero = items[0]
    rest = items[1:6]
    hero_title = escape(hero["title"])
    hero_ep = hero["episode"]
    hero_img = escape(hero["snapshot"])
    badge = pick_badge()
    label = f"{hero_title} &ndash; Episode {hero_ep}"
    desc = f"Episode {hero_ep} of {hero_title} is now available to stream in widescreen HD on Android TV, Firestick, or Mobile. Zero ads."

    thumbs = ""
    for r in rest:
        t = escape(r["title"])
        ep = r["episode"]
        img = escape(r["snapshot"])
        thumbs += f"""        <div style="display:flex;align-items:center;gap:10px;padding:6px 0">
            <img src="{img}" alt="{t}" style="{thumb_style()}" loading="lazy">
            <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:0.8rem;line-height:1.3;color:var(--text)">{t}</div>
                <div style="font-size:0.72rem;color:var(--text-muted)">Episode {ep}</div>
            </div>
        </div>"""

    return f"""<div class="promo-card">
    <div class="promo-badge">{badge}</div>
    <a href="#download" style="display:block;text-decoration:none;color:inherit">
        <div>
            <img src="{hero_img}" alt="{label}" style="width:100%;max-height:220px;object-fit:cover;border-radius:10px;margin-bottom:8px" loading="lazy">
            <span class="promo-meta"><i aria-hidden="true" class="fa-solid fa-fire"></i> New Release</span>
            <h3 style="margin-bottom:4px">{label}</h3>
            <p style="font-size:0.82rem;margin-bottom:10px">{desc}</p>
        </div>
        <div style="padding-top:8px;border-top:1px solid var(--border)">
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);margin-bottom:4px">Latest Episodes</div>
{thumbs}        </div>
    </a>
    <a href="#download" class="promo-btn" style="margin-top:12px"><i aria-hidden="true" class="fa-solid fa-play"></i> Watch All Latest Episodes</a>
</div>"""

def write(html):
    path = os.path.join(REPO, "promo.html")
    header = f"""<!--
  DYNAMIC PROMO CARD (Auto-generated daily)
  =========================================
  Generated at {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}.
  Do not edit manually.
-->
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + html + "\n")

def main():
    try:
        items = get_all()
        promo = generate(items)
        write(promo)
        print(json.dumps({"status": "ok", "count": len(items)}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
