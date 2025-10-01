"""align_negotiation_sessions_schema

Revision ID: c1b4bdad2f62
Revises: 1a4aa556ba91
Create Date: 2025-10-01 00:44:30.810041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1b4bdad2f62'
down_revision: Union[str, None] = '1a4aa556ba91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old columns that don't match the model
    op.drop_column('negotiation_sessions', 'buyer_strategy')
    op.drop_column('negotiation_sessions', 'seller_strategy')
    op.drop_column('negotiation_sessions', 'history')
    op.drop_column('negotiation_sessions', 'session_metadata')
    
    # Add new columns that match the model
    op.add_column('negotiation_sessions', sa.Column('buyer_state', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('negotiation_sessions', sa.Column('seller_state', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('negotiation_sessions', sa.Column('total_messages', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('negotiation_sessions', sa.Column('savings_achieved', sa.Float(), nullable=True))


def downgrade() -> None:
    # Reverse the changes
    op.drop_column('negotiation_sessions', 'savings_achieved')
    op.drop_column('negotiation_sessions', 'total_messages')
    op.drop_column('negotiation_sessions', 'seller_state')
    op.drop_column('negotiation_sessions', 'buyer_state')
    
    # Re-add old columns
    op.add_column('negotiation_sessions', sa.Column('session_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('negotiation_sessions', sa.Column('history', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('negotiation_sessions', sa.Column('seller_strategy', sa.String(50), nullable=True))
    op.add_column('negotiation_sessions', sa.Column('buyer_strategy', sa.String(50), nullable=True))
