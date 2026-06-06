#!/usr/bin/env python3
import json, os, subprocess, sys, re, requests
from datetime import datetime
from html import escape

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://animepahetv.github.io"
BADGES = ["LATEST EPISODES", "NEW RELEASES", "NOW AIRING", "EPISODES"]

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")

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
    rest = items[1:]
    hero_title = escape(hero["title"])
    hero_ep = hero["episode"]
    hero_img = escape(hero["snapshot"])
    badge = pick_badge()
    label = f"{hero_title} \u2013 Episode {hero_ep}"
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

def extract_facebook_message(promo_html):
    badge_match = re.search(r'<div class="promo-badge">([^<]+)</div>', promo_html)
    badge = badge_match.group(1) if badge_match else "NEW RELEASE"

    hero_title_match = re.search(r'<h3 style="margin-bottom:4px">([^<]+)</h3>', promo_html)
    hero_title = hero_title_match.group(1) if hero_title_match else ""

    titles = re.findall(
        r'<div style="font-weight:700;font-size:0\.8rem;line-height:1\.3;color:var\(--text\)">([^<]+)</div>',
        promo_html
    )

    lines = [f"\u2728 {badge}"]
    if hero_title:
        lines.append(f"\U0001f3ac {hero_title}")
    for t in titles[:4]:
        lines.append(f"\U0001f4fa {t}")

    lines.append(f"\n\U0001f4f1 Stream FREE on Android TV/Firestick:")
    lines.append(f"{SITE_URL}#download")
    lines.append(f"\n#AnimePaheTV #FreeAnime #AndroidTV #AnimeStreaming")
    return "\n".join(lines)

def post_to_facebook(message, image_url=None):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("Missing FB_PAGE_ID or FB_ACCESS_TOKEN - skipping Facebook post")
        return False

    try:
        if image_url:
            url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
            data = {"url": image_url, "message": message, "access_token": FB_ACCESS_TOKEN}
        else:
            url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
            data = {"message": message, "access_token": FB_ACCESS_TOKEN}

        resp = requests.post(url, data=data, timeout=30)
        result = resp.json()
        if "id" in result:
            print(f"Posted to Facebook: {result['id']}")
            return True
        else:
            print(f"Facebook API error: {json.dumps(result)}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return False

def main():
    try:
        items = get_all()
        promo = generate(items)
        write(promo)
        print(json.dumps({"status": "ok", "count": len(items)}))

        if FB_PAGE_ID and FB_ACCESS_TOKEN:
            message = extract_facebook_message(promo)
            hero_img = items[0].get("snapshot") if items else None
            print("Posting to Facebook...")
            post_to_facebook(message, image_url=hero_img)
        else:
            print("Facebook credentials not set - skipping Facebook post")

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()