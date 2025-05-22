import pytest
from httpx import AsyncClient

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

# @pytest.mark.asyncio
# async def test_login_user(client, test_user):
#     response = await client.post("/users/login", json={
#         "username": test_user.username,
#         "password": "testpass"
#     })
#     assert response.status_code == 200
#     assert "access_token" in response.json()

# @pytest.mark.asyncio
# async def test_get_user_profile(client, auth_header):
#     response = await client.get("/users/profile", headers=auth_header)
#     assert response.status_code == 200
#     assert response.json()["username"] == "testuser"

# @pytest.mark.asyncio
# async def test_update_user_profile(client, auth_header):
#     response = await client.put("/users/profile", headers=auth_header, json={
#         "full_name": "Updated Name"
#     })
#     assert response.status_code == 200
#     assert "user" in response.json()

# @pytest.mark.asyncio
# async def test_update_password(client, auth_header):
#     response = await client.put("/users/password", headers=auth_header, json={
#         "old_password": "testpass",
#         "new_password": "newpass456"
#     })
#     assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_upgrade_account(client, auth_header):
#     response = await client.put("/users/upgrade", headers=auth_header, json={
#         "new_role": "EDITOR"
#     })
#     assert response.status_code == 200
#     assert "user" in response.json()
