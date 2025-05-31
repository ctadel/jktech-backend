from operator import and_
from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.modules.conversations.models import Conversation, Message
from app.modules.conversations.schemas import ConversationCreateRequest, MessageCreate

async def create_conversation(
        db: AsyncSession,
        user_id: UUID,
        data: ConversationCreateRequest
        ) -> Conversation:
    convo = Conversation(user_id=user_id, document_id=data.document_id, title=data.title)
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo

async def get_user_conversations(db: AsyncSession, user_id):
    result = await db.execute(select(Conversation).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.is_archived == False
             )
        ))
    return result.scalars().all()

async def get_conversation_by_id(db: AsyncSession, convo_id) -> Conversation | None:
    result = await db.execute(select(Conversation).where(Conversation.id == convo_id))
    return result.scalars().first()

async def add_message(db: AsyncSession, convo_id, data: MessageCreate) -> Message:
    msg = Message(conversation_id=convo_id, role=data.role, content=data.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_messages(db: AsyncSession, convo_id) -> list[Message]:
    result = await db.execute(select(Message).where(Message.conversation_id == convo_id).order_by(Message.created_at))
    return result.scalars().all()


async def archive_conversation(db: AsyncSession, convo_id, user_id: int):
    result = await db.execute(
        update(Conversation)
        .where(Conversation.id == convo_id, Conversation.user_id == user_id)
        .values(is_archived=True)
        .returning(Conversation)
    )
    await db.commit()
    return result.scalar_one_or_none()

async def delete_conversation(db: AsyncSession, convo_id, user_id: int):
    result = await db.execute(
        delete(Conversation)
        .where(Conversation.id == convo_id, Conversation.user_id == user_id)
        .returning(Conversation)
    )
    await db.commit()
    return result.scalar_one_or_none()
