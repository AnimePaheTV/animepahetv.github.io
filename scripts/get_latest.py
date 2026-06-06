import httpx, json, sys
from datetime import datetime, timezone, timedelta

ANILIST = "https://graphql.anilist.co"

def get_latest():
    now = datetime.now(timezone.utc)
    start_ts = int(now.timestamp())
    end_ts = int((now + timedelta(hours=12)).timestamp())

    query = {
        "query": f"""
        {{
          Page(page: 1, perPage: 50) {{
            airingSchedules(
              airingAt_greater: {start_ts}
              airingAt_lesser: {end_ts}
              sort: TIME_DESC
            ) {{
              episode
              airingAt
              media {{
                id
                title {{ romaji english }}
                coverImage {{ large medium }}
              }}
            }}
          }}
        }}
        """
    }

    with httpx.Client(timeout=15) as client:
        r = client.post(
            ANILIST,
            json=query,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if r.status_code != 200:
            print(json.dumps({"error": f"AniList returned {r.status_code}"}))
            sys.exit(1)

        data = r.json()
        schedules = data.get("data", {}).get("Page", {}).get("airingSchedules", [])
        if not schedules:
            print(json.dumps({"error": "No episodes in the next 12 hours"}))
            sys.exit(1)

        seen = set()
        results = []
        for s in schedules:
            mid = s["media"]["id"]
            if mid in seen:
                continue
            seen.add(mid)
            title = s["media"]["title"]
            name = title.get("romaji") or title.get("english") or "Unknown"
            ci = s["media"]["coverImage"]
            results.append({
                "title": name,
                "episode": s["episode"],
                "snapshot_large": ci["large"],
                "snapshot_medium": ci["medium"],
                "created_at": datetime.fromtimestamp(s["airingAt"], tz=timezone.utc).strftime("%H:%M UTC"),
                "id": mid,
            })

        return results

if __name__ == "__main__":
    results = get_latest()
    print(json.dumps(results, indent=2))
