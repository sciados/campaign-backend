#!/usr/bin/env python3
"""
Fix the unique constraint issue on clickbank_accounts table
"""

import asyncio
import asyncpg
import os
from src.core.config import settings

async def fix_constraint():
    """Fix the unique constraint on clickbank_accounts table"""

    # Connect to database
    conn = await asyncpg.connect(settings.DATABASE_URL)

    try:
        print("Checking current constraints on clickbank_accounts table...")

        # Check existing constraints
        constraints = await conn.fetch("""
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'clickbank_accounts'
            ORDER BY tc.constraint_type, kcu.column_name;
        """)

        print("Current constraints:")
        for constraint in constraints:
            print(f"  {constraint['constraint_name']}: {constraint['constraint_type']} on {constraint['column_name']}")

        # Check if unique constraint exists on user_id
        has_unique_user_id = any(
            c['constraint_type'] == 'UNIQUE' and c['column_name'] == 'user_id'
            for c in constraints
        )

        if not has_unique_user_id:
            print("Adding unique constraint on user_id...")
            await conn.execute("""
                ALTER TABLE clickbank_accounts
                ADD CONSTRAINT clickbank_accounts_user_id_unique UNIQUE (user_id);
            """)
            print("✅ Added unique constraint on user_id")
        else:
            print("✅ Unique constraint on user_id already exists")

        # Verify the constraint was added
        print("\nFinal constraints:")
        final_constraints = await conn.fetch("""
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'clickbank_accounts'
            ORDER BY tc.constraint_type, kcu.column_name;
        """)

        for constraint in final_constraints:
            print(f"  {constraint['constraint_name']}: {constraint['constraint_type']} on {constraint['column_name']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_constraint())