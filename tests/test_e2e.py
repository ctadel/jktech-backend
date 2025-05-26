import io
import pytest

BASE_URL = "http://localhost:8000"  # Adjust if different

test_user = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "strongpassword",
    "full_name": "Test User"
}

@pytest.mark.asyncio
async def test_full_e2e_flow(client):

    # 1. Register
    res = await client.post("/users/auth/register", json=test_user)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login
    login_payload = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    res = await client.post("/users/auth/login", json=login_payload)
    assert res.status_code == 200
    access_token = res.json()["access_token"]
    assert access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3 upload a document
    file = io.BytesIO(b"test content")
    response = await client.post(
        "/documents",
        headers=headers,
        files={"file": ("test.txt", file)},
        data={"title": "Test Doc", "is_private": "false"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Doc"
    assert "document_key" in response.json()

    # 4. Public Explore
    res = await client.get("/documents/public/explore")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 5. Get a document and check ingestion status
    public_docs = res.json()
    assert len(public_docs) > 0
    document_id = public_docs[0]["id"]

    res = await client.get(f"/llm/ingestion_status/{document_id}")
    assert res.status_code == 200
    assert "ingestion_status" in res.json()

    # 6. Start a conversation
    convo_payload = {
        "document_id": document_id,
        "title": "My Test Conversation"
    }
    res = await client.post("/conversations", json=convo_payload, headers=headers)
    assert res.status_code == 200
    convo_id = res.json()["id"]

    # 7. Post a message to the conversation
    message_payload = {
        "role": "user",
        "content": "Hello LLM, what is this document about?"
    }
    res = await client.post(f"/conversations/{convo_id}", json=message_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["content"]

    # 8. Retrieve conversation messages
    res = await client.get(f"/conversations/{convo_id}", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
