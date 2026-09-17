import threading

import pytest
from playwright.sync_api import Page, expect
from werkzeug.serving import make_server

from app import app


@pytest.fixture(scope="session")
def live_server():
    server = make_server("127.0.0.1", 5000, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

    yield "http://127.0.0.1:5000"

    server.shutdown()
    thread.join()


def test_home_page(page: Page, live_server: str):
    response = page.goto(f"{live_server}/")

    assert response is not None
    assert response.status == 200
    expect(page.locator("body")).to_contain_text("User Management Service")


def test_missing_user_returns_not_found(page: Page, live_server: str):
    response = page.goto(f"{live_server}/user?id=missing")

    assert response is not None
    assert response.status == 404
    expect(page.locator("body")).to_contain_text("User not found")


def test_token_endpoint_returns_token(page: Page, live_server: str):
    response = page.goto(f"{live_server}/token")

    assert response is not None
    assert response.status == 200
    payload = response.json()
    assert isinstance(payload.get("token"), str)
    assert payload["token"]