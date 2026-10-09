"""merge meal queue branch with upstream v3.28.0 migrations

The fork's meal queue migration (a1b2c3meaLq) and upstream's migrations since
v3.20.1 both descend from 2187537c52b8, which leaves two Alembic heads. Mealie
runs `alembic upgrade head` on startup, which refuses to run with multiple heads.
This no-op merge revision joins the two branches back into a single head.

Existing databases that already have a1b2c3meaLq applied will run the upstream
migrations they are missing and then this merge; fresh databases run both
branches. Re-parenting a1b2c3meaLq instead would make existing databases skip
the upstream migrations, so do not do that.

Revision ID: mq0merge0328
Revises: 3527efeeec34, a1b2c3meaLq
Create Date: 2026-10-09 00:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = "mq0merge0328"
down_revision: str | tuple[str, ...] | None = ("3527efeeec34", "a1b2c3meaLq")
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    pass


def downgrade():
    pass
