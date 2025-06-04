from chain.base_handler import BaseHandler, ChainContext
from entity.ChainContextEntity import ToolResults, ToolExecutionResult
from tools.math_tools import execute_tool


class ToolExecutor(BaseHandler):
    """工具执行处理器 - 执行必要的计算和验证工具"""
    
    def _process(self, context: ChainContext) -> ChainContext:
        """执行工具调用"""
        
        if not context.strategy_plan or not context.strategy_plan.needs_tools:
            # 如果不需要工具，直接跳过
            context.tool_results = ToolResults(
                executed=False,
                results=[],
                summary="本问题不需要使用计算工具"
            )
            context.metadata["tool_executor"] = "skipped"
            return context
        
        try:
            function_results = context.strategy_plan.tool_calls
            executed_results = []
            
            for function_result in function_results:
                tool_name = function_result.function_name
                arguments = function_result.parameters
                
                # 执行工具
                result = execute_tool(tool_name, arguments)

                print(f"tool executor: \n{result}")

                executed_results.append(ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    result=result,
                    success=result.get("success", False),
                    img_path=result.get("file_path", None)
                ))

                context.metadata["img_path"] = result.get("file_path", None)
            
            # 生成工具执行摘要
            successful_tools = [r for r in executed_results if r.success]
            failed_tools = [r for r in executed_results if not r.success]
            
            summary_parts = []
            if successful_tools:
                summary_parts.append(f"成功执行了 {len(successful_tools)} 个工具")
            if failed_tools:
                summary_parts.append(f"有 {len(failed_tools)} 个工具执行失败")

            context.tool_results = ToolResults(
                executed=True,
                results=executed_results,
                summary="；".join(summary_parts) if summary_parts else "工具执行完成",
                successful_count=len(successful_tools),
                failed_count=len(failed_tools)
            )
            
            context.metadata["tool_executor"] = "completed"
            
        except Exception as e:
            context.tool_results = ToolResults(
                executed=False,
                results=[],
                summary=f"工具执行过程中出现错误：{str(e)}",
                error=str(e)
            )
            context.metadata["tool_executor"] = "error"

        print(f"tool executor: \n {context.tool_results}")

        return context
