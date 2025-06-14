from chain.base_handler import BaseHandler, ChainContext
from providers.Deepseek import DeepSeekChat


class AnswerSynthesizer(BaseHandler):
    """答案整合处理器 - 整合所有信息生成最终答案"""
    
    def __init__(self, api_key:str = None, model: str = "deepseek-reasoner", custom_prompt: str = ""):
        super().__init__()
        self.chat = DeepSeekChat(api_key=api_key, model=model)
        base_prompt = f"""你已经获得了以下信息：
1. 问题分析和解决策略
2. 工具计算结果（如果有）

请根据这些信息为学生提供完整、清晰的解答，要求：
- 输出格式为标准的markdown格式
- 根据学生背景调整解释的深度和方式
- 提供清晰的步骤说明
- 整合工具计算结果到解答中
- 给出学习建议和相关知识点
- 确保答案准确且易于理解
- 请用 $ 包裹latex语句"""
        
        self.answer_synthesizer_prompt = base_prompt
        if custom_prompt and custom_prompt.strip():
            self.answer_synthesizer_prompt += f"\n\n附加要求：\n{custom_prompt}"
    
    def _process(self, context: ChainContext) -> ChainContext:
        """整合所有信息生成最终答案"""
        
        # 构建完整的上下文信息
        context_info = self._build_context_info(context)

        user_message = f"""
原始问题：{context.problem}

{context_info}

学生背景：{context.user_background}

请为学生提供完整的解答和指导。
"""

        try:
            # 调用API生成最终答案
            messages = [
                {"role": "system", "content": self.answer_synthesizer_prompt},
                {"role": "system", "content": user_message}
            ]

            chat_history = context.metadata["chat_history"]

            if chat_history:
                messages.append({"role": "user", "content": chat_history["question"]})
                messages.append({"role": "assistant", "content": chat_history["answer"]})

            print(f"final prompt:\n {self.answer_synthesizer_prompt}")
            print(f"first user message:\n {user_message}")
            # print(f"final messages:\n {messages}")
            
            response = self.chat.call_api(messages, stream=False)
            parsed_response = self.chat._parse_response(response)
            
            context.final_answer = parsed_response.get("content")
            context.metadata["answer_synthesizer"] = "completed"
            
            # 如果有推理内容，也保存
            if parsed_response.get("reasoning_content"):
                context.metadata["reasoning"] = parsed_response["reasoning_content"]
            
        except Exception as e:
            context.final_answer = f"生成最终答案时出现错误：{str(e)}"
            context.metadata["answer_synthesizer"] = "error"
        
        return context
    
    def _build_context_info(self, context: ChainContext) -> str:
        """构建上下文信息字符串"""
        info_parts = []
        
        # 添加策略分析信息
        if context.strategy_plan:
            info_parts.append("=== 问题分析和策略 ===")
            info_parts.append(context.strategy_plan.analysis)
            
            if context.strategy_plan.reasoning:
                info_parts.append("\n推理过程：")
                info_parts.append(context.strategy_plan.reasoning)
        
        # 添加工具执行结果
        if context.tool_results and context.tool_results.executed:
            info_parts.append("\n=== 工具计算结果 ===")
            info_parts.append(f"执行摘要：{context.tool_results.summary}")
            
            for result in context.tool_results.results:
                if result.success:
                    info_parts.append(f"\n{result.tool_name} 结果：")
                    info_parts.append(f"  参数：{result.arguments}")
                    info_parts.append(f"  结果：{result.result}")
                else:
                    info_parts.append(f"\n{result.tool_name} 执行失败：{result.result.get('error', '未知错误')}")
        
        return "\n".join(info_parts)
