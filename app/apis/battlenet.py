"""Battle.net API client."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# --- Configuration loaded from .env ---
CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")
REGION = os.getenv("BLIZZARD_REGION", "us")

# --- Base URLs ---
# OAuth endpoint is global; data endpoints are region-specific
OAUTH_URL = "https://oauth.battle.net/token"
API_BASE_URL = f"https://{REGION}.api.blizzard.com"


def get_access_token() -> str:
    """Fetch an access token from Battle.net using client credentials flow.

    Returns:
        Access token string, valid for ~24h.

    Raises:
        httpx.HTTPStatusError: if authentication fails.
    """
    response = httpx.post(
        OAUTH_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=10.0,
    )
    response.raise_for_status()

    token_data = response.json()
    return token_data["access_token"]


def get_wow_token_price(access_token: str) -> dict:
    """Fetch current WoW Token price info.

    Used as a simple sanity check for the API integration.

    Args:
        access_token: Token obtained via get_access_token().

    Returns:
        Dictionary with WoW Token data (price in copper, last update, etc.).
    """
    url = f"{API_BASE_URL}/data/wow/token/index"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"dynamic-{REGION}", "locale": "en_US"}

    response = httpx.get(url, headers=headers, params=params, timeout=10.0)
    response.raise_for_status()
    return response.json()

def get_character_profile(access_token: str, realm: str, character_name: str) -> dict:
    """Fetch a character's basic profile (class, spec, level, ilvl, etc.).

    Args:
        access_token: Token obtained via get_access_token().
        realm: Realm name (e.g., "Thrall", "Area 52"). Will be normalized.
        character_name: Character name (e.g., "Stormtroll"). Will be normalized.

    Returns:
        Dictionary with the character's profile data.
    """
    realm_slug = realm.lower().replace(" ", "-").replace("'", "")
    name_slug = character_name.lower()

    url = f"{API_BASE_URL}/profile/wow/character/{realm_slug}/{name_slug}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"namespace": f"profile-{REGION}", "locale": "en_US"}

    response = httpx.get(url, headers=headers, params=params, timeout=10.0)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    print("Authenticating with Battle.net...")
    token = get_access_token()
    print(f"Token received: {token[:20]}...\n")

    print("Fetching character profile: Stormtroll-Thrall...")
    profile = get_character_profile(token, realm="Thrall", character_name="Stormtroll")

    print(f"  Name:         {profile['name']}")
    print(f"  Realm:        {profile['realm']['name']}")
    print(f"  Level:        {profile['level']}")
    print(f"  Class:        {profile['character_class']['name']}")
    print(f"  Spec:         {profile['active_spec']['name']}")
    print(f"  Race:         {profile['race']['name']}")
    print(f"  Faction:      {profile['faction']['name']}")
    print(f"  Item Level:   {profile['equipped_item_level']} (equipped) / {profile['average_item_level']} (avg)")
    print(f"  Achievements: {profile['achievement_points']:,} points")
    print(f"  Guild:        {profile.get('guild', {}).get('name', '(no guild)')}")