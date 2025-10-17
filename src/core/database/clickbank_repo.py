# clickbank_module/db/clickbank_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict

async def save_clickbank_creds(db: AsyncSession, user_id: int, nickname: str, clerk_key: str):
    query = text("""
    INSERT INTO clickbank_accounts (user_id, nickname, clerk_key)
    VALUES (:user_id, :nickname, :clerk_key)
    ON CONFLICT (user_id) DO UPDATE
    SET nickname = :nickname, clerk_key = :clerk_key
    """)
    await db.execute(query, {"user_id": user_id, "nickname": nickname, "clerk_key": clerk_key})
    await db.commit()

async def get_clickbank_creds(db: AsyncSession, user_id: int) -> Optional[Dict[str, str]]:
    query = text("SELECT nickname, clerk_key FROM clickbank_accounts WHERE user_id = :user_id")
    result = await db.execute(query, {"user_id": user_id})
    row = result.fetchone()
    return dict(row._mapping) if row else None
