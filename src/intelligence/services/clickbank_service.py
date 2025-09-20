import requests
import asyncio
from src.core.database.clickbank_repo import save_clickbank_creds, get_clickbank_creds
from src.core.config import settings

BASE_URL = "https://api.clickbank.com/rest/1.3"

def save_credentials(user_id: int, nickname: str, clerk_key: str):
    """Save ClickBank credentials for a user (sync wrapper)"""
    # Use asyncio to run the async function
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_clickbank_creds(user_id, nickname, clerk_key))
    except RuntimeError:
        # Create new loop if none exists
        asyncio.run(save_clickbank_creds(user_id, nickname, clerk_key))

    return {"status": "success", "message": "ClickBank account connected."}

def fetch_sales(user_id: int, days: int = 30):
    """Fetch sales data from ClickBank API (sync wrapper)"""
    # Get credentials using sync wrapper
    try:
        loop = asyncio.get_event_loop()
        creds = loop.run_until_complete(get_clickbank_creds(user_id))
    except RuntimeError:
        # Create new loop if none exists
        creds = asyncio.run(get_clickbank_creds(user_id))

    if not creds:
        raise Exception("ClickBank account not connected")

    headers = {
        "Authorization": f"{settings.CLICKBANK_DEV_KEY}:{creds['clerk_key']}"
    }
    params = {
        "accountId": creds['nickname'],
        "days": days
    }

    r = requests.get(f"{BASE_URL}/analytics/summary", headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"ClickBank API error: {r.text}")

    return r.json()