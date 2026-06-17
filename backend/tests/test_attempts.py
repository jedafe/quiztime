import pytest
from httpx import AsyncClient


class TestSubmitAttempt:
    async def test_submit_attempt(self, client: AsyncClient, created_quiz, auth_headers):
        # Add questions first
        q1 = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": [1],
        }, headers=auth_headers)
        q2 = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "What is 3+3?",
            "options": ["5", "6", "7", "8"],
            "answer": [1],
        }, headers=auth_headers)

        q1_id = q1.json()["id"]
        q2_id = q2.json()["id"]

        # Submit attempt with one correct, one wrong
        res = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"],
            "answers": {
                q1_id: [1],  # correct
                q2_id: [0],  # wrong
            },
            "time_spent": 60,
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["score"] == 1
        assert data["total"] == 2
        assert data["time_spent"] == 60

    async def test_submit_attempt_all_correct(self, client: AsyncClient, created_quiz, auth_headers):
        q1 = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "Q1?",
            "options": ["A", "B"],
            "answer": [0],
        }, headers=auth_headers)

        res = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"],
            "answers": {q1.json()["id"]: [0]},
            "time_spent": 30,
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()["score"] == 1
        assert res.json()["total"] == 1

    async def test_submit_attempt_empty_answers(self, client: AsyncClient, created_quiz, auth_headers):
        await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "Q?",
            "options": ["A", "B"],
            "answer": [0],
        }, headers=auth_headers)

        res = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"],
            "answers": {},
            "time_spent": 10,
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()["score"] == 0

    async def test_submit_attempt_no_auth(self, client: AsyncClient, created_quiz):
        res = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"],
            "answers": {},
            "time_spent": 10,
        })
        assert res.status_code in (401, 403)

    async def test_submit_attempt_quiz_not_found(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/attempts", json={
            "quiz_id": "00000000-0000-0000-0000-000000000000",
            "answers": {},
            "time_spent": 10,
        }, headers=auth_headers)
        assert res.status_code == 404


class TestMyAttempts:
    async def test_my_attempts_empty(self, client: AsyncClient, auth_headers):
        res = await client.get("/api/attempts/mine", headers=auth_headers)
        assert res.status_code == 200
        assert res.json() == []

    async def test_my_attempts_with_data(self, client: AsyncClient, created_quiz, auth_headers):
        # Submit an attempt
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "Q?",
            "options": ["A", "B"],
            "answer": [0],
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"],
            "answers": {q.json()["id"]: [0]},
            "time_spent": 30,
        }, headers=auth_headers)

        res = await client.get("/api/attempts/mine", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) == 1


class TestQuizStats:
    async def test_quiz_stats_no_attempts(self, client: AsyncClient, created_quiz):
        res = await client.get(f"/api/attempts/quiz/{created_quiz['id']}/stats")
        assert res.status_code == 200
        data = res.json()
        assert data["total_attempts"] == 0

    async def test_quiz_stats_with_attempts(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single",
            "text": "Q?",
            "options": ["A", "B"],
            "answer": [0],
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"],
            "answers": {q.json()["id"]: [0]},
            "time_spent": 30,
        }, headers=auth_headers)

        res = await client.get(f"/api/attempts/quiz/{created_quiz['id']}/stats")
        assert res.status_code == 200
        data = res.json()
        assert data["total_attempts"] == 1
        assert data["avg_score"] == 1.0
        assert data["best_score"] == 1
