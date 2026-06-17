import pytest
from httpx import AsyncClient
from tests.conftest import TestSessionLocal


class TestListQuizzes:
    async def test_list_quizzes_empty(self, client: AsyncClient):
        res = await client.get("/api/quizzes")
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["total_pages"] == 0

    async def test_list_quizzes_with_data(self, client: AsyncClient, created_quiz):
        res = await client.get("/api/quizzes")
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test Quiz"
        assert data["total"] == 1
        assert data["total_pages"] == 1


class TestCreateQuiz:
    async def test_create_quiz(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/quizzes", json={
            "title": "New Quiz",
            "description": "A new quiz",
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "New Quiz"
        assert data["description"] == "A new quiz"
        assert data["question_count"] == 0

    async def test_create_quiz_no_auth(self, client: AsyncClient):
        res = await client.post("/api/quizzes", json={
            "title": "No Auth Quiz",
        })
        assert res.status_code in (401, 403)

    async def test_create_quiz_empty_title(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/quizzes", json={
            "title": "",
        }, headers=auth_headers)
        assert res.status_code == 422


class TestGetQuiz:
    async def test_get_quiz(self, client: AsyncClient, created_quiz):
        res = await client.get(f"/api/quizzes/{created_quiz['id']}")
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "Test Quiz"
        assert "questions" in data

    async def test_get_quiz_not_found(self, client: AsyncClient):
        res = await client.get("/api/quizzes/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    async def test_get_quiz_no_answers(self, client: AsyncClient, created_quiz, auth_headers):
        """Answers should NOT be in the public quiz endpoint."""
        res = await client.get(f"/api/quizzes/{created_quiz['id']}")
        data = res.json()
        for q in data.get("questions", []):
            assert "answer" not in q


class TestGetQuizManage:
    async def test_get_quiz_manage_owner(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.get(f"/api/quizzes/{created_quiz['id']}/manage", headers=auth_headers)
        assert res.status_code == 200
        assert "questions" in res.json()

    async def test_get_quiz_manage_not_owner(self, client: AsyncClient, created_quiz):
        """Non-owner should get 403."""
        from app.auth import create_access_token
        from app.models import User
        import uuid

        # Create another user
        async with TestSessionLocal() as session:
            user = User(
                username="other",
                email="other@example.com",
                hashed_password="hash",
                role="user",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            token = create_access_token(data={"sub": str(user.id)})

        res = await client.get(
            f"/api/quizzes/{created_quiz['id']}/manage",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403


class TestUpdateQuiz:
    async def test_update_quiz(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.put(f"/api/quizzes/{created_quiz['id']}", json={
            "title": "Updated Title",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["title"] == "Updated Title"

    async def test_update_quiz_not_owner(self, client: AsyncClient, created_quiz):
        from app.auth import create_access_token
        from app.models import User

        async with TestSessionLocal() as session:
            user = User(
                username="other2",
                email="other2@example.com",
                hashed_password="hash",
                role="user",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            token = create_access_token(data={"sub": str(user.id)})

        res = await client.put(
            f"/api/quizzes/{created_quiz['id']}",
            json={"title": "Hacked"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403


class TestDeleteQuiz:
    async def test_delete_quiz(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.delete(f"/api/quizzes/{created_quiz['id']}", headers=auth_headers)
        assert res.status_code == 204

        # Verify deleted
        res = await client.get(f"/api/quizzes/{created_quiz['id']}")
        assert res.status_code == 404

    async def test_delete_quiz_not_owner(self, client: AsyncClient, created_quiz):
        from app.auth import create_access_token
        from app.models import User

        async with TestSessionLocal() as session:
            user = User(
                username="other3",
                email="other3@example.com",
                hashed_password="hash",
                role="user",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            token = create_access_token(data={"sub": str(user.id)})

        res = await client.delete(
            f"/api/quizzes/{created_quiz['id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403
