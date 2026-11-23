import sqlalchemy as sa


def upgrade(op):
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_projects_archived", "projects", ["archived"])


def downgrade(op):
    op.drop_index("ix_projects_archived", table_name="projects")
    op.drop_table("projects")
