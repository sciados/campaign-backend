# src/media_generation/repository/repo.py
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import media_jobs_table  # import your table definition

async def insert_generated_media(session: AsyncSession, payload: dict):
    """
    Insert a new media job into DB
    payload keys: user_id, salespage_url, media_type, platform, prompt, provider, output_url, cost_usd
    """
    stmt = insert(media_jobs_table).values(**payload)
    await session.execute(stmt)
    await session.commit()