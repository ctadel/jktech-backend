from fastapi import Depends, HTTPException
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.dependencies import get_current_user
from app.common.exceptions import InvalidConversationException
from app.modules.conversations import crud
from app.modules.conversations.models import Role
from app.modules.conversations.schemas import ConversationCreateRequest, MessageCreate
from app.modules.users.models import User
from app.modules.documents.service import IngestionService
from app.modules.documents.crud import add_views

class ConversationService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        self.db = db
        self.user = current_user

    async def create_conversation(self, data: ConversationCreateRequest):
        await add_views(self.db, data.document_id)
        return await crud.create_conversation(self.db, self.user.id, data)

    async def list_conversations(self):
        return await crud.get_user_conversations(self.db, self.user.id)

    async def get_conversation(self, convo_id):
        convo = await crud.get_conversation_by_id(self.db, convo_id)
        if convo and convo.user_id == self.user.id:
            return convo
        raise InvalidConversationException()

    async def post_message(self, convo_id, data: MessageCreate):
        convo = await self.get_conversation(convo_id)
        if not convo:
            raise InvalidConversationException()
        await crud.add_message(self.db, convo_id, data)

        ai_reply = await IngestionService.query_document(
                document_id=convo.document_id,
                query=data.content
            )

        ai_response = MessageCreate(
                role=Role.LLM,
                content=ai_reply
            )

        db_record = await crud.add_message(self.db, convo_id, ai_response)
        return db_record

    async def get_messages(self, convo_id):
        return await crud.get_messages(self.db, convo_id)

    async def archive_conversation(self, convo_id: UUID):
        convo = await crud.archive_conversation(self.db, convo_id, self.user.id)
        if not convo:
            raise InvalidConversationException()
        return convo

    async def delete_conversation(self, convo_id: UUID):
        convo = await crud.delete_conversation(self.db, convo_id, self.user.id)
        if not convo:
            raise InvalidConversationException()
        return convo
