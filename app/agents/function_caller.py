import json
import re

from entity.ChainContextEntity import FunctionCall, FunctionResponse
from providers.Deepseek import DeepSeekChat
from tools.math_tools import MATH_TOOLS


class FunctionCaller:
    def __init__(self, api_key: str = None):
        self.chat = DeepSeekChat(api_key=api_key, model="deepseek-chat")
        self.function_caller_prompt = f"""你是一个数学问题分析专家。
        
Function calling工具定义:
{MATH_TOOLS}

---
你的任务是：
1. analysis 字段为分析用户提出的问题，制定回答的策略，涉及的数学知识等。

1. 请分析用户的数学问题，判断是否需要调用函数来辅助解决。

2. 所有涉及数学公式的参数值需要符合python库sympy的语法。

3. 如果需要调用函数，请按以下JSON格式回复：
{{
    "need_function": true,
    "function_calls": [
        {{
            "function_name": "函数名",
            "parameters": {{
                "参数名": "参数值"
            }},
            "reason": "调用原因"
        }}
    ],
    "analysis": "分析用户提出的问题，制定回答的策略，涉及的数学知识等"
}}

如果不需要调用函数，请回复：
{{
    "need_function": false,
    "analysis": "分析用户提出的问题，制定回答的策略，涉及的数学知识等"
}}

注意：
1. 只有在需要精确计算、解方程或分析函数时才调用函数
2. 简单的概念解释不需要调用函数
3. 确保参数格式正确 \n"""
        
    def analyze(self, problem: str, user_background: str) -> FunctionResponse:
        """分析问题并判断是否需要调用函数"""

        try:
            response = self.chat.chatting(
                user_input=f"请分析这个数学问题：{problem}",
                system_prompt=self.function_caller_prompt + f"用户的教育背景为{user_background}"
            )
            
            # 解析响应
            content = response.content
            
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())

                    if result.get("need_function", False):
                        function_results = []
                        for func_call in result.get("function_calls", []):
                            function_results.append(FunctionCall(
                                function_name=func_call["function_name"],
                                parameters=func_call["parameters"],
                                reason=func_call.get("reason", "")
                            ))

                        return FunctionResponse(
                            need_function=True,
                            analysis=result.get("analysis", ""),
                            function_results=function_results,
                            reasoning=getattr(response, "reasoning_content", None)
                        )
                    else:
                        return FunctionResponse(
                            need_function=False,
                            analysis=result.get("analysis", ""),
                            function_results=[],
                            reasoning=getattr(response, "reasoning_content", None)
                        )
                        
                except json.JSONDecodeError:
                    # JSON解析失败，返回原始分析
                    return FunctionResponse(
                            need_function=False,
                            analysis=content,
                            function_results=[],
                            reasoning=getattr(response, "reasoning_content", None)
                        )
            else:
                return FunctionResponse(
                            need_function=False,
                            analysis=content,
                            function_results=[],
                            reasoning=getattr(response, "reasoning_content", None)
                        )
                
        except Exception as e:
            print(f"分析过程中出现错误：{str(e)}")
            return FunctionResponse(
                            need_function=False,
                            analysis=f"分析过程中出现错误：{str(e)}",
                            function_results=[],
                            error=str(e)
                        )
    
    def clear_history(self):
        """清除对话历史"""
        self.chat.clear_chat_history()
