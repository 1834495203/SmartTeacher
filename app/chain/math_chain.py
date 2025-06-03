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
        # AnswerSynthesizer 将在 process 方法中根据传入的 prompt 初始化
        # self.answer_synthesizer = AnswerSynthesizer(api_key) 
        
        # 构建责任链的一部分，AnswerSynthesizer 的链接将在 process 中动态完成
        self.strategy_planner.set_next(self.tool_executor)
    
    def process(self, problem: str, user_background: str, custom_prompt: str = "") -> ChainContext:
        """处理数学问题"""
        # 创建上下文
        context = ChainContext(problem, user_background)
        
        # 根据 custom_prompt 初始化 AnswerSynthesizer
        # 注意：这里假设 api_key 是 MathChain 的一个属性，或者可以从其他地方获取
        # 如果 api_key 不是 self.api_key, 需要调整
        answer_synthesizer = AnswerSynthesizer(api_key=self.strategy_planner.chat.api_key, custom_prompt=custom_prompt)
        
        # 构建完整的责任链
        current_handler = self.strategy_planner
        while current_handler.next_handler:
            current_handler = current_handler.next_handler
        current_handler.set_next(answer_synthesizer)
        
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
