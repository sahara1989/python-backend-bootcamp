"""add github_id to user

Revision ID: 7824ffbf4b06
Revises: 
Create Date: 2025-08-06 17:33:38.471178

"""

from alembic import op
import sqlalchemy as sa



revision = '7824ffbf4b06'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('github_id', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint('uq_user_github_id', ['github_id'])


def downgrade():

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_github_id', type_='unique')
        batch_op.drop_column('github_id')

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_user_id'))
        
