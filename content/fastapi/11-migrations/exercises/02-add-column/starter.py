import sqlalchemy as sa


def upgrade(op):
    op.add_column("tasks", sa.Column("status", sa.String(20), nullable=False))


def downgrade(op):
    op.drop_column("tasks", "status")
