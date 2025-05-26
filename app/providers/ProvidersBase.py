from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import uuid4

from entity.Conversation import ChatMessageType
from entity.Models import Chat, ChatContent


class AbstractChat(ABC):
    def __init__(self, model: str):
        """
        初始化抽象聊天类
        """
        self.model = model
        self.chat = Chat(messages=[])

        self.client: Any = None
        self.conversation_id = str(uuid4())  # 为每个对话分配唯一ID

    def prepare_messages(self, user_input: str, system_prompt: Optional[str] = None) -> List[Any]:
        """
        准备消息：将用户输入添加到聊天记录并转换为 API 格式
        """
        if system_prompt and not any(msg.role == "system" for msg in self.chat.messages):
            self.chat.messages.append(ChatContent(
                role="system",
                content=system_prompt,
                reasoning_content=None,
                chat_type=ChatMessageType.SYSTEM_PROMPT
            ))

        if user_input is not None:
            user_message = ChatContent(
                role="user",
                content=user_input,
                reasoning_content=None,
                chat_type=ChatMessageType.NORMAL_MESSAGE_USER
            )
            self.chat.messages.append(user_message)

        messages = []
        for msg in self.chat.messages:
            message_dict = {"role": msg.role, "content": msg.content}
            if msg.name:
                message_dict["name"] = msg.name
            messages.append(message_dict)
        return messages

    @abstractmethod
    def _create_client(self, api_key: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def call_api(self, messages: List[Dict[str, str]], stream: bool, **kwargs) -> Any:
        raise NotImplementedError('请创建调用api方式！')

    @abstractmethod
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        解析API响应，提取内容和token使用数据
        """
        # 假设 response 是 OpenAI API 的返回对象，包含 usage 字段
        content = response.choices[0].message.content
        response_data = {
            "content": content,
            "reasoning_content": None,
            "message": None,
            "finish_reason": response.choices[0].finish_reason
        }
        return response_data

    @abstractmethod
    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        pass

    def call_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict] = None, 
                       tool_choice: str = "auto") -> Dict[str, Any]:
        """
        调用带工具的API
        """
        kwargs = {}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
            
        response = self.call_api(messages, stream=False, **kwargs)
        return self._parse_response(response)

    def chatting(self, user_input: str | List[str] = None,
                 stream: bool = False, system_prompt: Optional[str] = None) -> ChatContent:
        """
        与模型进行聊天，处理用户输入并返回模型响应
        """
        if self.client is None:
            raise ValueError("客户端未初始化")

        try:
            api_messages = self.prepare_messages(user_input, system_prompt)

            response = self.call_api(api_messages, stream)
            if stream:
                raise NotImplementedError("Streaming should be handled by yourself")
            else:
                response_data = self._parse_response(response)
                assistant_message = ChatContent(
                    role="assistant",
                    content=response_data.get("content"),
                    reasoning_content=response_data.get("reasoning_content"),
                    message=response_data.get("message"),
                    finish_reason=response_data.get("finish_reason"),
                    chat_type=ChatMessageType.NORMAL_MESSAGE_ASSISTANT
                )
                self.chat.messages.append(assistant_message)

            return assistant_message

        except Exception as e:
            raise ValueError(f"API 调用失败: {str(e)}")

    def print_current_response(self) -> None:
        if not self.chat.messages or self.chat.messages[-1].role != "assistant":
            print("当前没有模型响应可打印")
            return
        print(self.chat.messages[-1])
        print("-" * 50)

    def print_chat_history(self) -> None:
        if not self.chat.messages:
            print("聊天记录为空")
            return
        print("聊天记录:")
        for msg in self.chat.messages:
            print(msg)
            print("-" * 50)

    def add_system_message(self, system_content: str,
                           chat_type: ChatMessageType = ChatMessageType.SYSTEM_PROMPT) -> None:
        system_message = ChatContent(
            role="system",
            content=system_content,
            reasoning_content=None,
            tool_calls=None,
            chat_type=chat_type
        )
        self.chat.messages.append(system_message)

    def clear_chat_history(self) -> None:
        self.chat.messages = []
        self.conversation_id = str(uuid4())  # 重置对话ID

    def whoami(self) -> str:
        return self.model