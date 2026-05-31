"""Shared pytest fixtures for IssueFlow eval task tests (backend)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


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
def make_user(client):
    counter = {"n": 0}

    def _make(*, email: str | None = None, name: str | None = None) -> dict:
        counter["n"] += 1
        payload = {
            "email": email or f"eval-user{counter['n']}@issueflow.test",
            "name": name or f"Eval User {counter['n']}",
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture()
def make_issue(client):
    def _make(**kwargs) -> dict:
        payload = {
            "title": kwargs.get("title", "Eval task issue"),
            "description": kwargs.get("description", "Created for eval task test"),
            "priority": kwargs.get("priority", "medium"),
        }
        if kwargs.get("assignee_id") is not None:
            payload["assignee_id"] = kwargs["assignee_id"]
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
