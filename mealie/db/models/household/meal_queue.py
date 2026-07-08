import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.datetime import NaiveDateTime
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..recipe import RecipeModel


class MealQueueItem(SqlAlchemyBase, BaseMixins):
    """
    A simple, undated "meal queue" (a.k.a. meal backlog).

    Unlike `GroupMealPlan`, entries here are NOT tied to a calendar date. They represent
    meals the household has decided to make "at some point soon" without committing to a
    specific day. Entries are consumed (ticked off) whenever they're actually cooked/eaten,
    and any remaining ("uneaten") entries can be bulk-added to a shopping list.

    This model intentionally stores `group_id` / `household_id` / `user_id` directly
    (denormalized) rather than deriving them via association proxies through the `User`
    model, so this feature can live entirely in its own file(s) without requiring changes
    to `User`/`Group`/`RecipeModel` relationships. This keeps the fork's diff against
    upstream mealie small and easy to carry forward across upgrades.
    """

    __tablename__ = "meal_queue_items"

    group_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, ForeignKey("households.id"), nullable=False, index=True
    )
    user_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("users.id"), index=True)

    recipe_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship("RecipeModel", uselist=False, viewonly=True)

    title: FilterableColumn[str] = mapped_column(String, nullable=False, default="")
    note: FilterableColumn[str] = mapped_column(String, nullable=False, default="")

    eaten: FilterableColumn[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    eaten_at: FilterableColumn[datetime.datetime | None] = mapped_column(NaiveDateTime, nullable=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
