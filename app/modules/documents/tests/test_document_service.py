# import pytest
# from unittest.mock import MagicMock
# from sqlalchemy.ext.asyncio import AsyncSession
# from modules.documents import service
# from modules.users.models import User, AccountLevel
# from modules.documents.models import Document

# class DummyUploadFile:
#     def __init__(self, content: bytes, filename: str):
#         self.file = content
#         self.filename = filename

# @pytest.fixture
# def mock_user_basic():
#     return User(id=1, username="basic", account_type=AccountLevel.BASIC.name)

# @pytest.fixture
# def mock_user_premium():
#     return User(id=2, username="premium", account_type=AccountLevel.PREMIUM.name)

# @pytest.fixture
# def dummy_file():
#     return DummyUploadFile(content=b"sample data", filename="file.txt")

# @pytest.mark.asyncio
# async def test_basic_user_upload_limit(mocker, db: AsyncSession, mock_user_basic, dummy_file):
#     # Mock get_user_documents to return 3 docs (limit for BASIC)
#     mocker.patch("modules.documents.crud.get_user_documents", return_value=[1, 2, 3])

#     with pytest.raises(Exception) as e:
#         await service.upload_document(
#             db=db,
#             user=mock_user_basic,
#             file=dummy_file,
#             title="Test File",
#             is_private=False
#         )
#     assert "upload 3 documents" in str(e.value)

# @pytest.mark.asyncio
# async def test_premium_user_reupload(mocker, db: AsyncSession, mock_user_premium, dummy_file):
#     # Mock existing document versions
#     mocker.patch("modules.documents.crud.get_documents_by_key", return_value=[
#         Document(id=1, version=1), Document(id=2, version=2)
#     ])
#     mocker.patch("modules.documents.crud.create_document", return_value=Document(
#         id=3, version=3, title="v3", document_key="abc123", file_path="mock/path"
#     ))
#     mocker.patch.object(service, "storage").upload_file = MagicMock(return_value="mock/path")

#     new_doc = await service.upload_document(
#         db=db,
#         user=mock_user_premium,
#         file=dummy_file,
#         title="v3",
#         is_private=True,
#         document_key="abc123",
#         is_reupload=True
#     )

#     assert new_doc.version == 3
#     assert new_doc.file_path == "mock/path"

# @pytest.mark.asyncio
# async def test_delete_document_authorized(mocker, db: AsyncSession, mock_user_basic):
#     # Mock a document owned by the user
#     doc = Document(id=1, user_id=mock_user_basic.id, file_path="mock/path")
#     mocker.patch("modules.documents.crud.get_document_by_id", return_value=doc)
#     mocker.patch("modules.documents.crud.delete_document", return_value=None)
#     mocker.patch.object(service, "storage").delete_file = MagicMock()

#     await service.delete_document(db=db, document_id=1, current_user=mock_user_basic)
#     service.storage.delete_file.assert_called_once_with("mock/path")
