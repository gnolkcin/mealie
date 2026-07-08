<template>
  <v-container>
    <RecipeDialogAddToShoppingList
      v-if="shoppingLists"
      v-model="state.shoppingListDialog"
      :recipes="uneatenRecipesWithScales"
      :shopping-lists="shoppingLists"
    />

    <BaseDialog
      v-model="state.addDialog"
      :title="$t('meal-plan.create-a-new-meal-plan')"
      :submit-text="$t('general.create')"
      color="primary"
      :icon="$globals.icons.foods"
      :submit-disabled="isCreateDisabled"
      can-submit
      @submit="createAndReset"
      @close="resetNewItem"
    >
      <v-card-text class="pb-0">
        <v-autocomplete
          v-if="!noteOnly"
          v-model="newItem.recipeId"
          v-model:search="search.query.value"
          :label="$t('meal-plan.meal-recipe')"
          :items="search.data.value"
          :custom-filter="normalizeFilter"
          :loading="search.loading.value"
          cache-items
          item-title="name"
          item-value="id"
          :return-object="false"
        />
        <template v-else>
          <v-text-field v-model="newItem.title" :label="$t('meal-plan.meal-title')" />
        </template>
        <v-textarea v-model="newItem.note" rows="2" :label="$t('meal-plan.meal-note')" />
      </v-card-text>
      <v-card-actions class="py-0 px-4">
        <v-switch v-model="noteOnly" class="mt-n3 mb-n4" :label="$t('meal-plan.note-only')" />
      </v-card-actions>
    </BaseDialog>

    <BaseDialog
      v-model="state.clearEatenDialog"
      :title="$t('meal-plan.clear-eaten')"
      color="error"
      :icon="$globals.icons.alertCircle"
      can-confirm
      @confirm="clearEaten"
    >
      <v-card-text>
        {{ $t('meal-plan.clear-eaten-confirmation') }}
      </v-card-text>
    </BaseDialog>

    <div class="d-flex flex-wrap align-center justify-space-between mb-2">
      <h1 class="text-h5">
        {{ $t('meal-plan.meal-queue') }}
      </h1>
      <div class="d-flex flex-wrap align-center ml-auto">
        <v-checkbox
          v-model="includeEaten"
          hide-details
          :label="$t('meal-plan.show-eaten')"
          class="my-auto mr-4"
        />
        <BaseButton
          color="error"
          variant="outlined"
          :icon="$globals.icons.delete"
          :text="$t('meal-plan.clear-eaten')"
          class="mr-2"
          @click="state.clearEatenDialog = true"
        />
        <BaseButton
          color="info"
          :icon="$globals.icons.cartCheck"
          :text="$t('meal-plan.add-all-to-list')"
          :disabled="!hasUneatenRecipes"
          :loading="state.addAllLoading"
          class="mr-2"
          @click="openShoppingListDialog"
        />
        <BaseButton
          color="info"
          :icon="$globals.icons.diceMultiple"
          :text="$t('meal-plan.random-meal')"
          :loading="state.randomLoading"
          class="mr-2"
          @click="addRandom"
        />
        <BaseButton
          color="primary"
          :icon="$globals.icons.foods"
          :text="$t('general.create')"
          @click="state.addDialog = true"
        />
      </div>
    </div>

    <v-alert v-if="!loading && queueItems.length === 0" type="info" variant="tonal">
      {{ $t('meal-plan.meal-queue-empty') }}
    </v-alert>

    <v-row>
      <v-col
        v-for="item in queueItems"
        :key="item.id"
        cols="12"
        sm="6"
        md="6"
        lg="4"
        xl="3"
      >
        <v-card
          class="queue-card"
          :class="{ 'left-color-border': !item.eaten }"
          :variant="item.eaten ? 'tonal' : 'elevated'"
        >
          <div class="d-flex align-stretch">
            <div
              class="queue-card-image flex-shrink-0"
              :class="{ 'cursor-pointer': !!recipeRoute(item) }"
              @click="openRecipe(item)"
            >
              <RecipeCardImage
                v-if="item.recipe"
                :recipe-id="item.recipe.id!"
                :slug="item.recipe.slug"
                small
                height="125"
                :icon-size="60"
              />
              <div v-else class="d-flex align-center justify-center fill-height">
                <v-icon color="primary" size="60">
                  {{ $globals.icons.primary }}
                </v-icon>
              </div>
            </div>
            <div class="d-flex align-center flex-grow-1 pa-2" style="min-width: 0;">
              <v-checkbox
                :model-value="item.eaten"
                hide-details
                class="flex-grow-0 mr-1"
                @update:model-value="(val) => actions.setEaten(item.id, !!val)"
              />
              <div
                class="flex-grow-1"
                style="min-width: 0;"
                :style="item.eaten ? 'text-decoration: line-through; opacity: 0.6;' : ''"
              >
                <component
                  :is="recipeRoute(item) ? 'router-link' : 'div'"
                  :to="recipeRoute(item) || undefined"
                  class="font-weight-medium queue-card-title"
                >
                  {{ item.recipe ? item.recipe.name : item.title }}
                </component>
                <div v-if="item.note" class="text-caption text-medium-emphasis">
                  {{ item.note }}
                </div>
              </div>
              <v-btn icon variant="text" size="small" @click="actions.deleteOne(item.id)">
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import RecipeCardImage from "~/components/Domain/Recipe/RecipeCardImage.vue";
import RecipeDialogAddToShoppingList from "~/components/Domain/Recipe/RecipeDialogAddToShoppingList.vue";
import { useMealQueue } from "~/composables/use-meal-queue";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";
import { normalizeFilter } from "~/composables/use-utils";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { ShoppingListSummary } from "~/lib/api/types/household";
import type { ReadMealQueueItem } from "~/lib/api/types/meal-queue";

