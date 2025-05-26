import sympy as sp
from typing import Dict, Any, List


def calculate_expression(expression: str) -> Dict[str, Any]:
    """计算数学表达式"""
    try:
        # 使用sympy计算表达式
        result = sp.sympify(expression)
        evaluated = float(result.evalf()) if result.is_number else str(result)
        return {
            "success": True,
            "result": evaluated,
            "expression": expression,
            "description": f"计算表达式 {expression} = {evaluated}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "expression": expression,
            "description": f"计算表达式 {expression} 时出错: {str(e)}"
        }


def solve_equation(equation: str, variable: str = "x") -> Dict[str, Any]:
    """解方程"""
    try:
        # 解析方程
        eq = sp.Eq(*[sp.sympify(side) for side in equation.split("=")])
        var = sp.Symbol(variable)
        solutions = sp.solve(eq, var)
        
        solutions_str = [str(sol) for sol in solutions]
        return {
            "success": True,
            "solutions": solutions_str,
            "equation": equation,
            "variable": variable,
            "description": f"方程 {equation} 的解为: {', '.join(solutions_str)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "equation": equation,
            "description": f"解方程 {equation} 时出错: {str(e)}"
        }


def plot_function(function: str, x_range: List[float] = [-10, 10]) -> Dict[str, Any]:
    """分析函数图像特征"""
    try:
        x = sp.Symbol('x')
        func = sp.sympify(function)
        
        # 计算导数
        derivative = sp.diff(func, x)
        second_derivative = sp.diff(derivative, x)
        
        # 找到极值点
        critical_points = sp.solve(derivative, x)
        critical_points_real = [cp for cp in critical_points if cp.is_real]
        
        # 找到拐点
        inflection_points = sp.solve(second_derivative, x)
        inflection_points_real = [ip for ip in inflection_points if ip.is_real]
        
        return {
            "success": True,
            "function": function,
            "derivative": str(derivative),
            "critical_points": [str(cp) for cp in critical_points_real],
            "inflection_points": [str(ip) for ip in inflection_points_real],
            "range": x_range,
            "description": f"函数 {function} 的导数为 {derivative}，极值点: {critical_points_real}，拐点: {inflection_points_real}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "function": function,
            "description": f"分析函数 {function} 时出错: {str(e)}"
        }


# 函数描述，用于LLM理解
FUNCTION_DESCRIPTIONS = """
可用的数学工具函数：

1. calculate_expression(expression: str)
   - 功能：计算数学表达式的值
   - 参数：expression - 数学表达式字符串，如 "2+3*4" 或 "sqrt(16)"
   - 适用场景：需要精确计算复杂数值表达式时

2. solve_equation(equation: str, variable: str = "x")
   - 功能：解数学方程
   - 参数：equation - 方程字符串，如 "x**2 - 4 = 0"；variable - 求解变量，默认为"x"
   - 适用场景：需要求解代数方程时

3. plot_function(function: str, x_range: List[float] = [-10, 10])
   - 功能：分析函数的数学特征
   - 参数：function - 函数表达式，如 "x**2 + 2*x + 1"；x_range - 分析范围
   - 适用场景：需要分析函数性质、求导数、找极值点时

请根据问题类型判断是否需要调用这些函数。
"""


def execute_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """执行指定的数学函数"""
    if function_name == "calculate_expression":
        return calculate_expression(kwargs.get("expression", ""))
    elif function_name == "solve_equation":
        return solve_equation(kwargs.get("equation", ""), kwargs.get("variable", "x"))
    elif function_name == "plot_function":
        return plot_function(kwargs.get("function", ""), kwargs.get("x_range", [-10, 10]))
    else:
        return {
            "success": False,
            "error": f"未知函数: {function_name}",
            "description": f"函数 {function_name} 不存在"
        }


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """执行工具函数"""
    if tool_name == "calculate_expression":
        return calculate_expression(arguments["expression"])
    elif tool_name == "solve_equation":
        return solve_equation(arguments["equation"], arguments.get("variable", "x"))
    elif tool_name == "plot_function":
        return plot_function(arguments["function"], arguments.get("x_range", [-10, 10]))
    else:
        return {"success": False, "error": f"未知工具: {tool_name}"}


# Function calling工具定义
MATH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_expression",
            "description": "计算数学表达式的值",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '2+3*4' 或 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "solve_equation",
            "description": "解数学方程",
            "parameters": {
                "type": "object",
                "properties": {
                    "equation": {
                        "type": "string",
                        "description": "要解的方程，如 'x**2 - 4 = 0'"
                    },
                    "variable": {
                        "type": "string",
                        "description": "要求解的变量，默认为x"
                    }
                },
                "required": ["equation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_function",
            "description": "分析函数图像特征",
            "parameters": {
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string",
                        "description": "要分析的函数，如 'x^2 + 2*x + 1'"
                    },
                    "x_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "x的取值范围，默认为[-10, 10]"
                    }
                },
                "required": ["function"]
            }
        }
    }
]
