import { BaseCRUDAPI } from "../base/base-clients";
import type {
  CreateMealQueueItem,
  ReadMealQueueItem,
  UpdateMealQueueItem,
} from "~/lib/api/types/meal-queue";

const prefix = "/api";

const routes = {
  mealQueue: `${prefix}/households/meal-queue`,
  mealQueueClearEaten: `${prefix}/households/meal-queue/eaten`,
  mealQueueId: (id: string | number) => `${prefix}/households/meal-queue/${id}`,
  mealQueueEaten: (id: string | number) => `${prefix}/households/meal-queue/${id}/eaten`,
};

export class MealQueueAPI extends BaseCRUDAPI<CreateMealQueueItem, ReadMealQueueItem, UpdateMealQueueItem> {
  override baseRoute = routes.mealQueue;
  override itemRoute = routes.mealQueueId;

  /** List queue entries. Pass `includeEaten: true` to also fetch items already ticked off. */
  async getAllQueued(includeEaten = false) {
    return await this.getAll(1, -1, { includeEaten });
  }

  /** Remove every already-eaten entry from the queue. Returns the deleted items. */
  async clearEaten() {
    return await this.requests.delete<ReadMealQueueItem[]>(routes.mealQueueClearEaten);
  }

  async setEaten(id: string | number, eaten: boolean) {
    return await this.requests.put<ReadMealQueueItem, null>(routes.mealQueueEaten(id), null, {
      params: { eaten },
    });
  }
}
