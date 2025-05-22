# import pytest
# import io

# @pytest.mark.asyncio
# async def test_upload_document(client, auth_header):
#     file = io.BytesIO(b"test content")
#     response = await client.put(
#         "/documents/upload",
#         headers=auth_header,
#         files={"file": ("test.txt", file)},
#         data={"title": "Test Doc", "is_private": "false"}
#     )
#     assert response.status_code == 200
#     assert response.json()["title"] == "Test Doc"
#     assert "document_key" in response.json()

# @pytest.mark.asyncio
# async def test_list_my_documents(client, auth_header):
#     response = await client.get("/documents/me", headers=auth_header)
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)

# @pytest.mark.asyncio
# async def test_list_public_documents(client):
#     response = await client.get("/documents/public")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)

# @pytest.mark.asyncio
# async def test_reupload_document(client, auth_header):
#     # Upload initial document
#     original = io.BytesIO(b"original")
#     upload = await client.put(
#         "/documents/upload",
#         headers=auth_header,
#         files={"file": ("file.txt", original)},
#         data={"title": "v1", "is_private": "false"}
#     )
#     doc_key = upload.json()["document_key"]

#     # Reupload with PATCH
#     version2 = io.BytesIO(b"new version")
#     response = await client.patch(
#         "/documents/upload",
#         headers=auth_header,
#         files={"file": ("file.txt", version2)},
#         data={"document_key": doc_key, "title": "v2"}
#     )
#     assert response.status_code == 200
#     assert response.json()["version"] == 2

# @pytest.mark.asyncio
# async def test_delete_document(client, auth_header):
#     # Upload first
#     file = io.BytesIO(b"delete me")
#     upload = await client.put(
#         "/documents/upload",
#         headers=auth_header,
#         files={"file": ("del.txt", file)},
#         data={"title": "Delete Test", "is_private": "false"}
#     )
#     doc_id = upload.json()["id"]

#     # Delete
#     response = await client.delete(f"/documents/{doc_id}", headers=auth_header)
#     assert response.status_code == 204
