"""Pytest configuration and shared fixtures for IssueFlow backend tests."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from tests.helpers import FIXED_NOW


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Session:
    session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_engine) -> TestClient:
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    with patch("app.main.init_db"), patch("app.main.seed_database"):
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()


@pytest.fixture()
def make_user_via_db(db_session):
    from app import crud

    def _make(*, email: str, name: str):
        return crud.create_user(db_session, email=email, name=name)

    return _make


@pytest.fixture()
def make_user(client):
    counter = {"n": 0}

    def _make_user(*, email: str | None = None, name: str | None = None) -> dict:
        counter["n"] += 1
        payload = {
            "email": email or f"user{counter['n']}@issueflow.test",
            "name": name or f"User {counter['n']}",
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make_user


@pytest.fixture()
def make_issue(client):
    def _make_issue(
        *,
        title: str = "Test issue",
        description: str | None = "Test description",
        priority: str = "medium",
        assignee_id: int | None = None,
    ) -> dict:
        payload: dict = {"title": title, "priority": priority}
        if description is not None:
            payload["description"] = description
        if assignee_id is not None:
            payload["assignee_id"] = assignee_id
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make_issue
