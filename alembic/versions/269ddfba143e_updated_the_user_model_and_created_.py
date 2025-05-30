"""updated the user model and created documents

Revision ID: 269ddfba143e
Revises: 809cbc92e6e0
Create Date: 2025-05-20 22:10:05.167271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '269ddfba143e'
down_revision: Union[str, None] = '809cbc92e6e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.Column('is_private_document', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.add_column('users', sa.Column('username', sa.String(), nullable=False))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'username')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    # ### end Alembic commands ###
