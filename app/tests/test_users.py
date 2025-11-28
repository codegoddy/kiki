import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User
from app.schemas.user import UserCreate
from app.services.user import create_user, get_user

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db_session):
    user_data = UserCreate(username="testuser", email="test@example.com", password="password")
    user = create_user(db_session, user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_get_user(db_session):
    user_data = UserCreate(username="testuser", email="test@example.com", password="password")
    created_user = create_user(db_session, user_data)
    retrieved_user = get_user(db_session, created_user.id)
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == "testuser"