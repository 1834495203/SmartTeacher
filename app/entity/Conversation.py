from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ChatMessageType(Enum):
    # 系统级别的prompt
    SYSTEM_PROMPT = 0
    # 角色的信息
    CHARACTER_TYPE = 1
    # 用户的信息
    USER_TYPE = 2
    # 一般的用户发的信息
    NORMAL_MESSAGE_USER = 3
    # 一般的llm回复的消息
    NORMAL_MESSAGE_ASSISTANT = 4
    # 旁白
    ASIDE_MESSAGE = 5
    # 联网搜索的信息
    ONLINE_MESSAGE = 6
    # 流式传输的数据
    NORMAL_MESSAGE_ASSISTANT_PART = 7
    # 排除的数据，报错
    EXCLUDE_MESSAGE_EXCEPTION = 8

class Conversation(BaseModel):
    root_conversation_id: int                        # 表示上一个父节点的会话id -1表示根节点
    conversation_id: int                             # 会话唯一id
    character_id: int = None                         # 对话角色id
    create_time: Optional[float] = None              # 创建时间戳


# 定义 API 聊天模型，存入数据库
class ChatContentMain(BaseModel):
    cid: Optional[str] = None                        # 对话唯一id
    conversation_id: Optional[int] = None            # 会话唯一id
    role: str                                        # 角色
    content: str                                     # 消息
    chat_type: ChatMessageType                       # 对话类型
    reasoning_content: Optional[str] = None          # 推理内容
    create_time: Optional[float] = None              # 时间
