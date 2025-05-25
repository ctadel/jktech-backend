from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Conversation, Message
from schemas import ConversationCreateRequest, MessageCreate
from uuid import UUID

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

async def get_user_conversations(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Conversation).where(Conversation.user_id == user_id))
    return result.scalars().all()

async def get_conversation_by_id(db: AsyncSession, convo_id: UUID) -> Conversation | None:
    result = await db.execute(select(Conversation).where(Conversation.id == convo_id))
    return result.scalars().first()

async def add_message(db: AsyncSession, convo_id: UUID, data: MessageCreate) -> Message:
    msg = Message(conversation_id=convo_id, role=data.role, content=data.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_messages(db: AsyncSession, convo_id: UUID) -> list[Message]:
    result = await db.execute(select(Message).where(Message.conversation_id == convo_id).order_by(Message.created_at))
    return result.scalars().all()
