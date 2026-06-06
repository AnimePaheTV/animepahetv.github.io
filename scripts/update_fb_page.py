#!/usr/bin/env python3
"""One-time script to update Facebook page info, profile pic, cover photo."""
import os, json, sys, requests
from html import escape

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
API = "https://graph.facebook.com/v25.0"

if not FB_PAGE_ID or not FB_TOKEN:
    print("Missing FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN")
    sys.exit(1)

auth = {"access_token": FB_TOKEN}

def call(method, path, data=None):
    url = f"{API}/{path}"
    if data:
        data.update(auth)
    else:
        data = auth
    r = requests.request(method, url, data=data, timeout=30)
    print(f"  {method} {path} -> {r.status_code}")
    if r.status_code >= 400:
        print(f"  ERROR: {r.text[:300]}")
    return r

# 1. Read current page info
print("=== 1. Current page info ===")
r = call("GET", FB_PAGE_ID)
if r.status_code == 200:
    info = r.json()
    print(f"  Name: {info.get('name')}")
    print(f"  Username: {info.get('username')}")
    print(f"  About: {info.get('about','')[:80]}...")
    print(f"  Category: {info.get('category')}")
    print(f"  Website: {info.get('website')}")

# 2. Update page info
print("\n=== 2. Updating page info ===")
r = call("POST", FB_PAGE_ID, {
    "name": "FreeStream TV",
    "username": "FreeStreamTV",
    "about": "Free streaming apps for Android TV, Firestick & Mobile. Watch anime, K-Dramas, movies & live football free. Zero ads.",
    "description": "FreeStream TV brings you three powerful streaming apps for Android TV, Firestick, and Mobile:\n\n\u2022 AnimePahe TV \u2013 Unlimited anime subbed and dubbed\n\u2022 Nkiri TV \u2013 K-Dramas, Hollywood series & popular movies\n\u2022 Socolive TV \u2013 Live football matches & real-time scores\n\n100% free. Zero ads. Download now.",
    "website": "https://animepahetv.github.io",
})

# 3. Upload profile picture from a public URL
print("\n=== 3. Uploading profile picture ===")
pic_url = "https://animepahetv.github.io/assets/icon.png"
r = call("POST", f"{FB_PAGE_ID}/photos", {
    "url": pic_url,
    "published": True,
    "temporary": True,
})
if r.status_code == 200:
    photo_id = r.json().get("id")
    if photo_id:
        print(f"  Photo ID: {photo_id}")
        # Set as profile picture
        print("\n=== 4. Setting as profile picture ===")
        r2 = call("POST", f"{FB_PAGE_ID}/picture", {
            "photo_id": photo_id,
        })
        if r2.status_code == 200:
            print("  Profile picture updated!")
        else:
            print(f"  Profile pic failed, trying alternative...")
            r3 = call("POST", f"{FB_PAGE_ID}", {
                "profile_pic_url": pic_url,
            })

# 5. Try setting cover photo
print("\n=== 5. Uploading cover photo ===")
cover_url = "https://nkiritv.github.io/assets/icon.png"
r = call("POST", f"{FB_PAGE_ID}/photos", {
    "url": cover_url,
    "published": False,
})
if r.status_code == 200:
    photo_id = r.json().get("id")
    if photo_id:
        print(f"  Cover photo ID: {photo_id}")
        r2 = call("POST", f"{FB_PAGE_ID}/cover", {
            "photo_id": photo_id,
        })

print("\n=== Done ===")
