"""Create campaign enums

Revision ID: 004_create_campaign_enums
Revises: 003_rename_campaigns_title_to_name
Create Date: 2025-09-14 13:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_create_campaign_enums'
down_revision: Union[str, None] = '003_rename_campaigns_title_to_name'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum types if they don't exist
    
    # Create CampaignStatusEnum
    campaignstatusenum = postgresql.ENUM(
        'draft', 'active', 'paused', 'completed', 'archived',
        name='campaignstatusenum'
    )
    campaignstatusenum.create(op.get_bind(), checkfirst=True)
    
    # Create CampaignTypeEnum  
    campaigntypeenum = postgresql.ENUM(
        'email_sequence', 'social_media', 'content_marketing', 
        'affiliate_promotion', 'product_launch',
        name='campaigntypeenum'
    )
    campaigntypeenum.create(op.get_bind(), checkfirst=True)
    
    # Update the campaigns table columns to use the enum types
    # (Only if the table exists and columns need updating)
    try:
        op.execute("""
            DO $$ BEGIN
                -- Check if campaigns table exists
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                    -- Update status column if it's not already an enum
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'campaigns' 
                        AND column_name = 'status' 
                        AND udt_name = 'campaignstatusenum'
                    ) THEN
                        ALTER TABLE campaigns 
                        ALTER COLUMN status TYPE campaignstatusenum 
                        USING status::campaignstatusenum;
                    END IF;
                    
                    -- Update campaign_type column if it's not already an enum
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'campaigns' 
                        AND column_name = 'campaign_type' 
                        AND udt_name = 'campaigntypeenum'
                    ) THEN
                        ALTER TABLE campaigns 
                        ALTER COLUMN campaign_type TYPE campaigntypeenum 
                        USING campaign_type::campaigntypeenum;
                    END IF;
                END IF;
            END $$;
        """)
    except Exception as e:
        # If there's an issue, just create the enums - the table might not exist yet
        pass


def downgrade() -> None:
    # Revert columns back to text if needed
    try:
        op.execute("""
            DO $$ BEGIN
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                    ALTER TABLE campaigns ALTER COLUMN status TYPE VARCHAR(50);
                    ALTER TABLE campaigns ALTER COLUMN campaign_type TYPE VARCHAR(50);
                END IF;
            END $$;
        """)
    except Exception:
        pass
        
    # Drop the enum types
    try:
        op.execute("DROP TYPE IF EXISTS campaigntypeenum")
        op.execute("DROP TYPE IF EXISTS campaignstatusenum") 
    except Exception:
        pass