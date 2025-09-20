import requests
import asyncio
from src.core.database.clickbank_repo import save_clickbank_creds, get_clickbank_creds
from src.core.config import settings

BASE_URL = "https://api.clickbank.com/rest/1.3"

def save_credentials(user_id: str, nickname: str, api_key: str):
    """Save ClickBank credentials for a user (sync wrapper)"""
    print(f"DEBUG: Attempting to save ClickBank credentials for user_id={user_id}, nickname={nickname}")

    # Use asyncio to run the async function
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_clickbank_creds(user_id, nickname, api_key))
        print(f"DEBUG: ClickBank credentials saved successfully via existing loop")
    except RuntimeError as e:
        print(f"DEBUG: RuntimeError, creating new loop: {e}")
        # Create new loop if none exists
        asyncio.run(save_clickbank_creds(user_id, nickname, api_key))
        print(f"DEBUG: ClickBank credentials saved successfully via new loop")
    except Exception as e:
        print(f"ERROR: Failed to save ClickBank credentials: {e}")
        raise e

    return {"status": "success", "message": "ClickBank account connected."}

def fetch_sales(user_id: str, days: int = 30):
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

    # New ClickBank API format: Use user's API key directly
    # No more dev key needed as of August 2023
    headers = {
        "Authorization": f"Bearer {creds['api_key']}",
        "Content-Type": "application/json"
    }
    params = {
        "account": creds['nickname'],  # Updated parameter name
        "days": days
    }

    r = requests.get(f"{BASE_URL}/analytics/summary", headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"ClickBank API error: {r.text}")

    return r.json()