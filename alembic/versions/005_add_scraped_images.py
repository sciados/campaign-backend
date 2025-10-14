"""Add scraped_images table

Revision ID: 005_add_scraped_images
Revises: 004_add_custom_mockup_templates
Create Date: 2025-01-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '005_add_scraped_images'
down_revision = '004_add_custom_mockup_templates'  # Update this to your last migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create scraped_images table"""

    op.create_table(
        'scraped_images',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('campaign_id', UUID, sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),

        # Storage
        sa.Column('r2_path', sa.String(), nullable=False),
        sa.Column('cdn_url', sa.String(), nullable=False),
        sa.Column('original_url', sa.String(), nullable=True),

        # Image properties
        sa.Column('width', sa.Integer, nullable=False),
        sa.Column('height', sa.Integer, nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),  # bytes
        sa.Column('format', sa.String(10), nullable=False),  # jpg, png, webp

        # Metadata
        sa.Column('alt_text', sa.Text(), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),  # Surrounding text
        sa.Column('quality_score', sa.Float, nullable=False, default=0.0, index=True),

        # Classification
        sa.Column('is_hero', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('is_product', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('is_lifestyle', sa.Boolean, default=False, nullable=False, index=True),

        # Usage tracking
        sa.Column('times_used', sa.Integer, default=0, nullable=False),
        sa.Column('last_used_at', sa.DateTime, nullable=True),

        # Additional metadata
        sa.Column('metadata', JSONB, nullable=True),

        # Timestamps
        sa.Column('scraped_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),

        # Indexes for common queries
        sa.Index('idx_scraped_images_campaign_type', 'campaign_id', 'is_hero', 'is_product'),
        sa.Index('idx_scraped_images_quality', 'quality_score'),
        sa.Index('idx_scraped_images_usage', 'times_used'),
    )

    # Create updated_at trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_scraped_images_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER scraped_images_updated_at
        BEFORE UPDATE ON scraped_images
        FOR EACH ROW
        EXECUTE FUNCTION update_scraped_images_updated_at();
    """)


def downgrade() -> None:
    """Drop scraped_images table"""

    op.execute("DROP TRIGGER IF EXISTS scraped_images_updated_at ON scraped_images;")
    op.execute("DROP FUNCTION IF EXISTS update_scraped_images_updated_at();")
    op.drop_table('scraped_images')
