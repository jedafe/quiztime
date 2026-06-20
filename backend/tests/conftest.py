import asyncio
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import get_db
from app.models import Base
from app.main import app


# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


# ── Helper fixtures ────────────────────────────────────
@pytest_asyncio.fixture
async def registered_user(client: AsyncClient):
    """Register a user and return the response data."""
    res = await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert res.status_code == 201
    return res.json()


@pytest_asyncio.fixture
async def admin_user(client: AsyncClient):
    """Register an admin user."""
    from app.auth import hash_password
    from app.models import User
    from app.database import get_db

    async with TestSessionLocal() as session:
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {"id": str(user.id), "username": user.username, "role": user.role}


@pytest_asyncio.fixture
def auth_headers(registered_user):
    """Return Authorization headers for the registered user."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}


@pytest_asyncio.fixture
def admin_headers(client: AsyncClient, admin_user):
    """Login as admin and return auth headers."""
    import asyncio

    async def _login():
        res = await client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123",
        })
        return res

    # We need to run this synchronously in the fixture
    # Use a different approach - create token directly
    from app.auth import create_access_token
    token = create_access_token(data={"sub": admin_user["id"]})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def created_quiz(client: AsyncClient, auth_headers):
    """Create a quiz and return it."""
    res = await client.post("/api/quizzes", json={
        "title": "Test Quiz",
        "description": "A test quiz",
    }, headers=auth_headers)
    assert res.status_code == 201
    return res.json()


@pytest_asyncio.fixture
async def category(client: AsyncClient, admin_headers):
    """Create a category as admin."""
    from app.models import Category
    async with TestSessionLocal() as session:
        cat = Category(name="Test Category")
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        return {"id": str(cat.id), "name": cat.name}


@pytest_asyncio.fixture
async def subcategory(client: AsyncClient, category):
    """Create a subcategory under the test category."""
    from app.models import Subcategory
    async with TestSessionLocal() as session:
        sub = Subcategory(name="Test Subcategory", category_id=uuid.UUID(category["id"]))
        session.add(sub)
        await session.commit()
        await session.refresh(sub)
        return {"id": str(sub.id), "name": sub.name, "category_id": category["id"]}
