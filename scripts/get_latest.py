import httpx, json, sys

BASE = "https://animepahe.pw"

def solve_ddos(client: httpx.Client) -> bool:
    try:
        r = client.get(
            f"{BASE}/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        ddgid = r.cookies.get("__ddgid_")
        if not ddgid:
            return False
        r2 = client.get(
            f"{BASE}/.well-known/ddos-guard/id/{ddgid}",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": f"{BASE}/",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            },
        )
        return r2.status_code == 200
    except Exception:
        pass
    return False

def get_latest():
    with httpx.Client(follow_redirects=True, timeout=15) as client:
        if not solve_ddos(client):
            print(json.dumps({"error": "DDoS-Guard bypass failed"}))
            sys.exit(1)
        r = client.get(
            f"{BASE}/api",
            params={"m": "airing", "page": 1},
            headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
        )
        if r.status_code != 200:
            print(json.dumps({"error": f"API returned {r.status_code}"}))
            sys.exit(1)
        return r.json()

if __name__ == "__main__":
    data = get_latest()
    releases = data.get("data", [])
    if releases:
        top5 = releases[:5]
        print(json.dumps([{
            "title": r["anime_title"],
            "episode": r["episode"],
            "snapshot": r["snapshot"],
            "created_at": r["created_at"],
            "id": r["id"],
        } for r in top5], indent=2))
    else:
        print(json.dumps({"error": "No releases found"}))
