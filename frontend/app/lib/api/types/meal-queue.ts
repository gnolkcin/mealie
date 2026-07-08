/* tslint:disable */

/**
/* Hand-written to mirror mealie/schema/meal_queue/meal_queue.py.
/* This is a fork-only feature; there is no upstream pydantic2ts export for it.
*/

import type { RecipeSummary } from "./recipe";

export interface CreateMealQueueItem {
  title?: string;
  note?: string;
  recipeId?: string | null;
}

export interface UpdateMealQueueItem extends CreateMealQueueItem {
  id: number;
  groupId: string;
  userId?: string | null;
  eaten?: boolean;
  eatenAt?: string | null;
}

export interface ReadMealQueueItem extends UpdateMealQueueItem {
  householdId: string;
  recipe?: RecipeSummary | null;
}

export interface MealQueueItemPagination {
  page: number;
  perPage: number;
  total: number;
  totalPages: number;
  items: ReadMealQueueItem[];
}
