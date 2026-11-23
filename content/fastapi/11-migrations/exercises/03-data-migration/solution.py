import sqlalchemy as sa


def upgrade(op):
    op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, full_name FROM users")).all()
    for row in rows:
        first, _, last = (row.full_name or "").strip().partition(" ")
        conn.execute(
            sa.text("UPDATE users SET first_name = :first, last_name = :last WHERE id = :id"),
            {"first": first, "last": last.strip(), "id": row.id},
        )
    with op.batch_alter_table("users") as batch:
        batch.drop_column("full_name")


def downgrade(op):
    op.add_column("users", sa.Column("full_name", sa.String(200), nullable=True))
    op.execute("UPDATE users SET full_name = TRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, ''))")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("first_name")
        batch.drop_column("last_name")
