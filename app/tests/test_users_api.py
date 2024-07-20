import random

from cuid import cuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


email_domains = [
    "gmail.com",
    "yandex.com",
    "mail.com",
]


def test_read_main():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "привет квазар"}


def test_can_add_user():
    username = cuid()
    email = f"{cuid()}@{random.choice(email_domains)}"
    res = client.post(
        "/user",
        json={"username": username, "email": email},
    )
    assert res.json()["username"] == username
    assert res.json()["email"] == email


def test_can_delete_user():
    username = cuid()
    email = f"{cuid()}@{random.choice(email_domains)}"
    res = client.post(
        "/user",
        json={"username": username, "email": email},
    )
    assert res.json()["username"] == username
    assert res.json()["email"] == email

    user_id = res.json()["id"]
    client.delete(
        f"/user/{user_id}",
    )
    res = client.get(
        f"/user/{user_id}",
    )
    assert res.status_code == 404


def test_can_update_user():
    username = cuid()
    email = f"{cuid()}@{random.choice(email_domains)}"
    res = client.post(
        "/user",
        json={"username": username, "email": email},
    )
    assert res.json()["username"] == username
    assert res.json()["email"] == email

    user_id = res.json()["id"]
    username = cuid()
    email = f"{cuid()}@{random.choice(email_domains)}"

    res = client.post(
        f"/user/{user_id}",
        json={"username": username, "email": email},
    )
    assert res.status_code == 200
    assert res.json()["username"] == username
    assert res.json()["email"] == email


def test_can_update_username_and_emai_only_user():
    username = cuid()
    email = f"{cuid()}@{random.choice(email_domains)}"
    res = client.post(
        "/user",
        json={"username": username, "email": email},
    )
    assert res.json()["username"] == username
    assert res.json()["email"] == email

    user_id = res.json()["id"]

    username = cuid()
    res = client.post(
        f"/user/{user_id}",
        json={"username": username},
    )
    assert res.status_code == 200
    assert res.json()["username"] == username

    email = f"{cuid()}@{random.choice(email_domains)}"

    res = client.post(
        f"/user/{user_id}",
        json={"email": email},
    )
    assert res.status_code == 200
    assert res.json()["email"] == email


def test_can_find_longest_username():
    username = "veeeeeeeeery_looooong_username"
    email = "veeeeeeeeery_looooong_username@mail.com"
    res = client.post(
        "/user",
        json={"username": username, "email": email},
    )
    assert res.json()["username"] == username
    assert res.json()["email"] == email

    user_id = res.json()["id"]

    res = client.get("/user/longest_usernames")
    assert res.json()[0]["username"] == username

    client.delete(
        f"/user/{user_id}",
    )

    res = client.get(
        f"/user/{user_id}",
    )
    assert res.status_code == 404


def test_can_count_users_by_email_domain():
    email_domain = "testdomain.com"
    ids = []

    for _ in range(20):
        username = cuid()
        email = f"{cuid()}@{email_domain}"
        res = client.post(
            "/user",
            json={"username": username, "email": email},
        )
        ids.append(res.json()["id"])

    res = client.post("/user/count_by_email_domain", json={"email": email_domain})

    data = res.json()
    assert data["email_domain"] == email_domain
    assert data["users_count"] == 20

    for id in ids:
        client.delete(
            f"/user/{id}",
        )
