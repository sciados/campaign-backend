"""Add ProductCreatorInvite table for admin-controlled special accounts

Revision ID: 007_add_product_creator_invite_table
Revises: 006_add_product_creator_submission_table
Create Date: 2025-09-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_product_creator_invite_table'
down_revision = '006_add_product_creator_submission_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ProductCreatorInvite table for admin-controlled invitations."""

    # Create product_creator_invites table
    op.create_table('product_creator_invites',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('invitee_email', sa.String(), nullable=False),
        sa.Column('invitee_name', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('invite_token', sa.String(), nullable=False),
        sa.Column('invited_by_admin_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_url_submissions', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('usage_restrictions', sa.Text(), nullable=True),
        sa.Column('special_permissions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_user_id', sa.String(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create unique constraints
    op.create_unique_constraint('uq_product_creator_invite_token', 'product_creator_invites', ['invite_token'])

    # Create indexes for performance
    op.create_index('idx_product_creator_invite_email', 'product_creator_invites', ['invitee_email'])
    op.create_index('idx_product_creator_invite_status', 'product_creator_invites', ['status'])
    op.create_index('idx_product_creator_invite_admin', 'product_creator_invites', ['invited_by_admin_id'])
    op.create_index('idx_product_creator_invite_expires', 'product_creator_invites', ['expires_at'])
    op.create_index('idx_product_creator_invite_created_user', 'product_creator_invites', ['created_user_id'])


def downgrade() -> None:
    """Drop ProductCreatorInvite table."""

    # Drop indexes
    op.drop_index('idx_product_creator_invite_created_user', table_name='product_creator_invites')
    op.drop_index('idx_product_creator_invite_expires', table_name='product_creator_invites')
    op.drop_index('idx_product_creator_invite_admin', table_name='product_creator_invites')
    op.drop_index('idx_product_creator_invite_status', table_name='product_creator_invites')
    op.drop_index('idx_product_creator_invite_email', table_name='product_creator_invites')

    # Drop unique constraints
    op.drop_constraint('uq_product_creator_invite_token', 'product_creator_invites', type_='unique')

    # Drop table
    op.drop_table('product_creator_invites')