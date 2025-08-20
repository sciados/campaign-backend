# src/core/ai_discovery_database.py - FIXED WITH ASYNC SUPPORT

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql import func
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime

# ✅ AI Discovery Database Connection (both sync and async)
AI_DISCOVERY_DATABASE_URL = os.getenv(
    "AI_DISCOVERY_DATABASE_URL", 
    # Fallback to main database if AI Discovery URL not set
    os.getenv("DATABASE_URL")
)

print(f"🔗 AI Discovery DB URL: {AI_DISCOVERY_DATABASE_URL[:50]}...")

# ✅ SYNC ENGINE (for the current router)
ai_discovery_engine = create_engine(AI_DISCOVERY_DATABASE_URL)
AIDiscoverySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ai_discovery_engine)

# ✅ ASYNC ENGINE (for future async operations)
if AI_DISCOVERY_DATABASE_URL.startswith('postgresql://'):
    # Convert to async URL
    async_url = AI_DISCOVERY_DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
else:
    async_url = AI_DISCOVERY_DATABASE_URL

ai_discovery_async_engine = create_async_engine(async_url)
AIDiscoveryAsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=ai_discovery_async_engine,
    class_=AsyncSession
)

AIDiscoveryBase = declarative_base()

# ✅ SYNC DEPENDENCY (for current router)
def get_ai_discovery_db() -> Session:
    """Get AI Discovery database session (sync)"""
    db = AIDiscoverySessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ ASYNC DEPENDENCY (for future use)
async def get_ai_discovery_async_db() -> AsyncSession:
    """Get AI Discovery database session (async)"""
    async with AIDiscoveryAsyncSessionLocal() as session:
        yield session

@contextmanager
def get_ai_discovery_session():
    """Context manager for AI Discovery database session"""
    db = AIDiscoverySessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@asynccontextmanager
async def get_ai_discovery_async_session():
    """Async context manager for AI Discovery database session"""
    async with AIDiscoveryAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# ✅ MODELS (same as before but ensuring they're properly exported)
class RailwayAIProvider(AIDiscoveryBase):
    """Model for Railway environment AI provider scanning"""
    __tablename__ = "railway_ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(255), nullable=False, index=True)
    env_var_name = Column(String(255), unique=True, nullable=False, index=True)
    env_var_status = Column(String(50), nullable=False, default='missing')
    value_preview = Column(String(255), nullable=True)
    integration_status = Column(String(50), default='discovered', index=True)
    category = Column(String(100), nullable=False, index=True)
    priority_tier = Column(String(50), nullable=False, default='discovered', index=True)
    cost_per_1k_tokens = Column(DECIMAL(10, 6), nullable=True)
    quality_score = Column(DECIMAL(3, 2), default=4.0)
    model = Column(String(255), nullable=True)
    capabilities = Column(Text, nullable=True)
    monthly_usage = Column(Integer, default=0)
    response_time_ms = Column(Integer, nullable=True)
    error_rate = Column(DECIMAL(5, 4), nullable=True)
    source = Column(String(50), default='environment', index=True)
    last_checked = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False, index=True)
    api_endpoint = Column(String(255), nullable=True)
    discovery_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Links to existing ai_tools_registry if needed
    tool_registry_id = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<RailwayAIProvider(provider_name='{self.provider_name}', env_var_name='{self.env_var_name}')>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'env_var_name': self.env_var_name,
            'env_var_status': self.env_var_status,
            'value_preview': self.value_preview,
            'integration_status': self.integration_status,
            'category': self.category,
            'priority_tier': self.priority_tier,
            'cost_per_1k_tokens': float(self.cost_per_1k_tokens) if self.cost_per_1k_tokens else None,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'model': self.model,
            'capabilities': self.capabilities.split(',') if self.capabilities else [],
            'monthly_usage': self.monthly_usage,
            'response_time_ms': self.response_time_ms,
            'error_rate': float(self.error_rate) if self.error_rate else None,
            'source': self.source,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'is_active': self.is_active,
            'api_endpoint': self.api_endpoint,
            'discovery_date': self.discovery_date.isoformat() if self.discovery_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ✅ TABLE CREATION HELPER
def create_ai_discovery_tables():
    """Create AI Discovery tables if they don't exist"""
    try:
        AIDiscoveryBase.metadata.create_all(bind=ai_discovery_engine)
        print("✅ AI Discovery tables created/verified")
    except Exception as e:
        print(f"⚠️ AI Discovery table creation failed: {e}")

async def create_ai_discovery_tables_async():
    """Create AI Discovery tables asynchronously"""
    try:
        async with ai_discovery_async_engine.begin() as conn:
            await conn.run_sync(AIDiscoveryBase.metadata.create_all)
        print("✅ AI Discovery tables created/verified (async)")
    except Exception as e:
        print(f"⚠️ AI Discovery table creation failed (async): {e}")

# ✅ HEALTH CHECK
def test_ai_discovery_connection():
    """Test AI Discovery database connection"""
    try:
        with get_ai_discovery_session() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ AI Discovery DB connection failed: {e}")
        return False

async def test_ai_discovery_connection_async():
    """Test AI Discovery database connection (async)"""
    try:
        async with get_ai_discovery_async_session() as db:
            await db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ AI Discovery DB connection failed (async): {e}")
        return False