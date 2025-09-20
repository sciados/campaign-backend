import requests
import os
from src.core.database  import save_clickbank_creds, get_clickbank_creds
from src.core.config import settings

BASE_URL = "https://api.clickbank.com/rest/1.3"

def get_dev_key():
    """Get ClickBank dev key from settings"""
    return settings.CLICKBANK_DEV_KEY

def is_clickbank_enabled():
    """Check if ClickBank integration is enabled"""
    return settings.CLICKBANK_DEV_KEY is not None

def save_credentials(user_id: int, nickname: str, clerk_key: str):
    """Save ClickBank credentials for a user"""
    if not is_clickbank_enabled():
        raise Exception("ClickBank integration is not enabled")

    # Save nickname + clerk_key, dev key stays global
    save_clickbank_creds(user_id, nickname, clerk_key)
    return {"status": "success", "message": "ClickBank account connected."}

def fetch_sales(user_id: int, days: int = 30):
    """Fetch sales data from ClickBank API"""
    if not is_clickbank_enabled():
        raise Exception("ClickBank integration is not enabled")

    creds = get_clickbank_creds(user_id)
    if not creds:
        raise Exception("ClickBank account not connected")

    dev_key = get_dev_key()
    if not dev_key:
        raise Exception("ClickBank dev key not configured")

    headers = {
        "Authorization": f"{dev_key}:{creds['clerk_key']}"
    }
    params = {
        "accountId": creds['nickname'],
        "days": days
    }

    r = requests.get(f"{BASE_URL}/analytics/summary", headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"ClickBank API error: {r.text}")

    return r.json()