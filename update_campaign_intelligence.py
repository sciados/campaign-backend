#!/usr/bin/env python3
"""
Quick script to link campaign to intelligence_core
"""
import asyncio
from sqlalchemy import text
from src.core.database.session import async_session_maker

async def update_campaign():
    async with async_session_maker() as db:
        try:
            # Update campaign with intelligence_id
            update_query = text("""
                UPDATE campaigns
                SET intelligence_id = '1cebca08-c988-43b7-b8ac-61a5f6498d1a',
                    intelligence_status = 'completed'
                WHERE id = '4b5e4dd2-1b6e-4b33-bb7c-8b3f9e51c8b8'
            """)
            await db.execute(update_query)
            await db.commit()

            print("✅ Campaign updated successfully")

            # Verify update
            verify_query = text("""
                SELECT c.id, c.title, c.intelligence_id, ic.product_name
                FROM campaigns c
                LEFT JOIN intelligence_core ic ON ic.id = c.intelligence_id
                WHERE c.id = '4b5e4dd2-1b6e-4b33-bb7c-8b3f9e51c8b8'
            """)
            result = await db.execute(verify_query)
            row = result.fetchone()

            if row:
                print(f"\n📋 Campaign Details:")
                print(f"   Title: {row.title}")
                print(f"   Intelligence ID: {row.intelligence_id}")
                print(f"   Product Name: {row.product_name}")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(update_campaign())
