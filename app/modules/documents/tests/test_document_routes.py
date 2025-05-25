import pytest
import io

async def auth_header(client):
    await client.post("/users/auth/register", json={
        "username": "ctadel",
        "email": "ctadel@example.com",
        "full_name": "Test User",
        "password": "testpass"
    })

    response = await client.post("/users/auth/login", json={
        "username": "ctadel",
        "password": "testpass"
    })

    if response.status_code != 200:
        raise Exception("Login failed during test setup")

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

session_header = None

@pytest.mark.asyncio
async def test_upload_document(client):
    global session_header
    session_header = await auth_header(client)
    file = io.BytesIO(b"test content")
    response = await client.post(
        "/documents",
        headers=session_header,
        files={"file": ("test.txt", file)},
        data={"title": "Test Doc", "is_private": "false"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Doc"
    assert "document_key" in response.json()

@pytest.mark.asyncio
async def test_list_my_documents(client):
    response = await client.get("/documents/public/user/ctadel", headers=session_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_list_public_documents(client):
    response = await client.get("/documents/public/explore")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_reupload_document_with_basic_account(client):
    original = io.BytesIO(b"original")
    upload = await client.post(
        "/documents",
        headers=session_header,
        files={"file": ("file.txt", original)},
        data={"title": "v1", "is_private": "false"}
    )
    doc_key = upload.json()["document_key"]
    print(doc_key)

    # Reupload with PATCH
    version2 = io.BytesIO(b"new version")
    response = await client.patch(
        "/documents",
        headers=session_header,
        files={"file": ("file.txt", version2)},
        data={"document_key": doc_key, "title": "v2", "is_private": True}
    )
    assert response.status_code == 401
    assert 'Tier Limit Reached' in response.json()['detail']

@pytest.mark.asyncio
async def test_reupload_document(client):
    response = await client.post("/users/profile/account/update-account-type",
        headers=session_header,
        json={"account_type": "PREMIUM"}
    )
    if response.status_code != 200:
        raise Exception("Failed to upgrade to premium")

    original = io.BytesIO(b"original")
    upload = await client.post(
        "/documents",
        headers=session_header,
        files={"file": ("file.txt", original)},
        data={"title": "v1", "is_private": "false"}
    )
    doc_key = upload.json()["document_key"]

    # Reupload with PATCH
    version2 = io.BytesIO(b"new version")
    response = await client.patch(
        "/documents",
        headers=session_header,
        files={"file": ("file.txt", version2)},
        data={"document_key": doc_key, "title": "v2", "is_private": True}
    )
    assert response.status_code == 200
    assert response.json()["version"] == 2

@pytest.mark.asyncio
async def test_delete_document(client):
    file = io.BytesIO(b"delete me")
    upload = await client.post(
        "/documents",
        headers=session_header,
        files={"file": ("del.txt", file)},
        data={"title": "Delete Test", "is_private": "false"}
    )
    doc_key = upload.json()["document_key"]

    response = await client.delete(f"/documents/{doc_key}", headers=session_header)
    assert response.status_code == 200
