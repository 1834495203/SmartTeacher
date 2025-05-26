from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from entity.ChainContextEntity import ToolResults, StrategyPlan


class ChainContext:
    """责任链上下文，用于在处理器之间传递数据"""
    def __init__(self, problem: str, user_background: str):
        self.problem = problem
        self.user_background = user_background
        # self.strategy_plan: Optional[Dict[str, Any]] = None
        self.strategy_plan: Optional[StrategyPlan] = None
        # self.tool_results: Optional[Dict[str, Any]] = None
        self.tool_results: Optional[ToolResults] = None
        self.final_answer: Optional[str] = None
        self.metadata: Dict[str, Any] = {}


class BaseHandler(ABC):
    """责任链处理器基类"""
    
    def __init__(self):
        self._next_handler: Optional[BaseHandler] = None
    
    def set_next(self, handler: 'BaseHandler') -> 'BaseHandler':
        """设置下一个处理器"""
        self._next_handler = handler
        return handler
    
    def handle(self, context: ChainContext) -> ChainContext:
        """处理请求"""
        # 执行当前处理器的逻辑
        context = self._process(context)
        
        # 如果有下一个处理器，继续传递
        if self._next_handler:
            return self._next_handler.handle(context)
        
        return context
    
    @abstractmethod
    def _process(self, context: ChainContext) -> ChainContext:
        """具体的处理逻辑，由子类实现"""
        pass
