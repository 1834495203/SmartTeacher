import streamlit as st
import json
import os
from datetime import datetime

from chain.base_handler import ChainContext
from chain.math_chain import MathChain

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSONL_FILE_PATH = f"{CURRENT_DIR}/data/questions.jsonl"


def load_questions_from_jsonl(file_path="data/questions.jsonl"):
    """从JSONL文件加载问题"""
    questions = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        questions.append(json.loads(line.strip()))
        except Exception as e:
            st.error(f"加载问题数据失败：{str(e)}")
    return questions


def save_question_to_jsonl(question_data, file_path="data/questions.jsonl"):
    """保存问题到JSONL文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        print(f"save question:\n {question_data}")
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(question_data, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        st.error(f"保存问题失败：{str(e)}")
        return False


def show_error_collection():
    """显示错题集页面"""
    st.header("📚 错题集")
    
    questions = load_questions_from_jsonl(JSONL_FILE_PATH)
    
    if not questions:
        st.info("暂无保存的问题")
        return
    
    # 按时间倒序排列
    questions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # 搜索功能
    search_term = st.text_input("🔍 搜索问题：", placeholder="输入关键词搜索...")
    
    if search_term:
        questions = [q for q in questions if search_term.lower() in q.get('problem', '').lower()]
    
    st.write(f"共找到 {len(questions)} 个问题")
    
    # 分页显示
    items_per_page = 5
    total_pages = (len(questions) - 1) // items_per_page + 1 if questions else 0
    
    if total_pages > 0:
        page = st.selectbox("选择页面：", range(1, total_pages + 1)) - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(questions))
        
        for i, question in enumerate(questions[start_idx:end_idx], start_idx + 1):
            with st.expander(f"问题 {i}: {question.get('problem', '')[:50]}..."):
                st.write(f"**提问时间：** {question.get('timestamp', 'N/A')}")
                st.write(f"**用户背景：** {question.get('user_background', 'N/A')}")
                st.write(f"**问题：** {question.get('problem', 'N/A')}")
                st.write("**解答：**")
                st.markdown(question.get('answer', 'N/A'))
                
                # 删除按钮
                if st.button(f"🗑️ 删除", key=f"delete_{i}"):
                    if delete_question_from_jsonl(i - 1, JSONL_FILE_PATH):
                        st.success("问题已删除")
                        st.rerun()


def delete_question_from_jsonl(index, file_path="data/questions.jsonl"):
    """从JSONL文件删除指定索引的问题"""
    try:
        questions = load_questions_from_jsonl(file_path)
        if 0 <= index < len(questions):
            questions.pop(index)
            
            # 重写文件
            with open(file_path, 'w', encoding='utf-8') as f:
                for question in questions:
                    f.write(json.dumps(question, ensure_ascii=False) + '\n')
            return True
    except Exception as e:
        st.error(f"删除问题失败：{str(e)}")
    return False


def main():
    st.set_page_config(
        page_title="数学家教智能体",
        page_icon="🧮",
        layout="wide"
    )

    st.title("🧮 数学家教智能体")
    st.markdown("---")

    # 页面选择
    page = st.sidebar.selectbox("选择页面", ["💬 问答对话", "📚 错题集"])

    if page == "📚 错题集":
        show_error_collection()
        return

    # 侧边栏 - 用户信息
    with st.sidebar:
        st.header("📝 个人信息")

        education_level = st.selectbox(
            "教育阶段",
            ["小学", "初中", "高中", "大学", "研究生"]
        )

        math_level = st.selectbox(
            "数学水平",
            ["基础", "中等", "良好", "优秀"]
        )

        learning_style = st.selectbox(
            "学习偏好",
            ["详细步骤", "概念理解", "实际应用", "快速解答"]
        )

        api_key = st.text_input("请输入deepseek密钥", type="password")

        user_background = f"教育阶段：{education_level}，数学水平：{math_level}，学习偏好：{learning_style}"

        st.markdown("---")
        st.markdown("**当前背景信息：**")
        st.text(user_background)

        # 清除对话按钮
        if st.button("🗑️ 清除当前对话"):
            for key in list(st.session_state.keys()):
                if key.startswith('conversation_'):
                    del st.session_state[key]
            if 'current_problem' in st.session_state:
                del st.session_state['current_problem']
            st.rerun()

    # 初始化会话状态
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_problem' not in st.session_state:
        st.session_state.current_problem = ""
    if 'problem_solved' not in st.session_state:
        st.session_state.problem_solved = False

    # 主界面
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("❓ 提出问题")

        # 问题输入
        problem = st.text_area(
            "请输入您的数学问题：",
            height=150,
            placeholder="例如：解方程 x² - 5x + 6 = 0",
            value=st.session_state.current_problem
        )

        # 示例问题
        st.markdown("**示例问题：**")
        example_problems = [
            "计算 (2+3)×4-5²",
            "解方程 x² - 5x + 6 = 0",
            "分析函数 f(x) = x² - 4x + 3 的图像特征",
            "求导数 d/dx(x³ + 2x² - x + 1)"
        ]

        for i, example in enumerate(example_problems):
            if st.button(f"示例 {i+1}: {example}", key=f"example_{i}"):
                st.session_state.current_problem = example
                st.session_state.problem_solved = False
                st.rerun()

        # 更新当前问题
        if problem != st.session_state.current_problem:
            st.session_state.current_problem = problem
            st.session_state.problem_solved = False

    with col2:
        st.header("💡 解答")

        # 显示对话历史
        if st.session_state.conversation_history:
            st.subheader("📝 对话历史")
            for i, conv in enumerate(st.session_state.conversation_history):
                with st.expander(f"对话 {i+1}: {conv['question'][:30]}..."):
                    st.write(f"**问题：** {conv['question']}")
                    st.markdown(f"**解答：** {conv['answer']}")

        if st.button("🚀 获取解答", type="primary") and problem:
            with st.spinner("正在处理问题..."):
                try:
                    # 初始化责任链
                    math_chain = MathChain(api_key)

                    # 处理问题
                    context = math_chain.process(problem, user_background)

                    # 获取处理步骤
                    steps = math_chain.get_processing_steps(context)

                    context = ChainContext(
                        problem="111",
                        user_background="222"
                    )
                    context.final_answer = "123"

                    # 显示处理过程
                    st.success("✨ 处理完成！")

                    # 显示处理步骤
                    with st.expander("🔍 查看处理过程", expanded=False):

                        # 策略规划步骤
                        st.subheader("1️⃣ 策略规划")
                        strategy_status = steps["strategy_planning"]["status"]
                        if strategy_status == "completed":
                            st.success("✅ 策略规划完成")
                            strategy_content = steps["strategy_planning"]["content"]
                            if strategy_content:
                                st.write("**问题分析：**")
                                st.write(strategy_content.analysis)
                                if strategy_content.needs_tools:
                                    st.info(f"📋 需要使用 {len(strategy_content.tool_calls)} 个工具")
                        else:
                            st.error("❌ 策略规划失败")

                        # 工具执行步骤
                        st.subheader("2️⃣ 工具执行")
                        tool_status = steps["tool_execution"]["status"]
                        if tool_status == "completed":
                            st.success("✅ 工具执行完成")
                            tool_content = steps["tool_execution"]["content"]
                            if tool_content and tool_content.executed:
                                st.write(f"**执行摘要：** {tool_content.summary}")
                                if tool_content.results:
                                    for result in tool_content.results:
                                        if result.success:
                                            st.write(f"🔧 {result.tool_name}: ✅")
                                        else:
                                            st.write(f"🔧 {result.tool_name}: ❌")
                        elif tool_status == "skipped":
                            st.info("⏭️ 无需使用工具")
                        else:
                            st.error("❌ 工具执行失败")

                        # 答案整合步骤
                        st.subheader("3️⃣ 答案整合")
                        answer_status = steps["answer_synthesis"]["status"]
                        if answer_status == "completed":
                            st.success("✅ 答案整合完成")
                        else:
                            st.error("❌ 答案整合失败")

                    # 显示最终答案
                    st.markdown("### 📚 详细解答")
                    if context.final_answer:
                        st.markdown(context.final_answer)

                        # 添加到对话历史
                        st.session_state.conversation_history.append({
                            'question': problem,
                            'answer': context.final_answer,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                        # 问题解决确认
                        st.markdown("---")
                        col_yes, col_no = st.columns(2)

                        with col_yes:
                            if st.button("✅ 问题已解决", type="primary"):
                                st.write("按钮被点击")
                                # 保存到数据库
                                question_data = {
                                    'problem': problem,
                                    'answer': context.final_answer,
                                    'user_background': user_background,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'conversation_history': st.session_state.conversation_history
                                }

                                if save_question_to_jsonl(question_data, JSONL_FILE_PATH):
                                    st.success("✅ 问题已保存到错题集！")
                                    # 清除当前对话
                                    st.session_state.conversation_history = []
                                    st.session_state.current_problem = ""
                                    st.session_state.problem_solved = True
                                    st.rerun()

                        with col_no:
                            if st.button("❓ 继续提问"):
                                st.info("请继续提出相关问题")
                    else:
                        st.error("未能生成最终答案")

                except Exception as e:
                    st.error(f"处理过程中出现错误：{str(e)}")

        elif not problem:
            st.warning("请先输入数学问题")

    # 底部信息
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        🤖 由 DeepSeek AI 驱动的数学家教智能体 (责任链模式)<br>
        策略规划 → 工具执行 → 答案整合 | 支持多轮对话和错题集
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
