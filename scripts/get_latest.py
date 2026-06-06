import asyncio, json, sys, re
from datetime import datetime, timezone
from playwright.async_api import async_playwright

HOME = "https://animepahe.com"

async def get_latest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto(HOME, timeout=60000)
        await page.wait_for_timeout(5000)

        releases = await page.query_selector_all(".release-card, .episode-card, [class*=release]")
        if not releases:
            releases = await page.query_selector_all(".anime-card")

        seen = set()
        results = []

        for card in releases[:20]:
            title_el = await card.query_selector('[data-title]') or await card.query_selector('a[href*="/anime/"]')
            if not title_el:
                continue
            title = await title_el.get_attribute("data-title") or await title_el.get_attribute("title") or ""
            if not title:
                title = await title_el.inner_text() or ""
            title = title.strip()
            if not title or title.lower() in seen:
                continue
            seen.add(title.lower())

            poster = await card.get_attribute("data-poster") or ""
            if not poster:
                img = await card.query_selector("img")
                if img:
                    poster = await img.get_attribute("src") or await img.get_attribute("data-src") or ""

            ep_str = await card.get_attribute("data-episodes") or "0"

            session = await card.get_attribute("data-session") or ""

            episode = 0
            ep_match = await card.query_selector(".episode-badge, .ep-number, [class*=episode]")
            if ep_match:
                ep_text = await ep_match.inner_text()
                nums = re.findall(r'\d+', ep_text)
                if nums:
                    episode = int(nums[0])
            if not episode and ep_str.isdigit():
                episode = int(ep_str)

            results.append({
                "title": title,
                "episode": episode,
                "snapshot": poster,
                "id": session,
                "created_at": datetime.now(timezone.utc).strftime("%H:%M UTC"),
            })

        if not results:
            data = await page.evaluate('''async () => {
                const r = await fetch("/api?m=release&page=1&sort=episode_asc", {credentials: "include"});
                return r.ok ? r.json() : null;
            }''')
            if data and data.get("data"):
                for item in data["data"][:20]:
                    title = item.get("anime_title", "") or item.get("title", "") or ""
                    if not title or title.lower() in seen:
                        continue
                    seen.add(title.lower())
                    results.append({
                        "title": title,
                        "episode": item.get("episode", 0),
                        "snapshot": item.get("poster", "") or item.get("snapshot", ""),
                        "id": item.get("session", "") or str(item.get("id", "")),
                        "created_at": datetime.now(timezone.utc).strftime("%H:%M UTC"),
                    })

        await browser.close()
        return results

if __name__ == "__main__":
    results = asyncio.run(get_latest())
    if not results:
        print(json.dumps({"error": "No anime found"}))
        sys.exit(1)
    print(json.dumps(results, indent=2))
