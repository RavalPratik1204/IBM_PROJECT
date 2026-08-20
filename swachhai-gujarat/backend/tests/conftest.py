"""pytest configuration."""
import pytest


@pytest.fixture(scope="session")
def test_db():
    """In-memory SQLite DB for integration tests."""
    import os
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["GROQ_API_KEY"] = "test_key"
    os.environ["JWT_SECRET"] = "test_secret"
    os.environ["SECRET_KEY"] = "test_app_secret"

    from app.core.database import engine, Base, SessionLocal
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
