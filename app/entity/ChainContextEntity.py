from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ToolExecutionResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    success: bool
    img_path: Optional[str] = None

class ToolResults(BaseModel):
    executed: bool
    results: List[ToolExecutionResult]
    summary: str
    successful_count: Optional[int] = None
    failed_count: Optional[int] = None
    error: Optional[str] = ""

class FunctionCall(BaseModel):
    function_name: str
    parameters: Dict[str, Any]
    reason: str = ""

class FunctionResponse(BaseModel):
    need_function: bool
    analysis: str
    function_results: List[FunctionCall]
    reasoning: Optional[str] = ""
    error: Optional[str] = ""

class StrategyPlan(BaseModel):
    reasoning: Optional[str] = ""
    tool_calls: List[FunctionCall]
    needs_tools: bool
    analysis: Optional[str] = ""