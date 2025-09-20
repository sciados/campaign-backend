# clickbank_module/db/clickbank_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.database.session import AsyncSessionManager

async def save_clickbank_creds(user_id: str, nickname: str, api_key: str):
    """Save ClickBank credentials using async session"""
    print(f"DEBUG: Database save - user_id={user_id}, nickname={nickname}, api_key=***")

    query = text("""
    INSERT INTO clickbank_accounts (user_id, nickname, api_key)
    VALUES (:user_id, :nickname, :api_key)
    ON CONFLICT (user_id) DO UPDATE
    SET nickname = :nickname, api_key = :api_key
    """)

    try:
        async with AsyncSessionManager.get_session() as session:
            print(f"DEBUG: Got database session, executing query")
            result = await session.execute(query, {"user_id": user_id, "nickname": nickname, "api_key": api_key})
            print(f"DEBUG: Query executed, committing transaction")
            await session.commit()
            print(f"DEBUG: Transaction committed successfully")
    except Exception as e:
        print(f"ERROR: Database save failed: {e}")
        raise e

async def get_clickbank_creds(user_id: str):
    """Get ClickBank credentials using async session"""
    query = text("SELECT nickname, api_key FROM clickbank_accounts WHERE user_id = :user_id")

    async with AsyncSessionManager.get_session() as session:
        result = await session.execute(query, {"user_id": user_id})
        row = result.fetchone()
        if row:
            return {"nickname": row.nickname, "api_key": row.api_key}
        return None
