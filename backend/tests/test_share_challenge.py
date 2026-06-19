import pytest
from httpx import AsyncClient


class TestShare:
    async def test_create_share_link(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        assert att.status_code == 201

        res = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": att.json()["id"],
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "code" in data
        assert "share_url" in data
        assert "og_url" in data
        assert len(data["code"]) == 12

    async def test_create_share_link_dedup(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        r1 = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": att.json()["id"],
        }, headers=auth_headers)
        r2 = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": att.json()["id"],
        }, headers=auth_headers)
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["code"] == r2.json()["code"]

    async def test_create_share_link_no_auth(self, client: AsyncClient, created_quiz):
        res = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": "00000000-0000-0000-0000-000000000000",
        })
        assert res.status_code in (401, 403)

    async def test_create_share_link_attempt_not_found(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": "00000000-0000-0000-0000-000000000000",
        }, headers=auth_headers)
        assert res.status_code == 404

    async def test_get_share_link(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        share = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": att.json()["id"],
        }, headers=auth_headers)

        res = await client.get(f"/api/share/{share.json()['code']}")
        assert res.status_code == 200
        data = res.json()
        assert data["score"] == 1
        assert data["total"] == 1
        assert data["percentage"] == 100.0
        assert data["grade"] == "Excellent"
        assert data["quiz_title"] == created_quiz["title"]

    async def test_get_share_link_404(self, client: AsyncClient):
        res = await client.get("/api/share/nonexistent")
        assert res.status_code == 404

    async def test_share_og_page(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        share = await client.post("/api/share", json={
            "quiz_id": created_quiz["id"], "attempt_id": att.json()["id"],
        }, headers=auth_headers)

        res = await client.get(f"/api/share/{share.json()['code']}/og")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        assert "og:title" in res.text
        assert "og:image" in res.text

    async def test_share_og_page_404(self, client: AsyncClient):
        res = await client.get("/api/share/nonexistent/og")
        assert res.status_code == 404


class TestChallenge:
    async def test_create_challenge(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)

        res = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"],
            "score_to_beat": 1,
            "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["challenge_code"]
        assert data["status"] == "pending"
        assert data["score_to_beat"] == 1
        assert data["total_questions"] == 1
        assert data["challenger_username"] == "testuser"

    async def test_create_challenge_no_auth(self, client: AsyncClient, created_quiz):
        res = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": "00000000-0000-0000-0000-000000000000",
        })
        assert res.status_code in (401, 403)

    async def test_create_challenge_quiz_not_found(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/challenges", json={
            "quiz_id": "00000000-0000-0000-0000-000000000000", "score_to_beat": 1,
            "total_questions": 1, "challenger_attempt_id": "00000000-0000-0000-0000-000000000000",
        }, headers=auth_headers)
        assert res.status_code == 404

    async def test_get_challenge(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        chal = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)

        res = await client.get(f"/api/challenges/{chal.json()['challenge_code']}")
        assert res.status_code == 200
        data = res.json()
        assert data["challenge_code"] == chal.json()["challenge_code"]
        assert data["quiz_title"] == created_quiz["title"]

    async def test_get_challenge_404(self, client: AsyncClient):
        res = await client.get("/api/challenges/nonexistent")
        assert res.status_code == 404

    async def test_accept_challenge(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        chal = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)
        code = chal.json()["challenge_code"]

        res = await client.post(f"/api/challenges/{code}/accept", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "accepted"

    async def test_accept_challenge_twice(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        chal = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)
        code = chal.json()["challenge_code"]

        await client.post(f"/api/challenges/{code}/accept", headers=auth_headers)
        res2 = await client.post(f"/api/challenges/{code}/accept", headers=auth_headers)
        assert res2.status_code == 400

    async def test_accept_challenge_404(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/challenges/nonexistent/accept", headers=auth_headers)
        assert res.status_code == 404

    async def test_my_challenges(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)

        res = await client.get("/api/challenges", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1

    async def test_my_challenges_empty(self, client: AsyncClient, auth_headers):
        res = await client.get("/api/challenges", headers=auth_headers)
        assert res.status_code == 200
        assert res.json() == []

    async def test_challenge_result_before_completion(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        chal = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)

        res = await client.get(f"/api/challenges/{chal.json()['challenge_code']}/result")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "pending"
        assert data["challenger_score"] == 1
        assert "winner" not in data or data["winner"] is None

    async def test_challenge_result_after_completion(
        self, client: AsyncClient, created_quiz, auth_headers
    ):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        chal = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)
        code = chal.json()["challenge_code"]

        # Challengee submits attempt with challenge_code linked
        # Register a second user
        res2 = await client.post("/api/auth/register", json={
            "username": "challengee", "email": "challengee@test.com", "password": "pass123",
        })
        assert res2.status_code == 201
        user2_token = res2.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Actually accept first (so challenge is accepted)
        await client.post(f"/api/challenges/{code}/accept", headers=user2_headers)

        # Submit attempt with challenge_code
        att2 = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 45,
            "challenge_code": code,
        }, headers=user2_headers)
        assert att2.status_code == 201

        # Now get result
        res = await client.get(f"/api/challenges/{code}/result")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["challenger_username"] == "testuser"
        assert data["challengee_username"] == "challengee"
        assert data["challenger_score"] == 1
        assert data["challengee_score"] == 1
        assert data["winner"] == "draw"

    async def test_challenge_result_404(self, client: AsyncClient):
        res = await client.get("/api/challenges/nonexistent/result")
        assert res.status_code == 404

    async def test_submit_attempt_with_challenge_code(
        self, client: AsyncClient, created_quiz, auth_headers
    ):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        att = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)
        chal = await client.post("/api/challenges", json={
            "quiz_id": created_quiz["id"], "score_to_beat": 1, "total_questions": 1,
            "challenger_attempt_id": att.json()["id"],
        }, headers=auth_headers)
        code = chal.json()["challenge_code"]

        # Accept challenge as another user
        res2 = await client.post("/api/auth/register", json={
            "username": "player2", "email": "p2@test.com", "password": "pass123",
        })
        user2_headers = {"Authorization": f"Bearer {res2.json()['access_token']}"}
        await client.post(f"/api/challenges/{code}/accept", headers=user2_headers)

        # Submit with challenge_code
        att2 = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 45,
            "challenge_code": code,
        }, headers=user2_headers)
        assert att2.status_code == 201

        # Verify challenge is now completed
        chal_get = await client.get(f"/api/challenges/{code}/result")
        assert chal_get.json()["status"] == "completed"

    async def test_submit_attempt_with_invalid_challenge_code(
        self, client: AsyncClient, created_quiz, auth_headers
    ):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        res = await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
            "challenge_code": "invalidcode123",
        }, headers=auth_headers)
        assert res.status_code == 201  # Attempt still works even with invalid challenge code


