from agents.function_caller import FunctionCaller
from chain.base_handler import BaseHandler, ChainContext
from entity.ChainContextEntity import StrategyPlan
from providers.Deepseek import DeepSeekChat


class StrategyPlanner(BaseHandler):
    """策略规划处理器 - 分析问题并制定解决策略"""
    
    def __init__(self, model: str = "deepseek-chat"):
        super().__init__()
        self.chat = DeepSeekChat(model)
        self.function_caller = FunctionCaller()
    
    def _process(self, context: ChainContext) -> ChainContext:
        """分析问题并制定解决策略"""
        try:
            
            # 调用API获取策略规划
            response = self.function_caller.analyze(context.problem, context.user_background)

            print("strategy planner:\n", response)
            
            # 解析工具调用
            if response.need_function:
                # 保存策略规划结果
                context.strategy_plan = StrategyPlan(
                    reasoning=response.reasoning,
                    tool_calls=response.function_results,
                    needs_tools=True
                )
            
            context.metadata["strategy_planner"] = "completed"
            
        except Exception as e:
            context.strategy_plan = StrategyPlan(
                analysis=f"策略规划过程中出现错误：{str(e)}",
                tool_calls=[],
                needs_tools=False
            )
            context.metadata["strategy_planner"] = "error"
        
        return context
