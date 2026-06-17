import pytest
from httpx import AsyncClient
from app.models import Category
from app.database import async_session


class TestListCategories:
    async def test_list_categories_empty(self, client: AsyncClient):
        res = await client.get("/api/categories")
        assert res.status_code == 200
        assert res.json() == []

    async def test_list_categories(self, client: AsyncClient, category):
        res = await client.get("/api/categories")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Category"


class TestCreateCategory:
    async def test_create_category_admin(self, client: AsyncClient, admin_headers):
        res = await client.post("/api/categories", json={
            "name": "Programming",
        }, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["name"] == "Programming"

    async def test_create_category_duplicate(self, client: AsyncClient, admin_headers, category):
        res = await client.post("/api/categories", json={
            "name": "Test Category",
        }, headers=admin_headers)
        assert res.status_code == 400

    async def test_create_category_non_admin(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/categories", json={
            "name": "New Category",
        }, headers=auth_headers)
        assert res.status_code == 403
