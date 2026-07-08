"""add meal queue items table (meal-queue fork feature)

Revision ID: a1b2c3meaLq
Revises: 2187537c52b8
Create Date: 2026-07-08 00:00:00.000000

"""

import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3meaLq"
down_revision = "2187537c52b8"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.create_table(
        "meal_queue_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("recipe_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("note", sa.String(), nullable=False),
        sa.Column("eaten", sa.Boolean(), nullable=False),
        sa.Column("eaten_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name="fk_meal_queue_items_group_id"),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"], name="fk_meal_queue_items_household_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_meal_queue_items_user_id"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], name="fk_meal_queue_items_recipe_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("meal_queue_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_meal_queue_items_group_id"), ["group_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_meal_queue_items_household_id"), ["household_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_meal_queue_items_user_id"), ["user_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_meal_queue_items_recipe_id"), ["recipe_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_meal_queue_items_eaten"), ["eaten"], unique=False)
        batch_op.create_index(batch_op.f("ix_meal_queue_items_created_at"), ["created_at"], unique=False)


def downgrade():
    with op.batch_alter_table("meal_queue_items", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_meal_queue_items_created_at"))
        batch_op.drop_index(batch_op.f("ix_meal_queue_items_eaten"))
        batch_op.drop_index(batch_op.f("ix_meal_queue_items_recipe_id"))
        batch_op.drop_index(batch_op.f("ix_meal_queue_items_user_id"))
        batch_op.drop_index(batch_op.f("ix_meal_queue_items_household_id"))
        batch_op.drop_index(batch_op.f("ix_meal_queue_items_group_id"))

    op.drop_table("meal_queue_items")
