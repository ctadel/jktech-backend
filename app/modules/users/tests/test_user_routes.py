import pytest
from httpx import AsyncClient
from app.common.endpoints import BASE_ENDPOINT as EP

session_token = None
def get_header():
    return {"Authorization": session_token}

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(EP.Users.Auth.route('REGISTER'), json={
        "username": "newuser",
        "email": "new@example.com",
        "full_name": "New User",
        "password": "newpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_user(client):
    response = await client.post(EP.Users.Auth.route('LOGIN'), json={
        "username": "newuser",
        "password": "newpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    global session_token
    session_token = 'Bearer ' + response.json()['access_token']

@pytest.mark.asyncio
async def test_get_user_profile(client):
    response = await client.get(EP.Users.Profile.route('GET_USER_PROFILE'), headers=get_header())
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"

@pytest.mark.asyncio
async def test_update_user_profile(client):
    response = await client.patch(EP.Users.Profile.route('UPDATE_PROFILE'), headers=get_header(), json={
        "full_name": "New Updated Name",
        "email": "updated@gmail.com"
    })
    assert response.status_code == 200
    assert "user" in response.json()

@pytest.mark.asyncio
async def test_validate_updated_profile(client):
    response = await client.get(EP.Users.Profile.route('GET_USER_PROFILE'), headers=get_header())
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Updated Name"
    assert response.json()["email"] == "updated@gmail.com"

@pytest.mark.asyncio
async def test_upgrade_account(client):
    response = await client.post(EP.Users.Profile.route('UPDATE_ACCOUNT_TYPE'), headers=get_header(), json={
        "account_type": "PREMIUM"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_password(client):
    response = await client.patch(EP.Users.Profile.route('UPDATE_PASSWORD'), headers=get_header(), json={
        "old_password": "newpass123",
        "new_password": "newpass456"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_with_new_password(client):
    response = await client.post(EP.Users.Auth.route('LOGIN'), json={
        "username": "newuser",
        "password": "newpass456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
