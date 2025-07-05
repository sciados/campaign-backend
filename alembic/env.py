import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, MetaData, Table, Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import enum

from alembic import context

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create minimal metadata for the intelligence table
metadata = MetaData()

# Define just the intelligence table that we need to migrate
campaign_intelligence = Table(
    'campaign_intelligence',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    
    # Basic Information
    Column('source_url', Text),
    Column('source_type', String(50), nullable=False),
    Column('source_title', String(500)),
    Column('analysis_status', String(50), default='PENDING'),
    
    # Core Intelligence Data - FIXED: Proper JSONB columns
    Column('offer_intelligence', JSONB, default={}),
    Column('psychology_intelligence', JSONB, default={}),
    Column('content_intelligence', JSONB, default={}),
    Column('competitive_intelligence', JSONB, default={}),
    Column('brand_intelligence', JSONB, default={}),
    
    # AI Enhancement Intelligence Columns - FIXED: Proper JSONB columns
    Column('scientific_intelligence', JSONB, default={}),
    Column('credibility_intelligence', JSONB, default={}),
    Column('market_intelligence', JSONB, default={}),
    Column('emotional_transformation_intelligence', JSONB, default={}),
    Column('scientific_authority_intelligence', JSONB, default={}),
    
    # Performance Tracking
    Column('confidence_score', Float, default=0.0),
    Column('usage_count', Integer, default=0),
    Column('success_rate', Float, default=0.0),
    
    # Raw Data Storage
    Column('raw_content', Text),
    Column('processing_metadata', JSONB, default={}),
    
    # Foreign Keys
    Column('campaign_id', UUID(as_uuid=True), nullable=False),
    Column('user_id', UUID(as_uuid=True), nullable=False),
    Column('company_id', UUID(as_uuid=True), nullable=False),
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use our minimal metadata
target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()