class TestLeaderboard:
    async def test_leaderboard_empty(self, client: AsyncClient, created_quiz, auth_headers):
        res = await client.get(f"/api/quizzes/{created_quiz['id']}/leaderboard", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["entries"] == []
        assert data["total_entries"] == 0

    async def test_leaderboard_with_attempts(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)

        # Second user
        r2 = await client.post("/api/auth/register", json={
            "username": "user2", "email": "u2@test.com", "password": "pass123",
        })
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}
        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 60,
        }, headers=h2)

        res = await client.get(f"/api/quizzes/{created_quiz['id']}/leaderboard", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_entries"] == 2
        assert len(data["entries"]) == 2

    async def test_leaderboard_ordering(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        q2 = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q2?", "options": ["A", "B", "C", "D"], "answer": [1],
        }, headers=auth_headers)
        q1_id = q.json()["id"]
        q2_id = q2.json()["id"]

        # User 1 scores 1/2
        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q1_id: [0], q2_id: [0]}, "time_spent": 30,
        }, headers=auth_headers)

        # Second user
        r2 = await client.post("/api/auth/register", json={
            "username": "user2", "email": "u2@test.com", "password": "pass123",
        })
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

        # User 2 scores 2/2
        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q1_id: [0], q2_id: [1]}, "time_spent": 60,
        }, headers=h2)

        res = await client.get(f"/api/quizzes/{created_quiz['id']}/leaderboard", headers=auth_headers)
        data = res.json()
        assert data["entries"][0]["username"] == "user2"
        assert data["entries"][0]["score"] == 2
        assert data["entries"][1]["username"] == "testuser"
        assert data["entries"][1]["score"] == 1

    async def test_leaderboard_best_attempt_only(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        q_id = q.json()["id"]

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q_id: [1]}, "time_spent": 30,
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q_id: [0]}, "time_spent": 20,
        }, headers=auth_headers)

        res = await client.get(f"/api/quizzes/{created_quiz['id']}/leaderboard", headers=auth_headers)
        data = res.json()
        assert data["total_entries"] == 1
        assert data["entries"][0]["score"] == 1

    async def test_leaderboard_period_filter(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)

        res = await client.get(
            f"/api/quizzes/{created_quiz['id']}/leaderboard?period=today", headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_entries"] == 1

    async def test_leaderboard_quiz_not_found(self, client: AsyncClient, auth_headers):
        res = await client.get(
            "/api/quizzes/00000000-0000-0000-0000-000000000000/leaderboard", headers=auth_headers
        )
        assert res.status_code == 404

    async def test_leaderboard_current_user_rank(self, client: AsyncClient, created_quiz, auth_headers):
        q = await client.post(f"/api/questions/{created_quiz['id']}", json={
            "type": "single", "text": "Q?", "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {q.json()["id"]: [0]}, "time_spent": 30,
        }, headers=auth_headers)

        res = await client.get(f"/api/quizzes/{created_quiz['id']}/leaderboard", headers=auth_headers)
        data = res.json()
        assert data["current_user_entry"] is not None
        assert data["current_user_rank"] == 1
        assert data["current_user_entry"]["username"] == "testuser"
