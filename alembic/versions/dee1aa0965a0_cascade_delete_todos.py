"""Cascade delete todos

Revision ID: dee1aa0965a0
Revises: 301c9ff2e0c5
Create Date: 2022-11-19 12:30:56.818860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dee1aa0965a0'
down_revision = '301c9ff2e0c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # valid for PostgreSQL only, there is no support for ALTER of constraints in SQLite
    op.drop_constraint('fk_todos_user_id_users', 'todos')
    op.create_foreign_key(
        'fk_todos_user_id_users',
        'todos', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    # valid for PostgreSQL only, there is no support for ALTER of constraints in SQLite
    op.drop_constraint('fk_todos_user_id_users')
    op.create_foreign_key(
        'fk_todos_user_id_users',
        'todos', 'users',
        ['user_id'], ['id'],
    )
