import pytest
from httpx import AsyncClient

session_token = 'Bearer '
def get_header():
    return {"Authorization": session_token}

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/users/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "full_name": "New User",
        "password": "newpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_user(client):
    response = await client.post("/users/login", json={
        "username": "newuser",
        "password": "newpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    global session_token
    session_token += response.json()['access_token']

@pytest.mark.asyncio
async def test_get_user_profile(client):
    response = await client.get("/users/profile", headers=get_header())
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"

@pytest.mark.asyncio
async def test_update_user_profile(client):
    response = await client.put("/users/profile", headers=get_header(), json={
        "full_name": "New Updated Name",
        "email": "updated@gmail.com"
    })
    assert response.status_code == 200
    assert "user" in response.json()

@pytest.mark.asyncio
async def test_validate_updated_profile(client):
    response = await client.get("/users/profile", headers=get_header())
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Updated Name"
    assert response.json()["email"] == "updated@gmail.com"

@pytest.mark.asyncio
async def test_upgrade_account(client):
    response = await client.put("/users/profile/update-account-type", headers=get_header(), json={
        "account_type": "PREMIUM"
    })
    assert response.status_code == 200
    assert "user" in response.json()

@pytest.mark.asyncio
async def test_update_password(client):
    response = await client.put("/users/password", headers=get_header(), json={
        "old_password": "newpass123",
        "new_password": "newpass456"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_with_new_password(client):
    response = await client.post("/users/login", json={
        "username": "newuser",
        "password": "newpass456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
