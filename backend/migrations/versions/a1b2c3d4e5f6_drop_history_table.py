"""Drop history table

Revision ID: a1b2c3d4e5f6
Revises: be2e632c1407
Create Date: 2026-04-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'be2e632c1407'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_index('ix_history_watched_at')
        batch_op.drop_index('ix_history_user_id')
        batch_op.drop_index('ix_history_media_id')

    op.drop_table('history')


def downgrade():
    op.create_table(
        'history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('media_id', sa.Integer(), nullable=False),
        sa.Column('watched_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['media_id'], ['media.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.create_index('ix_history_watched_at', ['watched_at'], unique=False)
        batch_op.create_index('ix_history_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_history_media_id', ['media_id'], unique=False)
