import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models import QuizAttempt, Rating
from app.database import get_db, Base
from app.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    })
    resp = await client.post("/api/auth/login", json={
        "username": "testuser", "password": "password123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "password123",
    })
    # force admin role
    async with TestSessionLocal() as db:
        from app.models import User
        result = await db.execute(User.__table__.select().where(User.username == "admin"))
        user = result.first()
        await db.execute(User.__table__.update().where(User.id == user.id).values(role="admin"))
        await db.commit()

    resp = await client.post("/api/auth/login", json={
        "username": "admin", "password": "password123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def second_user_headers(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "password123",
    })
    resp = await client.post("/api/auth/login", json={
        "username": "user2", "password": "password123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def created_quiz(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/quizzes", json={
        "title": "Test Quiz for Search",
        "description": "A test quiz about programming and coding",
    }, headers=auth_headers)
    return resp.json()


@pytest.fixture
async def second_quiz(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/quizzes", json={
        "title": "Math Fundamentals",
        "description": "Basic mathematics and algebra",
    }, headers=auth_headers)
    return resp.json()


@pytest.fixture
async def created_category(client: AsyncClient, admin_headers: dict):
    resp = await client.post("/api/categories", json={"name": "SearchTest"}, headers=admin_headers)
    return resp.json()


# ── Search & Filtering Tests ──────────────────────────────

