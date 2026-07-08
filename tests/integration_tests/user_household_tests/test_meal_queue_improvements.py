from tests.utils import api_routes  # noqa: F401  (ensures test utils import fine)
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_meal_queue_show_eaten_and_clear(api_client, unique_user: TestUser):
    # create a recipe to attach
    slug = random_string(10)
    response = api_client.post("/api/recipes", json={"name": slug}, headers=unique_user.token)
    assert response.status_code == 201
    recipe_slug = response.json()
    recipe = api_client.get(f"/api/recipes/{recipe_slug}", headers=unique_user.token).json()

    # queue two items: one recipe-based, one note-only
    r1 = api_client.post(
        "/api/households/meal-queue", json={"recipeId": recipe["id"]}, headers=unique_user.token
    )
    assert r1.status_code == 201, r1.text
    r2 = api_client.post(
        "/api/households/meal-queue", json={"title": "leftovers"}, headers=unique_user.token
    )
    assert r2.status_code == 201, r2.text

    item1 = r1.json()
    item2 = r2.json()

    # recipe summary must include the slug so the frontend can link to the recipe page
    assert item1["recipe"]["slug"] == recipe["slug"]

    # tick one off
    r = api_client.put(f"/api/households/meal-queue/{item1['id']}/eaten", headers=unique_user.token)
    assert r.status_code == 200
    assert r.json()["eaten"] is True

    # default listing hides eaten
    r = api_client.get("/api/households/meal-queue", headers=unique_user.token)
    ids = [i["id"] for i in r.json()["items"]]
    assert item2["id"] in ids and item1["id"] not in ids

    # the SHOW EATEN fix: camelCase includeEaten param must be honored
    r = api_client.get("/api/households/meal-queue?includeEaten=true", headers=unique_user.token)
    ids = [i["id"] for i in r.json()["items"]]
    assert item1["id"] in ids and item2["id"] in ids, "includeEaten=true should return eaten items"

    # clear eaten removes only the eaten entry
    r = api_client.delete("/api/households/meal-queue/eaten", headers=unique_user.token)
    assert r.status_code == 200, r.text
    deleted_ids = [i["id"] for i in r.json()]
    assert deleted_ids == [item1["id"]]

    r = api_client.get("/api/households/meal-queue?includeEaten=true", headers=unique_user.token)
    ids = [i["id"] for i in r.json()["items"]]
    assert item1["id"] not in ids and item2["id"] in ids
