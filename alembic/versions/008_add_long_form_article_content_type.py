"""add_long_form_article_content_type

Revision ID: 008
Revises: 007
Create Date: 2025-10-08 14:20:42

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing check constraint
    op.execute("""
        ALTER TABLE generated_content
        DROP CONSTRAINT IF EXISTS valid_content_type;
    """)

    # Add the new check constraint with long_form_article included
    op.execute("""
        ALTER TABLE generated_content
        ADD CONSTRAINT valid_content_type
        CHECK (content_type IN (
            'email_sequence',
            'social_media',
            'blog_post',
            'ad_copy',
            'image',
            'video_script',
            'long_form_article'
        ));
    """)


def downgrade() -> None:
    # Drop the constraint with long_form_article
    op.execute("""
        ALTER TABLE generated_content
        DROP CONSTRAINT IF EXISTS valid_content_type;
    """)

    # Restore the original constraint without long_form_article
    op.execute("""
        ALTER TABLE generated_content
        ADD CONSTRAINT valid_content_type
        CHECK (content_type IN (
            'email_sequence',
            'social_media',
            'blog_post',
            'ad_copy',
            'image',
            'video_script'
        ));
    """)
