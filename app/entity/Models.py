# 定义聊天内容类
import uuid
from typing import Optional, List, Any

from entity.Conversation import ChatContentMain, ChatMessageType


# 使用于llm的对话信息
class ChatContent(ChatContentMain):
    # 新增字段：OpenAI 接口返回的字段
    name: Optional[str] = None              # 消息名称
    finish_reason: Optional[str] = None     # 完成原因
    message: Optional[Any] = None           # 消息对象
    
    class Config:
        arbitrary_types_allowed = True      # 允许 Any 类型

# 原始的 Chat 类
class Chat:
    def __init__(self,
                 messages: Optional[List[ChatContent]] = None,):
        self.messages: List[ChatContent] = messages or []

    def set_message(self, messages: ChatContent):
        self.messages.append(messages)
        return self

    def set_messages(self, messages: List[ChatContent]):
        for msg_ in messages:
            self.set_message(msg_)
        return self

    def get_messages_by_type(self, message_type: ChatMessageType) -> List[ChatContent]:
        """
        根据指定的 ChatMessageType 返回对应类型的消息列表

        Args:
            message_type: 要筛选的消息类型

        Returns:
            List[ChatContent]: 指定类型的消息列表
        """
        return [message for message in self.messages if message.chat_type == message_type]

    def get_messages_by_types(self, message_types: List[ChatMessageType]) -> List[ChatContent]:
        """
        根据指定的多个 ChatMessageType 返回对应类型的消息列表

        Args:
            message_types: 要筛选的消息类型列表

        Returns:
            List[ChatContent]: 符合指定类型之一的消息列表
        """
        return [message for message in self.messages if message.chat_type in message_types]

    def has_message_type(self, message_type: ChatMessageType) -> bool:
        """
        检查是否存在指定类型的消息

        Args:
            message_type: 要检查的消息类型

        Returns:
            bool: 如果存在指定类型的消息则返回 True，否则返回 False
        """
        return any(message.chat_type == message_type for message in self.messages)

    def count_by_type(self, message_type: ChatMessageType) -> int:
        """
        统计指定类型消息的数量

        Args:
            message_type: 要统计的消息类型

        Returns:
            int: 指定类型的消息数量
        """
        return sum(1 for message in self.messages if message.chat_type == message_type)
