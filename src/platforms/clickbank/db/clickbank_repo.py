# clickbank_module/db/clickbank_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.database.session import AsyncSessionManager

async def save_clickbank_creds(user_id: str, nickname: str, api_key: str):
    """Save ClickBank credentials using async session"""
    print(f"DEBUG: Database save - user_id={user_id}, nickname={nickname}, api_key=***")

    try:
        async with AsyncSessionManager.get_session() as session:
            print(f"DEBUG: Got database session, attempting update first")

            # First try to update existing record
            update_query = text("""
                UPDATE clickbank_accounts
                SET nickname = :nickname, api_key = :api_key
                WHERE user_id = :user_id
            """)

            result = await session.execute(update_query, {"user_id": user_id, "nickname": nickname, "api_key": api_key})
            print(f"DEBUG: Update query executed, rows affected: {result.rowcount}")

            # If no rows were updated, insert new record
            if result.rowcount == 0:
                print(f"DEBUG: No existing record found, inserting new record")
                insert_query = text("""
                    INSERT INTO clickbank_accounts (user_id, nickname, api_key)
                    VALUES (:user_id, :nickname, :api_key)
                """)
                await session.execute(insert_query, {"user_id": user_id, "nickname": nickname, "api_key": api_key})
                print(f"DEBUG: Insert query executed")

            print(f"DEBUG: Committing transaction")
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
