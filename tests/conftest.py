"""
Pytest configuration and async fixtures for Cloud-Event-RSVP-Tracker.
Uses an in-memory SQLite database for isolated, fast, reproducible tests.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.app import app
from backend.models.user import User, UserRole
from backend.utils.password import hash_password
from backend.utils.jwt_utils import create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh in-memory database schema for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """FastAPI async test client overriding get_db with test session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def organizer_user(db_session: AsyncSession):
    """Fixture providing a persisted organizer user."""
    user = User(
        name="Test Organizer",
        email="organizer@test.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.ORGANIZER
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def attendee_user(db_session: AsyncSession):
    """Fixture providing a persisted attendee user."""
    user = User(
        name="Test Attendee",
        email="attendee@test.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.ATTENDEE
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def organizer_token(organizer_user: User):
    return create_access_token(data={"sub": organizer_user.id, "email": organizer_user.email, "role": organizer_user.role.value})


@pytest.fixture
def attendee_token(attendee_user: User):
    return create_access_token(data={"sub": attendee_user.id, "email": attendee_user.email, "role": attendee_user.role.value})
