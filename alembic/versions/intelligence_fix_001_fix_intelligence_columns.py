"""Fix intelligence model column definitions - SAFE VERSION

Revision ID: intelligence_fix_001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'intelligence_fix_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing JSONB columns to campaign intelligence table"""
    
    # Check if columns exist before adding them
    conn = op.get_bind()
    
    # Get existing columns
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'intelligence_core' 
        AND table_schema = 'public'
    """))
    existing_columns = {row[0] for row in result}
    
    # Add missing JSONB columns only if they don't exist
    columns_to_add = [
        ('offer_intelligence', 'JSONB'),
        ('psychology_intelligence', 'JSONB'),
        ('content_intelligence', 'JSONB'),
        ('competitive_intelligence', 'JSONB'),
        ('brand_intelligence', 'JSONB'),
        ('scientific_intelligence', 'JSONB'),
        ('credibility_intelligence', 'JSONB'),
        ('market_intelligence', 'JSONB'),
        ('emotional_transformation_intelligence', 'JSONB'),
        ('scientific_authority_intelligence', 'JSONB'),
        ('processing_metadata', 'JSONB'),
    ]
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            print(f"Adding column: {column_name}")
            op.execute(sa.text(f"""
                ALTER TABLE intelligence_core 
                ADD COLUMN {column_name} JSONB DEFAULT '{{}}'::jsonb
            """))
        else:
            print(f"Column {column_name} already exists, skipping")
    
    # Update any existing NULL values to empty JSON objects
    op.execute(sa.text("""
        UPDATE intelligence_core 
        SET 
            offer_intelligence = COALESCE(offer_intelligence, '{}'::jsonb),
            psychology_intelligence = COALESCE(psychology_intelligence, '{}'::jsonb),
            content_intelligence = COALESCE(content_intelligence, '{}'::jsonb),
            competitive_intelligence = COALESCE(competitive_intelligence, '{}'::jsonb),
            brand_intelligence = COALESCE(brand_intelligence, '{}'::jsonb),
            scientific_intelligence = COALESCE(scientific_intelligence, '{}'::jsonb),
            credibility_intelligence = COALESCE(credibility_intelligence, '{}'::jsonb),
            market_intelligence = COALESCE(market_intelligence, '{}'::jsonb),
            emotional_transformation_intelligence = COALESCE(emotional_transformation_intelligence, '{}'::jsonb),
            scientific_authority_intelligence = COALESCE(scientific_authority_intelligence, '{}'::jsonb),
            processing_metadata = COALESCE(processing_metadata, '{}'::jsonb)
        WHERE 
            offer_intelligence IS NULL OR
            psychology_intelligence IS NULL OR
            content_intelligence IS NULL OR
            competitive_intelligence IS NULL OR
            brand_intelligence IS NULL OR
            scientific_intelligence IS NULL OR
            credibility_intelligence IS NULL OR
            market_intelligence IS NULL OR
            emotional_transformation_intelligence IS NULL OR
            scientific_authority_intelligence IS NULL OR
            processing_metadata IS NULL
    """))


def downgrade() -> None:
    """Remove the added JSONB columns"""
    
    columns_to_remove = [
        'offer_intelligence',
        'psychology_intelligence', 
        'content_intelligence',
        'competitive_intelligence',
        'brand_intelligence',
        'scientific_intelligence',
        'credibility_intelligence',
        'market_intelligence',
        'emotional_transformation_intelligence',
        'scientific_authority_intelligence',
        'processing_metadata',
    ]
    
    for column_name in columns_to_remove:
        try:
            op.drop_column('intelligence_core', column_name)
        except Exception as e:
            print(f"Could not drop column {column_name}: {e}")