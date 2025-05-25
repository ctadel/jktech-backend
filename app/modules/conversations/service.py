from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.dependencies import get_current_user
from app.modules.conversations import crud
from app.modules.conversations.schemas import ConversationCreateRequest, MessageCreate
from models import User

class ConversationService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        self.db = db
        self.user = current_user

    async def create_conversation(self, data: ConversationCreateRequest):
        return await crud.create_conversation(self.db, self.user.id, data)

    async def list_conversations(self):
        return await crud.get_user_conversations(self.db, self.user.id)

    async def get_conversation(self, convo_id):
        convo = await crud.get_conversation_by_id(self.db, convo_id)
        if convo and convo.user_id == self.user.id:
            return convo
        return None

    async def post_message(self, convo_id, data: MessageCreate):
        convo = await self.get_conversation(convo_id)
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return await crud.add_message(self.db, convo_id, data)

    async def get_messages(self, convo_id):
        return await crud.get_messages(self.db, convo_id)
