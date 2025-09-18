"""Add ProductCreatorSubmission table for admin URL pre-population

Revision ID: 006_add_product_creator_submission_table
Revises: intelligence_fix_001
Create Date: 2025-09-18 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_product_creator_submission_table'
down_revision = 'intelligence_fix_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ProductCreatorSubmission table for admin URL pre-population system."""

    # Create product_creator_submissions table
    op.create_table('product_creator_submissions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('urls', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=False),
        sa.Column('submitter_user_id', sa.String(), nullable=True),
        sa.Column('launch_date', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending_review'),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('processed_by_admin_id', sa.String(), nullable=True),
        sa.Column('intelligence_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_time_seconds', sa.String(), nullable=True),
        sa.Column('total_urls_processed', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_product_creator_product_name', 'product_creator_submissions', ['product_name'])
    op.create_index('idx_product_creator_status', 'product_creator_submissions', ['status'])
    op.create_index('idx_product_creator_created_at', 'product_creator_submissions', ['created_at'])
    op.create_index('idx_product_creator_contact_email', 'product_creator_submissions', ['contact_email'])


def downgrade() -> None:
    """Drop ProductCreatorSubmission table."""

    # Drop indexes
    op.drop_index('idx_product_creator_contact_email', table_name='product_creator_submissions')
    op.drop_index('idx_product_creator_created_at', table_name='product_creator_submissions')
    op.drop_index('idx_product_creator_status', table_name='product_creator_submissions')
    op.drop_index('idx_product_creator_product_name', table_name='product_creator_submissions')

    # Drop table
    op.drop_table('product_creator_submissions')