import logging

from functools import lru_cache
from pydantic import BaseModel
from fastapi import status, APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse
from revChatGPT.V1 import Chatbot

from .models.models import ChatgptConversation
from .tools import DBSession, Tools, ratelimit

router = APIRouter()
_logger = logging.getLogger(__name__)


class ChatgptMessage(BaseModel):
    token: str
    text: str
    chat_id: str = "Default"


@ratelimit(10, 10)
@router.post("/chatgpt", response_class=PlainTextResponse, tags=["chatgpt"])
def get_chatgpt_message(chatgpt_message: ChatgptMessage) -> str:
    if chatgpt_message.token != Tools.get_api_token():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "token is not correct"}
        )
    chatbot = get_chatbot(chatgpt_message.chat_id)
    try:
        res = ""
        for data in chatbot.ask(chatgpt_message.text):
            res = data["message"]
        return res
    except Exception as e:
        get_chatbot.cache_clear()


@lru_cache()
def get_chatbot(chat_id) -> Chatbot:
    with DBSession() as session:
        conversation = session.query(
            ChatgptConversation
        ).filter(
            ChatgptConversation.chat_id == chat_id
        ).one_or_none()
        if conversation:
            _logger.info(
                f"为 {chat_id} 获取 chatbot, conversation_id: {conversation.conversation_id}"
            )
            return Chatbot(
                config={
                    "access_token": Tools.get_chatgpt_access_token(),
                },
                conversation_id=conversation.conversation_id
            )

        else:
            chatbot = Chatbot(
                config={
                    "access_token": Tools.get_chatgpt_access_token(),
                }
            )
            for data in chatbot.ask("Hi"):
                _ = data["message"]
            conversation_id = chatbot.conversation_id
            session = DBSession()
            session.add(
                ChatgptConversation(
                    chat_id=chat_id,
                    conversation_id=conversation_id
                )
            )
            session.commit()
            _logger.info(
                f"为 {chat_id} 新建 chatbot, conversation_id: {conversation_id}"
            )
            return chatbot
