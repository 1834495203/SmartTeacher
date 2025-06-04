from typing import Dict, Any, List

from chain.base_handler import ChainContext
from chain.strategy_planner import StrategyPlanner
from chain.tool_executor import ToolExecutor
from chain.answer_synthesizer import AnswerSynthesizer


class MathChain:
    """数学问题处理责任链"""
    
    def __init__(self, api_key):
        # 创建处理器
        self.strategy_planner = StrategyPlanner(api_key)
        self.tool_executor = ToolExecutor()
        self.api_key = api_key
        # AnswerSynthesizer 将在 process 方法中根据传入的 prompt 初始化
        self.strategy_planner.set_next(self.tool_executor)
    
    def process(self, problem: str, user_background: str, custom_prompt: str = "",
                conv_history: List[Dict[str, Any]] = None) -> ChainContext:
        """处理数学问题"""
        # 创建上下文
        context = ChainContext(problem, user_background)
        
        # 根据 custom_prompt 初始化 AnswerSynthesizer
        answer_synthesizer = AnswerSynthesizer(api_key=self.api_key, custom_prompt=custom_prompt)
        
        # 构建完整的责任链
        self.tool_executor.set_next(answer_synthesizer)

        context.metadata["chat_history"] = conv_history
        
        # 开始处理链
        result_context = self.strategy_planner.handle(context)
        
        return result_context
    
    def get_processing_steps(self, context: ChainContext) -> dict:
        """获取处理步骤的详细信息"""
        return {
            "strategy_planning": {
                "status": context.metadata.get("strategy_planner", "not_started"),
                "content": context.strategy_plan
            },
            "tool_execution": {
                "status": context.metadata.get("tool_executor", "not_started"),
                "content": context.tool_results
            },
            "answer_synthesis": {
                "status": context.metadata.get("answer_synthesizer", "not_started"),
                "content": context.final_answer
            }
        }
