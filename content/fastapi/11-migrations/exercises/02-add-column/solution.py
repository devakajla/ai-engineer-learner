import sqlalchemy as sa


def upgrade(op):
    op.add_column("tasks", sa.Column("status", sa.String(20), nullable=False, server_default="todo"))
    op.create_index("ix_tasks_status", "tasks", ["status"])


def downgrade(op):
    op.drop_index("ix_tasks_status", table_name="tasks")
    with op.batch_alter_table("tasks") as batch:
        batch.drop_column("status")
