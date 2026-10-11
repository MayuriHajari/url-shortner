
import random
import string

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from db import Base


@pytest.fixture
def client():
    # Separate in-memory SQLite database for this test run
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_shorten_and_redirect(client):
    response = client.post(
        "/shorten",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 201
    short_code = response.json()["short_code"]

    redirect_response = client.get(
        f"/redirect?code={short_code}",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == "https://example.com/"


def test_duplicate_url_returns_same_short_code(client):
    random_suffix = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )
    random_url = f"https://example.com/{random_suffix}"

    response1 = client.post("/shorten", json={"url": random_url})
    response2 = client.post("/shorten", json={"url": random_url})

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["short_code"] == response2.json()["short_code"]


def test_non_existent_short_code(client):
    response = client.get(
        "/redirect?code=invalid123",
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Short code not found."}


def test_delete_short_code(client):
    response = client.post(
        "/shorten",
        json={"url": "https://delete-test.com"},
    )
    assert response.status_code == 201

    short_code = response.json()["short_code"]
    delete_response = client.delete(f"/urls/{short_code}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Short code deleted successfully."
    }

    redirect_response = client.get(
        f"/redirect?code={short_code}",
        follow_redirects=False,
    )
    assert redirect_response.status_code == 404


def test_shorten_rejects_empty_url(client):
    response = client.post("/shorten", json={"url": ""})
    assert response.status_code == 422


def test_shorten_rejects_unsupported_scheme(client):
    response = client.post(
        "/shorten",
        json={"url": "ftp://example.com/file"},
    )
    assert response.status_code == 422


def test_shorten_rejects_missing_url(client):
    response = client.post("/shorten", json={})
    assert response.status_code == 422


def test_delete_nonexistent_short_code(client):
    response = client.delete("/urls/nonexistent-delete-code-987654")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short code not found."}


def test_deleted_url_cannot_be_redirected(client):
    response = client.post(
        "/shorten",
        json={"url": "https://delete-test.com/unique-isolation-test"},
    )
    assert response.status_code == 201

    short_code = response.json()["short_code"]
    delete_response = client.delete(f"/urls/{short_code}")

    assert delete_response.status_code == 200

    redirect_response = client.get(
        f"/redirect?code={short_code}",
        follow_redirects=False,
    )
    assert redirect_response.status_code == 404
