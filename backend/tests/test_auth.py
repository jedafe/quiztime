import pytest
from httpx import AsyncClient


class TestHealthCheck:
    async def test_health_endpoint(self, client: AsyncClient):
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        })
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["role"] == "user"

    async def test_register_duplicate_username(self, client: AsyncClient, registered_user):
        res = await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "other@example.com",
            "password": "password123",
        })
        assert res.status_code == 400
        assert "already exists" in res.json()["detail"]

    async def test_register_duplicate_email(self, client: AsyncClient, registered_user):
        res = await client.post("/api/auth/register", json={
            "username": "otheruser",
            "email": "test@example.com",
            "password": "password123",
        })
        assert res.status_code == 400

    async def test_register_short_password(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "user",
            "email": "u@e.com",
            "password": "12345",
        })
        assert res.status_code == 422

    async def test_register_short_username(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "ab",
            "email": "u@e.com",
            "password": "password123",
        })
        assert res.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, registered_user):
        res = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"

    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        res = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword",
        })
        assert res.status_code == 401
        assert "Invalid credentials" in res.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        res = await client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "password",
        })
        assert res.status_code == 401


class TestMe:
    async def test_me_authenticated(self, client: AsyncClient, registered_user, auth_headers):
        res = await client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["username"] == "testuser"

    async def test_me_unauthenticated(self, client: AsyncClient):
        res = await client.get("/api/auth/me")
        assert res.status_code in (401, 403)

    async def test_me_invalid_token(self, client: AsyncClient):
        res = await client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert res.status_code == 401
