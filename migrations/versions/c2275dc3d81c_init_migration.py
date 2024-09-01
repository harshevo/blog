"""init_migration

Revision ID: c2275dc3d81c
Revises: 
Create Date: 2024-09-02 02:48:00.530662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2275dc3d81c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('fullname', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('profile_picture_url', sa.String(), nullable=True),
    sa.Column('bio_txt', sa.String(), nullable=True),
    sa.Column('role', sa.Enum('USER', 'AUTHOR', 'ADMIN', name='powerrole'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('users_pkey')),
    sa.UniqueConstraint('email', name=op.f('users_email_key')),
    sa.UniqueConstraint('password_hash', name=op.f('users_password_hash_key')),
    sa.UniqueConstraint('username', name=op.f('users_username_key'))
    )
    op.create_table('refresh_tokens',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('refresh_tokens_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('refresh_tokens_pkey')),
    sa.UniqueConstraint('token', name=op.f('refresh_tokens_token_key'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    # ### end Alembic commands ###
