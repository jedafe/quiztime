import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from app.models import BadgeDefinition, UserBadge, XpEvent, EmailToken, User
from app.database import get_db
from tests.conftest import TestSessionLocal


BADGES_DATA = [
    {"key": "first_quiz", "name": "First Quiz", "description": "Complete your first quiz", "icon": "🎯"},
    {"key": "perfect_score", "name": "Perfect Score", "description": "Get 100% on any quiz", "icon": "💯"},
    {"key": "quiz_creator", "name": "Quiz Creator", "description": "Create 5 quizzes", "icon": "✍️"},
    {"key": "streak_master", "name": "Streak Master", "description": "Maintain a 7-day streak", "icon": "🔥"},
    {"key": "knowledge_seeker", "name": "Knowledge Seeker", "description": "Complete 50 quizzes", "icon": "📚"},
    {"key": "centurion", "name": "Centurion", "description": "Reach level 10", "icon": "🏅"},
]


@pytest_asyncio.fixture(autouse=True)
async def seed_badges():
    async with TestSessionLocal() as session:
        for b in BADGES_DATA:
            existing = await session.execute(select(BadgeDefinition).where(BadgeDefinition.key == b["key"]))
            if not existing.scalar_one_or_none():
                session.add(BadgeDefinition(**b))
        await session.commit()


def _make_question(quiz_id, subcategory_id):
    from app.models import Question
    return Question(
        quiz_id=quiz_id, subcategory_id=subcategory_id,
        type="single", text="Test?",
        options=["A", "B"], answer=[0],
    )


