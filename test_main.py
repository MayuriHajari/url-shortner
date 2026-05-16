import random
import string

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_shorten_and_redirect():

    # Step 1: Shorten URL
    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "short_code" in data

    short_code = data["short_code"]

    # Step 2: Redirect using short code
    redirect_response = client.get(
        f"/redirect?code={short_code}",
        follow_redirects=False
    )

    # Step 3: Validate redirect
    assert redirect_response.status_code == 302

    assert (
        redirect_response.headers["location"]
        == "https://example.com/"
    )


def test_duplicate_url_returns_same_short_code():

    # Generate random URL
    random_suffix = ''.join(
        random.choices(
            string.ascii_lowercase + string.digits,
            k=8
        )
    )

    random_url = f"https://example.com/{random_suffix}"

    # First request
    response1 = client.post(
        "/shorten",
        json={
            "url": random_url
        }
    )

    assert response1.status_code == 201

    short_code_1 = response1.json()["short_code"]

    # Second request with same URL
    response2 = client.post(
        "/shorten",
        json={
            "url": random_url
        }
    )

    assert response2.status_code == 201

    short_code_2 = response2.json()["short_code"]

    # Same short code should be returned
    assert short_code_1 == short_code_2


def test_non_existent_short_code():

    response = client.get(
        "/redirect?code=invalid123",
        follow_redirects=False
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Short code not found."
    }
    
def test_delete_short_code():

    # Step 1: Create short URL
    response = client.post(
        "/shorten",
        json={
            "url": "https://delete-test.com"
        }
    )

    assert response.status_code == 201

    short_code = response.json()["short_code"]

    # Step 2: Delete short code
    delete_response = client.delete(
        f"/urls/{short_code}"
    )

    assert delete_response.status_code == 200

    assert delete_response.json() == {
        "message": "Short code deleted successfully."
    }

    # Step 3: Verify redirect no longer works
    redirect_response = client.get(
        f"/redirect?code={short_code}",
        follow_redirects=False
    )

    assert redirect_response.status_code == 404    