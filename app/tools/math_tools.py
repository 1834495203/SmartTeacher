import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, Any, List, Union, Tuple
from datetime import datetime


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


def draw_plot(plot_type: str,
              functions: Union[str, List[str]] = None,
              x_range: List[float] = [-10, 10],
              y_range: List[float] = None,
              points: List[Tuple[float, float]] = None,
              shapes: List[Dict[str, Any]] = None,
              title: str = None,
              xlabel: str = "x",
              ylabel: str = "y",
              grid: bool = True,
              save_path: str = None,
              figure_size: Tuple[int, int] = (10, 8),
              dpi: int = 300) -> Dict[str, Any]:
    """
    绘制函数或几何图形并保存至文件

    参数：
    - plot_type: 绘图类型 ("function", "geometry", "mixed")
    - functions: 函数表达式字符串或字符串列表
    - x_range: x轴范围 [xmin, xmax]
    - y_range: y轴范围 [ymin, ymax]，None时自动设置
    - points: 点坐标列表 [(x1, y1), (x2, y2), ...]
    - shapes: 几何图形列表，每个元素为字典描述图形参数
    - title: 图表标题
    - xlabel, ylabel: 坐标轴标签
    - grid: 是否显示网格
    - save_path: 保存路径，None时自动生成
    - figure_size: 图像尺寸 (width, height)
    - dpi: 图像分辨率
    """
    try:
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 创建图形
        fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)

        # 生成x轴数据点
        x_vals = np.linspace(x_range[0], x_range[1], 1000)

        # 绘制函数
        if plot_type in ["function", "mixed"] and functions:
            if isinstance(functions, str):
                functions = [functions]

            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

            for i, func_str in enumerate(functions):
                try:
                    # 将函数字符串转换为numpy可计算的形式
                    x_sym = sp.Symbol('x')
                    func_sym = sp.sympify(func_str)
                    func_lambda = sp.lambdify(x_sym, func_sym, 'numpy')

                    # 计算y值，处理可能的数学错误
                    y_vals = []
                    for x_val in x_vals:
                        try:
                            y_val = func_lambda(x_val)
                            if np.isfinite(y_val):
                                y_vals.append(y_val)
                            else:
                                y_vals.append(np.nan)
                        except:
                            y_vals.append(np.nan)

                    y_vals = np.array(y_vals)

                    # 绘制函数曲线
                    color = colors[i % len(colors)]
                    ax.plot(x_vals, y_vals, label=f'y = {func_str}', color=color, linewidth=2)

                except Exception as func_error:
                    print(f"警告：无法绘制函数 {func_str}: {func_error}")

        # 绘制点
        if points:
            x_points = [p[0] for p in points]
            y_points = [p[1] for p in points]
            ax.scatter(x_points, y_points, color='red', s=50, zorder=5, label='Points')

            # 标注点坐标
            for i, (x, y) in enumerate(points):
                ax.annotate(f'({x}, {y})', (x, y), xytext=(5, 5),
                            textcoords='offset points', fontsize=9)

        # 绘制几何图形
        if plot_type in ["geometry", "mixed"] and shapes:
            for shape in shapes:
                shape_type = shape.get('type', '').lower()

                if shape_type == 'circle':
                    center = shape.get('center', (0, 0))
                    radius = shape.get('radius', 1)
                    color = shape.get('color', 'blue')
                    fill = shape.get('fill', False)

                    circle = plt.Circle(center, radius, color=color, fill=fill, alpha=0.6)
                    ax.add_patch(circle)

                elif shape_type == 'rectangle':
                    corner = shape.get('corner', (0, 0))  # 左下角
                    width = shape.get('width', 1)
                    height = shape.get('height', 1)
                    color = shape.get('color', 'green')
                    fill = shape.get('fill', False)

                    rectangle = plt.Rectangle(corner, width, height,
                                              color=color, fill=fill, alpha=0.6)
                    ax.add_patch(rectangle)

                elif shape_type == 'line':
                    start = shape.get('start', (0, 0))
                    end = shape.get('end', (1, 1))
                    color = shape.get('color', 'black')

                    ax.plot([start[0], end[0]], [start[1], end[1]],
                            color=color, linewidth=2)

                elif shape_type == 'polygon':
                    vertices = shape.get('vertices', [(0, 0), (1, 0), (0.5, 1)])
                    color = shape.get('color', 'orange')
                    fill = shape.get('fill', False)

                    polygon = plt.Polygon(vertices, color=color, fill=fill, alpha=0.6)
                    ax.add_patch(polygon)

        # 设置坐标轴范围
        ax.set_xlim(x_range)
        if y_range:
            ax.set_ylim(y_range)

        # 设置标签和标题
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')

        # 显示网格
        if grid:
            ax.grid(True, alpha=0.3)

        # 添加坐标轴
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)

        # 显示图例
        if (functions and len(functions) > 1) or points or (shapes and len(shapes) > 0):
            ax.legend()

        # 生成保存路径
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"plot_{plot_type}_{timestamp}.png"

        # 确保保存目录存在
        save_dir = os.path.dirname(save_path) if os.path.dirname(save_path) else '.'
        os.makedirs(save_dir, exist_ok=True)

        # 保存图像
        plt.tight_layout()
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close()  # 关闭图形以释放内存

        return {
            "success": True,
            "file_path": os.path.abspath(save_path),
            "plot_type": plot_type,
            "functions": functions,
            "description": f"成功绘制{plot_type}图像并保存到 {save_path}"
        }

    except Exception as e:
        plt.close()  # 确保在错误时也关闭图形
        return {
            "success": False,
            "error": str(e),
            "description": f"绘制图像时出错: {str(e)}"
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

4. draw_plot(plot_type, functions, x_range, y_range, points, shapes, title, xlabel, ylabel, grid, save_path, figure_size, dpi)
   - 功能：绘制函数图像或几何图形并保存到文件
   - 参数：
     * plot_type: "function"(函数图像), "geometry"(几何图形), "mixed"(混合)
     * functions: 函数表达式字符串或列表
     * x_range, y_range: 坐标轴范围
     * points: 点坐标列表
     * shapes: 几何图形描述列表
     * 其他参数用于自定义图像样式
   - 适用场景：需要可视化函数图像、绘制几何图形、生成数学图表时

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
    elif function_name == "draw_plot":
        return draw_plot(**kwargs)
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
    elif tool_name == "draw_plot":
        return draw_plot(**arguments)
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
    },
    {
        "type": "function",
        "function": {
            "name": "draw_plot",
            "description": "绘制函数或几何图形并保存至文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_type": {
                        "type": "string",
                        "enum": ["function", "geometry", "mixed"],
                        "description": "绘图类型：function(函数图像), geometry(几何图形), mixed(混合)"
                    },
                    "functions": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}}
                        ],
                        "description": "函数表达式字符串或字符串列表"
                    },
                    "x_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "x轴范围 [xmin, xmax]"
                    },
                    "y_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "y轴范围 [ymin, ymax]，可选"
                    },
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "点坐标列表 [[x1, y1], [x2, y2], ...]"
                    },
                    "shapes": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "几何图形列表，每个元素描述一个图形"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题"
                    },
                    "xlabel": {
                        "type": "string",
                        "description": "x轴标签"
                    },
                    "ylabel": {
                        "type": "string",
                        "description": "y轴标签"
                    },
                    "grid": {
                        "type": "boolean",
                        "description": "是否显示网格"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "保存路径，不指定时自动生成"
                    },
                    "figure_size": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "图像尺寸 [width, height]"
                    },
                    "dpi": {
                        "type": "integer",
                        "description": "图像分辨率"
                    }
                },
                "required": ["plot_type"]
            }
        }
    }
]

# 使用示例
if __name__ == "__main__":
    # 示例1：绘制函数图像
    result1 = draw_plot(
        plot_type="function",
        functions=["x**2", "sin(x)", "cos(x)"],
        x_range=[-5, 5],
        title="函数图像示例",
        save_path="function_example.png"
    )
    print("函数绘图结果:", result1)

    # 示例2：绘制几何图形
    shapes_example = [
        {"type": "circle", "center": (0, 0), "radius": 2, "color": "blue", "fill": False},
        {"type": "rectangle", "corner": (-1, -1), "width": 2, "height": 2, "color": "red", "fill": True},
        {"type": "line", "start": (-3, -3), "end": (3, 3), "color": "green"}
    ]

    result2 = draw_plot(
        plot_type="geometry",
        shapes=shapes_example,
        x_range=[-4, 4],
        y_range=[-4, 4],
        title="几何图形示例",
        save_path="geometry_example.png"
    )
    print("几何绘图结果:", result2)