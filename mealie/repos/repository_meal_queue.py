from datetime import UTC, datetime

from mealie.db.models.household import MealQueueItem
from mealie.schema.meal_queue import ReadMealQueueItem

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryMealQueue(HouseholdRepositoryGeneric[ReadMealQueueItem, MealQueueItem]):
    def set_eaten(self, item_id: int, eaten: bool) -> ReadMealQueueItem:
        """Mark a meal queue entry as eaten (or un-eaten), stamping/clearing `eaten_at`."""
        return self.update(
            item_id,
            {"eaten": eaten, "eaten_at": datetime.now(UTC) if eaten else None},
        )

    def get_uneaten(self) -> list[ReadMealQueueItem]:
        if not self.household_id:
            raise Exception("household_id not set")

        return self.multi_query({"eaten": False}, order_by="created_at")
