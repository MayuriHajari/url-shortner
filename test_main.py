from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_shorten_and_redirect():
    # Step 1: Call /shorten
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

    # Step 2: Call /redirect
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