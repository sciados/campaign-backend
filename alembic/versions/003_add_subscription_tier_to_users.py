"""Add subscription_tier to users table

Revision ID: 003_add_subscription_tier_to_users
Revises: 002_add_waitlist_table
Create Date: 2025-10-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '003_add_subscription_tier_to_users'
down_revision: Union[str, None] = '002_add_waitlist_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add subscription_tier column to users table for easier access.
    This denormalizes the tier from companies table to avoid joins.
    """

    # Add subscription_tier column to users table
    op.add_column('users', sa.Column('subscription_tier', sa.String(), nullable=True))

    # Backfill existing users with their company's subscription tier
    op.execute("""
        UPDATE users
        SET subscription_tier = companies.subscription_tier
        FROM companies
        WHERE users.company_id = companies.id
    """)

    # Set default to 'FREE' for users without a company
    op.execute("""
        UPDATE users
        SET subscription_tier = 'FREE'
        WHERE subscription_tier IS NULL
    """)

    # Make column non-nullable now that all rows have values
    op.alter_column('users', 'subscription_tier', nullable=False, server_default='FREE')


def downgrade() -> None:
    """Remove subscription_tier column from users table"""
    op.drop_column('users', 'subscription_tier')
