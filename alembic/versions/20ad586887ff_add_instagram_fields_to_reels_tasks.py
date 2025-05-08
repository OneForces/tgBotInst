"""add instagram fields to reels_tasks

Revision ID: 20ad586887ff
Revises: e276ed4a34fc
Create Date: 2025-05-08 19:35:48.080933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20ad586887ff'
down_revision: Union[str, None] = 'e276ed4a34fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
