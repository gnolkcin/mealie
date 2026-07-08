import { BaseCRUDAPI } from "../base/base-clients";
import type {
  CreateMealQueueItem,
  ReadMealQueueItem,
  UpdateMealQueueItem,
} from "~/lib/api/types/meal-queue";

const prefix = "/api";

const routes = {
  mealQueue: `${prefix}/households/meal-queue`,
  mealQueueId: (id: string | number) => `${prefix}/households/meal-queue/${id}`,
  mealQueueEaten: (id: string | number) => `${prefix}/households/meal-queue/${id}/eaten`,
};

export class MealQueueAPI extends BaseCRUDAPI<CreateMealQueueItem, ReadMealQueueItem, UpdateMealQueueItem> {
  baseRoute = routes.mealQueue;
  itemRoute = routes.mealQueueId;

  /** List queue entries. Pass `includeEaten: true` to also fetch items already ticked off. */
  async getAllQueued(includeEaten = false) {
    return await this.getAll(1, -1, { includeEaten });
  }

  async setEaten(id: string | number, eaten: boolean) {
    return await this.requests.put<ReadMealQueueItem>(routes.mealQueueEaten(id), null, {
      params: { eaten },
    });
  }
}
