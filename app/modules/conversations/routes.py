from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.modules.conversations.service import ConversationService
from app.common.endpoints import Endpoints as EP
from app.modules.conversations.schemas import ConversationCreateRequest, MessageCreate, ConversationDetail, \
        MessageRead, ConversationResponse

class ConversationRoutes:
    def __init__(self, prefix: str = "/conversations"):
        self.router = APIRouter(
                prefix=prefix, tags=["Conversations"]
                )

        self.router.get(    EP.Conversations.LIST_USER_CONVERSATIONS  )(self.list_user_conversations)
        self.router.post(   EP.Conversations.START_NEW_CONVERSATION   )(self.start_new_conversation)
        self.router.get(    EP.Conversations.GET_CONVERSATION         )(self.get_conversation)
        self.router.post(   EP.Conversations.ADD_MESSAGE              )(self.add_message)
        self.router.delete( EP.Conversations.DELETE_CONVERSATION      )(self.delete_conversation)
        self.router.post(   EP.Conversations.ARCHIVE_CONVERSATION     )(self.archive_conversation)


    async def list_user_conversations(
            self, service = Depends(ConversationService)
            ) -> List[ConversationResponse]:
        conversations = await service.list_conversations()
        return [ConversationResponse.model_validate(convo) for convo in conversations]

    async def start_new_conversation(
            self, data: ConversationCreateRequest,
            service = Depends(ConversationService)
            ) -> ConversationResponse:
        convo = await service.create_conversation(data)
        return ConversationResponse.model_validate(convo)

    async def get_conversation(
            self, convo_id: str,
            service = Depends(ConversationService)
            ) -> ConversationDetail:
        convo = await service.get_conversation(convo_id)
        if not convo:
            raise HTTPException(status_code=404, detail="Not found")
        messages = await service.get_messages(convo_id)
        return [ConversationDetail.model_validate(message) for message in messages]

    async def add_message(
            self, convo_id: str, data: MessageCreate,
            service = Depends(ConversationService)
            ) -> MessageRead:
        message = await service.post_message(convo_id, data)
        return MessageRead.model_validate(message)

    async def get_conversation(
            self, convo_id: str,
            service = Depends(ConversationService)
            ) -> list[MessageRead]:
        return await service.get_messages(convo_id)

    async def delete_conversation(
            self, convo_id: str,
            service = Depends(ConversationService)):
        return await service.delete_conversation(convo_id)

    async def archive_conversation(
            self, convo_id: str,
            service = Depends(ConversationService)):
        return await service.archive_conversation(convo_id)
