from chain.base_handler import BaseHandler, ChainContext
from providers.Deepseek import DeepSeekChat


class AnswerSynthesizer(BaseHandler):
    """答案整合处理器 - 整合所有信息生成最终答案"""
    
    def __init__(self, api_key:str = None, model: str = "deepseek-reasoner"):
        super().__init__()
        self.chat = DeepSeekChat(model, api_key)
    
    def _process(self, context: ChainContext) -> ChainContext:
        """整合所有信息生成最终答案"""
        
        # 构建完整的上下文信息
        context_info = self._build_context_info(context)
        
        system_prompt = f"""你是一个专业的数学家教，需要根据学生的教育背景提供个性化的数学指导。

学生背景：{context.user_background}

你已经获得了以下信息：
1. 问题分析和解决策略
2. 工具计算结果（如果有）

请根据这些信息为学生提供完整、清晰的解答，要求：
- 输出格式为标准的markdown格式
- 根据学生背景调整解释的深度和方式
- 提供清晰的步骤说明
- 整合工具计算结果到解答中
- 给出学习建议和相关知识点
- 确保答案准确且易于理解"""

        user_message = f"""
原始问题：{context.problem}

{context_info}

请为学生提供完整的解答和指导。
"""

        try:
            # 调用API生成最终答案
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            print(f"final prompt:\n {system_prompt}")
            print(f"first user message:\n {user_message}")
            
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
