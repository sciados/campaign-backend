# clickbank_module/services/clickbank_service.py
import os
import requests
from src.platforms.clickbank.db.clickbank_repo import save_clickbank_creds, get_clickbank_creds

BASE_URL = "https://api.clickbank.com/rest/1.3"
DEV_KEY = os.getenv("CLICKBANK_DEV_KEY")  # Stored in Railway ENV

def save_credentials(user_id: int, nickname: str, clerk_key: str):
    # Save nickname + clerk_key, dev key stays global
    save_clickbank_creds(user_id, nickname, clerk_key)
    return {"status": "success", "message": "ClickBank account connected."}

def fetch_sales(user_id: int, days: int = 30):
    creds = get_clickbank_creds(user_id)
    if not creds:
        raise Exception("ClickBank account not connected")

    headers = {
        "Authorization": f"{DEV_KEY}:{creds['clerk_key']}"
    }
    params = {
        "accountId": creds['nickname'],
        "days": days
    }

    r = requests.get(f"{BASE_URL}/analytics/summary", headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"ClickBank API error: {r.text}")

    return r.json()
