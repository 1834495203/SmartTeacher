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
        self.answer_synthesizer = AnswerSynthesizer(api_key)
        
        # 构建责任链
        self.strategy_planner.set_next(self.tool_executor).set_next(self.answer_synthesizer)
    
    def process(self, problem: str, user_background: str) -> ChainContext:
        """处理数学问题"""
        # 创建上下文
        context = ChainContext(problem, user_background)
        
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
