import pytest
from httpx import AsyncClient
from app.models import User
from app.auth import create_access_token
from tests.conftest import TestSessionLocal


class TestCreateQuestion:
    async def test_create_single_question(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": [1],
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["text"] == "What is 2+2?"
        assert data["type"] == "single"
        assert data["answer"] == [1]

    async def test_create_multiple_question(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "multiple",
            "text": "Select even numbers",
            "options": ["1", "2", "3", "4"],
            "answer": [1, 3],
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()["answer"] == [1, 3]

    async def test_create_true_false_question(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "true-false",
            "text": "Is Python a language?",
            "options": ["True", "False"],
            "answer": [0],
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()["type"] == "true-false"

    async def test_create_question_no_auth(self, client: AsyncClient, created_quiz):
        res = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "Question?",
            "options": ["A", "B"],
            "answer": [0],
        })
        assert res.status_code in (401, 403)

    async def test_create_question_not_owner(self, client: AsyncClient, created_quiz):
        from app.auth import create_access_token
        from app.models import User

        async with TestSessionLocal() as session:
            user = User(
                username="notowner",
                email="notowner@example.com",
                hashed_password="hash",
                role="user",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            token = create_access_token(data={"sub": str(user.id)})

        res = await client.post(
            f"/api/questions/{created_quiz['id']}",
            json={
                "type": "single",
                "text": "Question?",
                "options": ["A", "B"],
                "answer": [0],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403


class TestUpdateQuestion:
    async def test_update_question(self, client: AsyncClient, created_quiz, auth_headers):
        # Create question first
        create_res = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "Original?",
            "options": ["A", "B"],
            "answer": [0],
        }, headers=auth_headers)
        q_id = create_res.json()["id"]

        # Update
        res = await client.put(f"/api/questions/{q_id}", json={
            "text": "Updated?",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["text"] == "Updated?"

    async def test_update_question_not_found(self, client: AsyncClient, auth_headers):
        res = await client.put(
            "/api/questions/00000000-0000-0000-0000-000000000000",
            json={"text": "Nope"},
            headers=auth_headers,
        )
        assert res.status_code == 404


class TestDeleteQuestion:
    async def test_delete_question(self, client: AsyncClient, created_quiz, auth_headers):
        # Create
        create_res = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "To delete?",
            "options": ["A", "B"],
            "answer": [0],
        }, headers=auth_headers)
        q_id = create_res.json()["id"]

        # Delete
        res = await client.delete(f"/api/questions/{q_id}", headers=auth_headers)
        assert res.status_code == 204

    async def test_delete_question_not_found(self, client: AsyncClient, auth_headers):
        res = await client.delete(
            "/api/questions/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert res.status_code == 404
