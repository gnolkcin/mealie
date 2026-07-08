from functools import cached_property

from fastapi import APIRouter, Depends

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.repos.repository_meal_queue import RepositoryMealQueue
from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BaseCrudController
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.meal_queue import (
    CreateMealQueueItem,
    MealQueueItemPagination,
    ReadMealQueueItem,
    SaveMealQueueItem,
    UpdateMealQueueItem,
)
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/households/meal-queue", tags=["Households: Meal Queue"])


@controller(router)
class MealQueueController(BaseCrudController):
    """
    The "meal queue" is an undated backlog of meals ("what we're cooking this week"),
    separate from the date-based meal planner/calendar. This entire controller (and the
    model/schema/repo it depends on) is additive: it does not modify any existing mealie
    route, so it can be dropped in/out of a fork with minimal merge conflicts.
    """

    @cached_property
    def repo(self) -> RepositoryMealQueue:
        return self.repos.meal_queue

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, self.t("generic.server-error"))

    @cached_property
    def mixins(self):
        return HttpRepo[CreateMealQueueItem, ReadMealQueueItem, UpdateMealQueueItem](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=MealQueueItemPagination)
    def get_all(
        self,
        q: PaginationQuery = Depends(PaginationQuery),
        include_eaten: bool = False,
    ):
        """List the household's meal queue. By default only un-eaten entries are returned."""
        if not include_eaten:
            eaten_filter = "eaten = false"
            q.query_filter = f"({q.query_filter}) AND ({eaten_filter})" if q.query_filter else eaten_filter

        if not q.order_by:
            q.order_by = "created_at"

        return self.repo.page_all(pagination=q)

    @router.post("", response_model=ReadMealQueueItem, status_code=201)
    def create_one(self, data: CreateMealQueueItem):
        """Add a new entry to the queue. Provide either `recipe_id` or a freeform `title`."""
        save_data = mapper.cast(
            data,
            SaveMealQueueItem,
            group_id=self.group_id,
            household_id=self.household_id,
            user_id=self.user.id,
        )
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=ReadMealQueueItem)
    def get_one(self, item_id: int):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=ReadMealQueueItem)
    def update_one(self, item_id: int, data: UpdateMealQueueItem):
        return self.mixins.update_one(data, item_id)

    @router.put("/{item_id}/eaten", response_model=ReadMealQueueItem)
    def set_eaten(self, item_id: int, eaten: bool = True):
        """Tick an entry off the queue (or un-tick it) without needing the full payload."""
        return self.repo.set_eaten(item_id, eaten)

    @router.delete("/{item_id}", response_model=ReadMealQueueItem)
    def delete_one(self, item_id: int):
        return self.mixins.delete_one(item_id)
