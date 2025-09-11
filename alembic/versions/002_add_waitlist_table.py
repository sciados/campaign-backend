"""Add waitlist table

Revision ID: 002_add_waitlist_table
Revises: intelligence_fix_001_fix_intelligence_columns
Create Date: 2025-01-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '002_add_waitlist_table'
down_revision: Union[str, None] = 'intelligence_fix_001_fix_intelligence_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create waitlist table
    op.create_table(
        'waitlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('referrer', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('is_notified', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_waitlist_email', 'waitlist', ['email'])
    op.create_index('idx_waitlist_created', 'waitlist', ['created_at'])
    
    # Add unique constraint on email
    op.create_unique_constraint(None, 'waitlist', ['email'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_waitlist_created', table_name='waitlist')
    op.drop_index('idx_waitlist_email', table_name='waitlist')
    
    # Drop table
    op.drop_table('waitlist')