class TestSearchFiltering:
    async def test_search_by_title(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?search=Math")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Math Fundamentals"

    async def test_search_by_description(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?search=programming")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Test Quiz for Search"

    async def test_search_case_insensitive(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?search=MATH")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Math Fundamentals"

    async def test_search_no_match(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?search=zzzznonexistent")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_search_empty_string_returns_all(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?search=")
        data = resp.json()
        assert data["total"] == 2

    async def test_filter_by_category(self, client, created_quiz, auth_headers, admin_headers, created_category):
        # Add a question with the category
        cat_id = created_category["id"]
        await client.post(f"/api/questions/{created_quiz['id']}", json={
            "category_id": cat_id,
            "type": "single",
            "text": "Test question with category?",
            "options": ["A", "B", "C", "D"],
            "answer": [0],
        }, headers=auth_headers)

        resp = await client.get(f"/api/quizzes?category_id={cat_id}")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == created_quiz["id"]

    async def test_filter_by_nonexistent_category(self, client):
        resp = await client.get("/api/quizzes?category_id=00000000-0000-0000-0000-000000000000")
        data = resp.json()
        assert data["total"] == 0

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/quizzes", json={
                "title": f"Pagination Quiz {i}",
                "description": f"Pagination test quiz number {i}",
            }, headers=auth_headers)

        resp = await client.get("/api/quizzes?page=1&page_size=2")
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3
        assert len(data["items"]) == 2

        resp2 = await client.get("/api/quizzes?page=3&page_size=2")
        data2 = resp2.json()
        assert len(data2["items"]) == 1

    async def test_sort_by_newest_default(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?sort_by=newest")
        data = resp.json()
        titles = [item["title"] for item in data["items"]]
        # Second quiz should be first (most recent)
        assert titles[0] == "Math Fundamentals"

    async def test_sort_by_newest_asc(self, client, created_quiz, second_quiz):
        resp = await client.get("/api/quizzes?sort_by=newest&sort_order=asc")
        data = resp.json()
        titles = [item["title"] for item in data["items"]]
        assert titles[0] == "Test Quiz for Search"  # older first

    async def test_sort_by_popular(self, client, created_quiz, auth_headers, second_user_headers):
        # Submit an attempt for the first quiz
        qid = created_quiz["id"]
        await client.post("/api/attempts", json={
            "quiz_id": qid, "answers": {}, "time_spent": 10,
        }, headers=auth_headers)
        await client.post("/api/attempts", json={
            "quiz_id": qid, "answers": {}, "time_spent": 10,
        }, headers=second_user_headers)

        resp = await client.get("/api/quizzes?sort_by=popular")
        data = resp.json()
        assert data["items"][0]["id"] == qid
        assert data["items"][0]["attempt_count"] == 2


# ── Ratings Tests ─────────────────────────────────────────

class TestRatings:
    async def test_create_rating(self, client, created_quiz, auth_headers):
        resp = await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"],
            "score": 4,
            "review": "Great quiz!",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["score"] == 4
        assert data["review"] == "Great quiz!"
        assert data["username"] == "testuser"

    async def test_create_rating_invalid_score(self, client, created_quiz, auth_headers):
        resp = await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"],
            "score": 6,
        }, headers=auth_headers)
        assert resp.status_code == 422

    async def test_create_rating_duplicate_updates(self, client, created_quiz, auth_headers):
        await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 4,
        }, headers=auth_headers)
        resp = await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 2, "review": "Updated!",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["score"] == 2
        assert data["review"] == "Updated!"

    async def test_create_rating_nonexistent_quiz(self, client, auth_headers):
        resp = await client.post("/api/ratings", json={
            "quiz_id": "00000000-0000-0000-0000-000000000000",
            "score": 4,
        }, headers=auth_headers)
        assert resp.status_code == 404

    async def test_create_rating_unauthenticated(self, client, created_quiz):
        resp = await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 4,
        })
        assert resp.status_code in (401, 403)

    async def test_list_ratings(self, client, created_quiz, auth_headers, second_user_headers):
        await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 5, "review": "Excellent!",
        }, headers=auth_headers)
        await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 3,
        }, headers=second_user_headers)

        resp = await client.get(f"/api/ratings/{created_quiz['id']}")
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_list_ratings_empty(self, client, created_quiz):
        resp = await client.get(f"/api/ratings/{created_quiz['id']}")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_ratings_nonexistent_quiz(self, client):
        resp = await client.get("/api/ratings/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    async def test_rating_stats(self, client, created_quiz, auth_headers, second_user_headers):
        await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 5,
        }, headers=auth_headers)
        await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 3,
        }, headers=second_user_headers)

        resp = await client.get(f"/api/ratings/{created_quiz['id']}/stats")
        data = resp.json()
        assert data["avg_rating"] == 4.0
        assert data["total_ratings"] == 2
        assert data["distribution"]["5"] == 1
        assert data["distribution"]["3"] == 1
        assert data["distribution"]["1"] == 0

    async def test_my_rating(self, client, created_quiz, auth_headers):
        await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 4,
        }, headers=auth_headers)

        resp = await client.get(f"/api/ratings/{created_quiz['id']}/my", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 4

    async def test_my_rating_not_found(self, client, created_quiz, auth_headers):
        resp = await client.get(f"/api/ratings/{created_quiz['id']}/my", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_rating(self, client, created_quiz, auth_headers):
        create_resp = await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 4,
        }, headers=auth_headers)
        rating_id = create_resp.json()["id"]

        del_resp = await client.delete(f"/api/ratings/{rating_id}", headers=auth_headers)
        assert del_resp.status_code == 204

        # Verify it's gone
        resp = await client.get(f"/api/ratings/{created_quiz['id']}/my", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_rating_unauthorized(self, client, created_quiz, auth_headers, second_user_headers):
        create_resp = await client.post("/api/ratings", json={
            "quiz_id": created_quiz["id"], "score": 4,
        }, headers=auth_headers)
        rating_id = create_resp.json()["id"]

        del_resp = await client.delete(f"/api/ratings/{rating_id}", headers=second_user_headers)
        assert del_resp.status_code == 403

    async def test_sort_by_rating(self, client, auth_headers, second_user_headers):
        # Create two quizzes with different ratings
        q1 = await client.post("/api/quizzes", json={"title": "High Rated Quiz"}, headers=auth_headers)
        q2 = await client.post("/api/quizzes", json={"title": "Low Rated Quiz"}, headers=auth_headers)
        q1_id = q1.json()["id"]
        q2_id = q2.json()["id"]

        await client.post("/api/ratings", json={"quiz_id": q1_id, "score": 5}, headers=auth_headers)
        await client.post("/api/ratings", json={"quiz_id": q1_id, "score": 4}, headers=second_user_headers)
        await client.post("/api/ratings", json={"quiz_id": q2_id, "score": 1}, headers=auth_headers)

        resp = await client.get("/api/quizzes?sort_by=rating")
        data = resp.json()
        assert data["items"][0]["title"] == "High Rated Quiz"
        assert data["items"][0]["avg_rating"] == 4.5
        assert data["items"][1]["title"] == "Low Rated Quiz"
        assert data["items"][1]["avg_rating"] == 1.0
