from fastapi.testclient import TestClient

from .main import app
from .dependencies import secret_token, query_token

client = TestClient(app)


def test_read_item():
    item_id = "plumbus"
    response = client.get(f"/items/{item_id}?token={query_token}", headers={"X-Token": secret_token})
    json_response = response.json()
    print(json_response)
    assert response.status_code == 200
    assert json_response == {
        "item_id": item_id, "name": "Plumbus"
    }


def test_read_item_bad_token():
    item_id = "foo"
    response = client.get(f"/items/{item_id}?token={query_token}", headers={"X-Token": "bad x-token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "X-Token header invalid"}


def test_read_inexistent_item():
    item_id = "baz"
    response = client.get(f"/items/{item_id}?token={query_token}", headers={"X-Token": secret_token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_create_item():
    item_id = "foobar"
    response = client.post(f"/items/?token={query_token}", headers={"X-Token": secret_token}, json={"id": item_id, "title": "Foo Bar", "description": "The Foo Barters"},)
    json_response = response.json()
    print(json_response)
    assert response.status_code == 200
    assert response.json() == {
        "id": item_id,
        "description": "The Foo Barters",
    }


def test_create_item_bad_token():
    item_id = "bazz"
    response = client.post(f"/items/?token={query_token}", headers={"X-Token": "bad x token"}, json={"id": item_id, "title": "Foo Bar", "description": "The Foo Barters"},)
    json_response = response.json()
    print(json_response)
    assert response.status_code == 400
    assert response.json() == {"detail": "X-Token header invalid"}


def test_create_existing_item():
    item_id = "gun"
    response = client.post(f"/items/?token={query_token}", headers={"X-Token": secret_token}, json={"id": item_id, "title": "Foo Bar", "description": "The Foo Barters"},)
    json_response = response.json()
    print(json_response)
    assert response.status_code == 403
    assert response.json() == {"detail": "Item already exists"}
