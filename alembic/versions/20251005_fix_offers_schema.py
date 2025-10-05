"""fix_offers_schema

Revision ID: 20251005_fix_offers
Revises: c1b4bdad2f62
Create Date: 2025-10-05 14:21:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20251005_fix_offers'
down_revision: Union[str, None] = 'c1b4bdad2f62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align offers table with OfferRecord model."""
    
    # Drop old columns that don't match the model
    with op.batch_alter_table('offers', schema=None) as batch_op:
        # Drop columns that don't exist in the model
        batch_op.drop_column('total_price')
        batch_op.drop_column('contract_term_months')
        batch_op.drop_column('discount_percentage')
        batch_op.drop_column('features_included')
        batch_op.drop_column('features_excluded')
        batch_op.drop_column('compliance_met')
        batch_op.drop_column('compliance_gaps')
        batch_op.drop_column('status')
        batch_op.drop_column('valid_until')
        batch_op.drop_column('notes')
        batch_op.drop_column('offer_metadata')
        
        # Add new columns that match the model
        batch_op.add_column(sa.Column('negotiation_session_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('term_months', sa.Integer(), nullable=False, server_default='12'))
        batch_op.add_column(sa.Column('discount_percent', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('value_adds', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('conditions', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('utility_buyer', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('utility_seller', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('accepted', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('rejected', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('round_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('actor', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('rationale', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('strategy', sa.String(length=50), nullable=True))
        
        # Add foreign key constraint for negotiation_session_id
        batch_op.create_foreign_key(
            'fk_offers_negotiation_session_id',
            'negotiation_sessions',
            ['negotiation_session_id'],
            ['id']
        )
        
        # Remove server defaults after adding columns
        batch_op.alter_column('term_months', server_default=None)
        batch_op.alter_column('accepted', server_default=None)
        batch_op.alter_column('rejected', server_default=None)


def downgrade() -> None:
    """Reverse the changes."""
    
    with op.batch_alter_table('offers', schema=None) as batch_op:
        # Drop new columns
        batch_op.drop_constraint('fk_offers_negotiation_session_id', type_='foreignkey')
        batch_op.drop_column('strategy')
        batch_op.drop_column('rationale')
        batch_op.drop_column('actor')
        batch_op.drop_column('round_number')
        batch_op.drop_column('rejected')
        batch_op.drop_column('accepted')
        batch_op.drop_column('utility_seller')
        batch_op.drop_column('utility_buyer')
        batch_op.drop_column('conditions')
        batch_op.drop_column('value_adds')
        batch_op.drop_column('discount_percent')
        batch_op.drop_column('term_months')
        batch_op.drop_column('negotiation_session_id')
        
        # Re-add old columns
        batch_op.add_column(sa.Column('offer_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('valid_until', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'))
        batch_op.add_column(sa.Column('compliance_gaps', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('compliance_met', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('features_excluded', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('features_included', postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('discount_percentage', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('contract_term_months', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('total_price', sa.Float(), nullable=False, server_default='0'))
