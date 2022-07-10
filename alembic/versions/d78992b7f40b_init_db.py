"""init_db

Revision ID: d78992b7f40b
Revises: 
Create Date: 2022-07-08 20:55:27.859919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd78992b7f40b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=40), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_user', sa.Integer(), nullable=True),
    sa.Column('updated_user', sa.Integer(), nullable=True),
    sa.Column('confirmed', sa.BOOLEAN(), nullable=True),
    sa.Column('last_seen', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['created_user'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    permissions = op.create_table('permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('description', sa.String(length=120), nullable=False),
    sa.Column('color', sa.String(length=40), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_user', sa.Integer(), nullable=True),
    sa.Column('updated_user', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_user'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    roles = op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('description', sa.String(length=120), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_user', sa.Integer(), nullable=True),
    sa.Column('updated_user', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_user'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    role_permission = op.create_table('role_permission',
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('permission_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], )
    )
    op.create_table('user_role',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

    # Default values
    op.bulk_insert(
        permissions,
        [
            {
                "name":"write",
                "description":"Write permission",
                "color":"#8ac926",
            },
            {
                "name":"update",
                "description":"Update permission",
                "color":"#1982c4",
            },
            {
                "name":"delete",
                "description":"Delete permission",
                "color":"#ff595e",
            }
        ],
    )
    op.bulk_insert(
        roles,
        [
            {
                "name": "admin",
                "description": "Admin role",
            },
            {
                "name": "moderate",
                "description": "Moderator role",
            },
            {
                "name": "users",
                "description": "Users role",
            },
        ],
    )
    op.bulk_insert(
        role_permission,
        [
            {
                "role_id": 1,
                "permission_id": 1,
            },
                        {
                "role_id": 1,
                "permission_id": 2,
            },
                        {
                "role_id": 1,
                "permission_id": 3,
            },
        ]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_role')
    op.drop_table('role_permission')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('users')
    # ### end Alembic commands ###