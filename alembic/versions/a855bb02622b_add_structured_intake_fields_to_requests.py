"""add_structured_intake_fields_to_requests

Revision ID: a855bb02622b
Revises: b27d1932173a
Create Date: 2025-10-07 16:16:13.556941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a855bb02622b'
down_revision: Union[str, None] = 'b27d1932173a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add structured intake fields to requests table
    op.add_column('requests', sa.Column('procurement_goal', sa.Text(), nullable=True))
    op.add_column('requests', sa.Column('timeline_deadline', sa.DateTime(), nullable=True))
    op.add_column('requests', sa.Column('timeline_urgency', sa.String(length=50), nullable=True))
    op.add_column('requests', sa.Column('risk_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove structured intake fields from requests table
    op.drop_column('requests', 'risk_notes')
    op.drop_column('requests', 'timeline_urgency')
    op.drop_column('requests', 'timeline_deadline')
    op.drop_column('requests', 'procurement_goal')
