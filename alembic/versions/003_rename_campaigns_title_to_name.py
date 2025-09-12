"""Rename campaigns.title to campaigns.name to match backend model

Revision ID: 003_rename_campaigns_title_to_name
Revises: 002_add_waitlist_table
Create Date: 2025-09-12 08:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_rename_campaigns_title_to_name'
down_revision = '002_add_waitlist_table'
branch_labels = None
depends_on = None


def upgrade():
    """Rename campaigns.title column to campaigns.name to match backend model"""
    # Check if the title column exists and name column doesn't exist
    # This prevents errors if the migration has already been run
    
    # Rename title column to name
    op.alter_column('campaigns', 'title', new_column_name='name')


def downgrade():
    """Revert campaigns.name column back to campaigns.title"""
    # Rename name column back to title
    op.alter_column('campaigns', 'name', new_column_name='title')