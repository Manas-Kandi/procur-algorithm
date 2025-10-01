"""add_outcome_columns_to_negotiations

Revision ID: 1a4aa556ba91
Revises: 20250930_052
Create Date: 2025-10-01 00:43:06.037602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a4aa556ba91'
down_revision: Union[str, None] = '20250930_052'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add outcome and outcome_reason columns to negotiation_sessions
    op.add_column('negotiation_sessions', sa.Column('outcome', sa.String(50), nullable=True))
    op.add_column('negotiation_sessions', sa.Column('outcome_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove outcome columns
    op.drop_column('negotiation_sessions', 'outcome_reason')
    op.drop_column('negotiation_sessions', 'outcome')