class TestXpEarning:
    async def test_xp_on_quiz_complete(self, client: AsyncClient, auth_headers, subcategory):
        # Create quiz + question
        q_res = await client.post("/api/quizzes", json={"title": "XP Test", "description": ""}, headers=auth_headers)
        quiz = q_res.json()
        await client.post(f"/api/questions/{quiz['id']}", json={
            "subcategory_id": subcategory["id"], "type": "single", "text": "Q?",
            "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        res = await client.post("/api/attempts", json={
            "quiz_id": quiz["id"], "answers": {}, "time_spent": 10,
        }, headers=auth_headers)
        assert res.status_code == 201

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        assert prof.json()["xp"] >= 10
        assert prof.json()["level"] >= 1

    async def test_perfect_score_bonus_xp(self, client: AsyncClient, auth_headers, subcategory):
        q_res = await client.post("/api/quizzes", json={"title": "Perfect Test", "description": ""}, headers=auth_headers)
        quiz = q_res.json()
        await client.post(f"/api/questions/{quiz['id']}", json={
            "subcategory_id": subcategory["id"], "type": "single", "text": "Q?",
            "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        # Submit correct answer to get perfect score
        q_take = await client.get(f"/api/quizzes/{quiz['id']}/take", headers=auth_headers)
        q_id = str(q_take.json()["questions"][0]["id"])
        res = await client.post("/api/attempts", json={
            "quiz_id": quiz["id"], "answers": {q_id: [0]}, "time_spent": 10,
        }, headers=auth_headers)
        assert res.status_code == 201

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        assert prof.json()["xp"] >= 60

    async def test_xp_history(self, client: AsyncClient, auth_headers, created_quiz, subcategory):
        # Add a question so XP > 0
        await client.post(f"/api/questions/{created_quiz['id']}", json={
            "subcategory_id": subcategory["id"], "type": "single", "text": "Q?",
            "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {}, "time_spent": 10,
        }, headers=auth_headers)

        res = await client.get("/api/gamification/xp-history", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] > 0
        assert data["items"][0]["source"] == "quiz_complete"
        assert data["items"][0]["amount"] > 0

    async def test_create_quiz_xp(self, client: AsyncClient, auth_headers):
        prof_before = await client.get("/api/gamification/my-profile", headers=auth_headers)
        xp_before = prof_before.json()["xp"]

        await client.post("/api/quizzes", json={"title": "XP Creation", "description": ""}, headers=auth_headers)

        prof_after = await client.get("/api/gamification/my-profile", headers=auth_headers)
        assert prof_after.json()["xp"] == xp_before + 25

    async def test_level_up(self, client: AsyncClient, auth_headers, created_quiz, subcategory):
        # Add a question so each attempt gives 10 XP
        await client.post(f"/api/questions/{created_quiz['id']}", json={
            "subcategory_id": subcategory["id"], "type": "single", "text": "Q?",
            "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)
        # Complete many quizzes to earn XP
        for i in range(20):
            res = await client.post("/api/attempts", json={
                "quiz_id": created_quiz["id"], "answers": {}, "time_spent": 10,
            }, headers=auth_headers)
            assert res.status_code == 201

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        assert prof.json()["level"] > 1


class TestBadges:
    async def test_first_quiz_badge(self, client: AsyncClient, auth_headers, created_quiz):
        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {}, "time_spent": 10,
        }, headers=auth_headers)

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        badge_keys = [b["key"] for b in prof.json()["badges"] if b["earned_at"]]
        assert "first_quiz" in badge_keys

    async def test_perfect_score_badge(self, client: AsyncClient, auth_headers, subcategory):
        q_res = await client.post("/api/quizzes", json={"title": "Badge Test", "description": ""}, headers=auth_headers)
        quiz = q_res.json()
        await client.post(f"/api/questions/{quiz['id']}", json={
            "subcategory_id": subcategory["id"], "type": "single", "text": "Q?",
            "options": ["A", "B"], "answer": [0],
        }, headers=auth_headers)

        q_take = await client.get(f"/api/quizzes/{quiz['id']}/take", headers=auth_headers)
        q_id = str(q_take.json()["questions"][0]["id"])
        await client.post("/api/attempts", json={
            "quiz_id": quiz["id"], "answers": {q_id: [0]}, "time_spent": 10,
        }, headers=auth_headers)

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        badge_keys = [b["key"] for b in prof.json()["badges"] if b["earned_at"]]
        assert "perfect_score" in badge_keys

    async def test_no_perfect_badge_on_partial(self, client: AsyncClient, auth_headers, created_quiz):
        await client.post("/api/attempts", json={
            "quiz_id": created_quiz["id"], "answers": {}, "time_spent": 10,
        }, headers=auth_headers)

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        badge_keys = [b["key"] for b in prof.json()["badges"] if b["earned_at"]]
        assert "perfect_score" not in badge_keys

    async def test_badge_all_badges_listed(self, client: AsyncClient, auth_headers):
        res = await client.get("/api/gamification/badges", headers=auth_headers)
        assert res.status_code == 200
        badges = res.json()
        assert len(badges) == 6
        keys = [b["key"] for b in badges]
        assert "first_quiz" in keys
        assert "centurion" in keys

    async def test_badge_not_duplicated(self, client: AsyncClient, auth_headers, created_quiz):
        for i in range(3):
            await client.post("/api/attempts", json={
                "quiz_id": created_quiz["id"], "answers": {}, "time_spent": 10,
            }, headers=auth_headers)

        prof = await client.get("/api/gamification/my-profile", headers=auth_headers)
        first_quiz_badges = [b for b in prof.json()["badges"] if b["key"] == "first_quiz" and b["earned_at"]]
        assert len(first_quiz_badges) == 1


class TestProfile:
    async def test_my_profile_structure(self, client: AsyncClient, auth_headers):
        res = await client.get("/api/gamification/my-profile", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "xp" in data
        assert "level" in data
        assert "streak_count" in data
        assert "badges" in data
        assert "email_verified" in data

    async def test_other_user_profile(self, client: AsyncClient, auth_headers, registered_user):
        res = await client.get(f"/api/gamification/profile/{registered_user['user']['id']}")
        assert res.status_code == 200
        assert res.json()["username"] == registered_user["user"]["username"]

    async def test_profile_not_found(self, client: AsyncClient):
        res = await client.get("/api/gamification/profile/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404


class TestXpLeaderboard:
    async def test_leaderboard_returns_users(self, client: AsyncClient, auth_headers):
        res = await client.get("/api/gamification/leaderboard")
        assert res.status_code == 200
        entries = res.json()
        assert isinstance(entries, list)
        if entries:
            assert "rank" in entries[0]
            assert "xp" in entries[0]
            assert "level" in entries[0]


class TestEmailVerification:
    async def test_register_creates_token(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "emailtest",
            "email": "email@example.com",
            "password": "testpass123",
        })
        assert res.status_code == 201

        async with TestSessionLocal() as session:
            user = await session.execute(select(User).where(User.username == "emailtest"))
            user = user.scalar_one_or_none()
            assert user is not None
            assert user.email_verified == False

            tokens = await session.execute(
                select(EmailToken).where(EmailToken.user_id == user.id, EmailToken.type == "verify")
            )
            token_records = tokens.scalars().all()
            assert len(token_records) >= 1
            assert token_records[0].type == "verify"
            assert token_records[0].used == False

    async def test_email_verified_in_response(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "emailtest2",
            "email": "email2@example.com",
            "password": "testpass123",
        })
        data = res.json()
        assert data["user"]["email_verified"] == False

    async def test_verify_email_success(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "username": "verifyme",
            "email": "verify@example.com",
            "password": "testpass123",
        })
        assert res.status_code == 201

        async with TestSessionLocal() as session:
            user = await session.execute(select(User).where(User.username == "verifyme"))
            user = user.scalar_one()
            token = await session.execute(
                select(EmailToken).where(EmailToken.user_id == user.id, EmailToken.type == "verify", EmailToken.used == False)
            )
            token_record = token.scalar_one()

        res = await client.post("/api/email/verify", json={"token": token_record.token})
        assert res.status_code == 200
        assert res.json()["message"] == "Email verified successfully"

        # Verify user is now verified
        async with TestSessionLocal() as session:
            user2 = await session.execute(select(User).where(User.username == "verifyme"))
            assert user2.scalar_one().email_verified == True

    async def test_verify_email_invalid_token(self, client: AsyncClient):
        res = await client.post("/api/email/verify", json={"token": "badtoken"})
        assert res.status_code == 400

    async def test_resend_verification(self, client: AsyncClient, auth_headers):
        res = await client.post("/api/email/resend-verification", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["message"] == "Verification email sent"

    async def test_resend_when_already_verified(self, client: AsyncClient, auth_headers):
        # Manually set user as verified
        async with TestSessionLocal() as session:
            user = await session.execute(select(User).where(User.username == "testuser"))
            user = user.scalar_one()
            user.email_verified = True
            await session.commit()

        res = await client.post("/api/email/resend-verification", headers=auth_headers)
        assert res.status_code == 400

    async def test_forgot_password_unknown_email(self, client: AsyncClient):
        res = await client.post("/api/email/forgot-password", json={"email": "nobody@example.com"})
        assert res.status_code == 200

    async def test_reset_password_success(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "username": "resetme",
            "email": "reset@example.com",
            "password": "oldpass123",
        })

        # Request password reset first to create a reset token
        await client.post("/api/email/forgot-password", json={"email": "reset@example.com"})

        async with TestSessionLocal() as session:
            user = await session.execute(select(User).where(User.username == "resetme"))
            user = user.scalar_one()
            token = await session.execute(
                select(EmailToken).where(EmailToken.user_id == user.id, EmailToken.type == "reset", EmailToken.used == False)
            )
            token_record = token.scalar_one()

        # Reset password
        res = await client.post("/api/email/reset-password", json={
            "token": token_record.token,
            "new_password": "newpass123",
        })
        assert res.status_code == 200

        # Login with new password
        res = await client.post("/api/auth/login", json={"username": "resetme", "password": "newpass123"})
        assert res.status_code == 200

        # Old password fails
        res = await client.post("/api/auth/login", json={"username": "resetme", "password": "oldpass123"})
        assert res.status_code == 401

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        res = await client.post("/api/email/reset-password", json={
            "token": "badtoken", "new_password": "newpass123",
        })
        assert res.status_code == 400
