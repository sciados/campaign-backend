"""Convert enum columns to varchar

Revision ID: 005_convert_enums_to_varchar
Revises: 004_create_campaign_enums
Create Date: 2025-09-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_convert_enums_to_varchar'
down_revision: Union[str, None] = '004_create_campaign_enums'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert enum columns back to varchar to match SQLAlchemy String columns
    try:
        op.execute("""
            DO $$ BEGIN
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                    -- Convert status column from enum to varchar
                    ALTER TABLE campaigns 
                    ALTER COLUMN status TYPE VARCHAR(50) 
                    USING status::text;
                    
                    -- Convert campaign_type column from enum to varchar
                    ALTER TABLE campaigns 
                    ALTER COLUMN campaign_type TYPE VARCHAR(50) 
                    USING campaign_type::text;
                END IF;
            END $$;
        """)
        print("✅ Successfully converted enum columns to varchar")
    except Exception as e:
        print(f"❌ Error converting columns: {e}")
        raise


def downgrade() -> None:
    # Convert back to enums if needed (reverse operation)
    try:
        op.execute("""
            DO $$ BEGIN
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                    -- Convert back to enum types
                    ALTER TABLE campaigns 
                    ALTER COLUMN status TYPE campaignstatusenum 
                    USING status::campaignstatusenum;
                    
                    ALTER TABLE campaigns 
                    ALTER COLUMN campaign_type TYPE campaigntypeenum 
                    USING campaign_type::campaigntypeenum;
                END IF;
            END $$;
        """)
    except Exception as e:
        print(f"Error reverting to enums: {e}")
        pass