const i18n = useI18n();
const api = useUserApi();
const auth = useMealieAuth();
const route = useRoute();
const router = useRouter();

useSeoMeta({
  title: i18n.t("meal-plan.meal-queue"),
});

const { queueItems, uneatenItems, includeEaten, actions, loading } = useMealQueue();

const search = useRecipeSearch(api);
const noteOnly = ref(false);

const groupSlug = computed(() => route.params.groupSlug || auth.user.value?.groupSlug || "");

function recipeRoute(item: ReadMealQueueItem): string {
  if (!item.recipe?.slug) {
    return "";
  }
  return `/g/${groupSlug.value}/r/${item.recipe.slug}`;
}

function openRecipe(item: ReadMealQueueItem) {
  const to = recipeRoute(item);
  if (to) {
    router.push(to);
  }
}

const newItem = ref({
  title: "",
  note: "",
  recipeId: undefined as string | undefined,
});

const state = ref({
  addDialog: false,
  shoppingListDialog: false,
  clearEatenDialog: false,
  addAllLoading: false,
  randomLoading: false,
});

const isCreateDisabled = computed(() => {
  if (noteOnly.value) {
    return !newItem.value.title;
  }
  return !newItem.value.recipeId;
});

function resetNewItem() {
  newItem.value = { title: "", note: "", recipeId: undefined };
  noteOnly.value = false;
}

async function createAndReset() {
  await actions.createOne({ ...newItem.value });
  resetNewItem();
}

async function addRandom() {
  state.value.randomLoading = true;
  const created = await actions.addRandom();
  state.value.randomLoading = false;
  if (!created) {
    alert.error(i18n.t("meal-plan.no-recipes-found-for-random"));
  }
}

async function clearEaten() {
  await actions.clearEaten();
}

const hasUneatenRecipes = computed(() => uneatenItems.value.some(item => !!item.recipe));

const uneatenRecipesWithScales = computed(() => {
  return uneatenItems.value
    .filter(item => !!item.recipe)
    .map(item => ({ scale: 1, ...item.recipe! }));
});

const shoppingLists = ref<ShoppingListSummary[]>();

async function getShoppingLists() {
  const { data } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
  if (data) {
    shoppingLists.value = (data.items as ShoppingListSummary[]) ?? [];
  }
}

async function openShoppingListDialog() {
  state.value.addAllLoading = true;
  await getShoppingLists();
  state.value.shoppingListDialog = true;
  state.value.addAllLoading = false;
}
</script>

<style scoped>
.left-color-border {
  border-left: 5px solid rgb(var(--v-theme-primary)) !important;
}

.queue-card {
  overflow: hidden;
}

/* Fixed-size thumbnail column: constrains the image so it can no longer
   stretch/overflow the compact card on desktop. */
.queue-card-image {
  width: 125px;
  height: 125px;
  overflow: hidden;
}

.cursor-pointer {
  cursor: pointer;
}

.queue-card-title {
  color: inherit;
  text-decoration: none;
  display: block;
}

.queue-card-title:hover {
  text-decoration: underline;
}
</style>
