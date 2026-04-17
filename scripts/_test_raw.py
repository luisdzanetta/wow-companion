"""Diagnose the mythic-keystone-profile response to find the current season ID."""

import json
import httpx
from app.apis.battlenet import get_access_token, API_BASE_URL, REGION

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"}
params = {"namespace": f"profile-{REGION}", "locale": "en_US"}

CHARS = [
    ("thrall", "stormtroll"),
    ("alterac-mountains", "stormpaladin"),
]

for realm_slug, name_slug in CHARS:
    print(f"\n=== {name_slug.title()}-{realm_slug.title()} ===")
    url = f"{API_BASE_URL}/profile/wow/character/{realm_slug}/{name_slug}/mythic-keystone-profile"
    response = httpx.get(url, headers=headers, params=params, timeout=10.0)
    data = response.json()

    # Print what we actually got
    print(f"Top-level keys: {list(data.keys())}")
    print(f"\nFull JSON:")
    print(json.dumps(data, indent=2)[:2000])  # first 2000 chars to keep output manageable