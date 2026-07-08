from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household import MealQueueItem
from mealie.db.models.recipe import RecipeModel
from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase


class CreateMealQueueItem(MealieModel):
    """
    Add an entry to the household's meal queue. Either `recipe_id` or `title` must be
    provided (mirrors the same "recipe OR freeform title" pattern used by mealplan entries).
    """

    title: str = ""
    note: str = ""
    recipe_id: Annotated[UUID | None, Field(validate_default=True)] = None

    @field_validator("recipe_id")
    @classmethod
    def id_or_title(cls, value, info: ValidationInfo):
        if bool(value) is False and bool(info.data.get("title")) is False:
            raise ValueError(f"`recipe_id={value}` or `title={info.data.get('title')}` must be provided")

        return value


class UpdateMealQueueItem(CreateMealQueueItem):
    id: int
    group_id: UUID
    user_id: UUID | None = None
    eaten: bool = False
    eaten_at: datetime | None = None


class SaveMealQueueItem(CreateMealQueueItem):
    group_id: UUID
    household_id: UUID
    user_id: UUID | None = None
    model_config = ConfigDict(from_attributes=True)


class ReadMealQueueItem(UpdateMealQueueItem):
    household_id: UUID
    recipe: RecipeSummary | None = None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(MealQueueItem.recipe).joinedload(RecipeModel.recipe_category),
            selectinload(MealQueueItem.recipe).joinedload(RecipeModel.tags),
            selectinload(MealQueueItem.recipe).joinedload(RecipeModel.tools),
        ]


class MealQueueItemPagination(PaginationBase):
    items: list[ReadMealQueueItem]
