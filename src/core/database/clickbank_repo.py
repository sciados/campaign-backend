# clickbank_module/db/clickbank_repo.py
from src.core.database  import database

async def save_clickbank_creds(user_id: int, nickname: str, clerk_key: str):
    query = """
    INSERT INTO clickbank_accounts (user_id, nickname, clerk_key)
    VALUES (:user_id, :nickname, :clerk_key)
    ON CONFLICT (user_id) DO UPDATE
    SET nickname = :nickname, clerk_key = :clerk_key
    """
    await database.execute(query, {"user_id": user_id, "nickname": nickname, "clerk_key": clerk_key})

async def get_clickbank_creds(user_id: int):
    query = "SELECT nickname, clerk_key FROM clickbank_accounts WHERE user_id = :user_id"
    row = await database.fetch_one(query, {"user_id": user_id})
    return dict(row) if row else None
