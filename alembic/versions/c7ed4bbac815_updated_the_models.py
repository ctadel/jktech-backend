"""updated the models

Revision ID: c7ed4bbac815
Revises: 269ddfba143e
Create Date: 2025-05-21 15:59:07.983298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7ed4bbac815'
down_revision: Union[str, None] = '269ddfba143e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('document_key', sa.String(), nullable=False))
    op.add_column('documents', sa.Column('version', sa.Integer(), nullable=True))
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_index('ix_users_email', table_name='users')
    op.create_unique_constraint(None, 'users', ['email'])
    op.drop_column('users', 'role')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', postgresql.ENUM('ADMIN', 'EDITOR', 'VIEWER', name='userrole'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='unique')
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('documents', 'version')
    op.drop_column('documents', 'document_key')
    # ### end Alembic commands ###
