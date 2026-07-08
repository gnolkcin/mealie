import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import type { CreateMealQueueItem, ReadMealQueueItem, UpdateMealQueueItem } from "~/lib/api/types/meal-queue";

/**
 * `useMealQueue` manages the household's undated "meal queue" (a.k.a. meal backlog):
 * meals the household has decided to make soon without pinning them to a calendar date.
 * This mirrors the shape of `useMealplans` (see use-group-mealplan.ts) but has no date range.
 */
export const useMealQueue = function () {
  const api = useUserApi();
  const loading = ref(false);
  const includeEaten = ref(false);

  const queueItems = ref<ReadMealQueueItem[]>([]);

  const actions = {
    async refreshAll() {
      loading.value = true;
      const { data } = await api.mealQueue.getAllQueued(includeEaten.value);
      if (data) {
        queueItems.value = data.items;
      }
      loading.value = false;
    },
    async createOne(payload: CreateMealQueueItem) {
      loading.value = true;
      const { data } = await api.mealQueue.createOne(payload);
      if (data) {
        await this.refreshAll();
      }
      loading.value = false;
      return data;
    },
    async updateOne(payload: UpdateMealQueueItem) {
      loading.value = true;
      const { data } = await api.mealQueue.updateOne(payload.id, payload);
      if (data) {
        await this.refreshAll();
      }
      loading.value = false;
    },
    async setEaten(id: number, eaten: boolean) {
      // optimistic update so the checkbox feels instant
      const item = queueItems.value.find(i => i.id === id);
      if (item) {
        item.eaten = eaten;
      }
      const { data } = await api.mealQueue.setEaten(id, eaten);
      if (data && !includeEaten.value && eaten) {
        queueItems.value = queueItems.value.filter(i => i.id !== id);
      }
      return data;
    },
    async deleteOne(id: number) {
      loading.value = true;
      const { data } = await api.mealQueue.deleteOne(id);
      if (data) {
        await this.refreshAll();
      }
      loading.value = false;
    },
    async clearEaten() {
      loading.value = true;
      await api.mealQueue.clearEaten();
      await this.refreshAll();
      loading.value = false;
    },
    /**
     * Add a random recipe to the queue. Fetches a small random page of recipes
     * (server-side `orderBy=random`, which requires a paginationSeed) and prefers
     * one that isn't already sitting uneaten in the queue.
     */
    async addRandom() {
      loading.value = true;
      const { data } = await api.recipes.getAll(1, 5, {
        orderBy: "random",
        paginationSeed: Date.now().toString(),
        orderDirection: "asc",
      });

      const candidates = data?.items ?? [];
      if (!candidates.length) {
        loading.value = false;
        return null;
      }

      const queuedRecipeIds = new Set(
        queueItems.value.filter(i => !i.eaten && i.recipeId).map(i => i.recipeId),
      );
      const pick = candidates.find(r => r.id && !queuedRecipeIds.has(r.id)) ?? candidates[0];
      if (!pick?.id) {
        loading.value = false;
        return null;
      }

      const created = await this.createOne({ recipeId: pick.id });
      loading.value = false;
      return created;
    },
  };

  useAsyncData(useAsyncKey(), async () => {
    await actions.refreshAll();
    return true;
  });

  watch(includeEaten, actions.refreshAll);

  const uneatenItems = computed(() => queueItems.value.filter(i => !i.eaten));

  return { queueItems, uneatenItems, includeEaten, actions, loading };
};
