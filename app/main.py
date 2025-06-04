import streamlit as st
import json
import os
from datetime import datetime

from chain.base_handler import ChainContext
from chain.math_chain import MathChain

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSONL_FILE_PATH = f"{CURRENT_DIR}/data/questions.jsonl"
PROMPTS_JSONL_FILE_PATH = f"{CURRENT_DIR}/data/prompts.jsonl"


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


def load_prompts_from_jsonl(file_path=PROMPTS_JSONL_FILE_PATH):
    """从JSONL文件加载Prompt"""
    prompts = {"默认Prompt": ""} # 添加一个默认选项
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        prompt_data = json.loads(line.strip())
                        prompts[prompt_data["name"]] = prompt_data["prompt"]
        except Exception as e:
            st.error(f"加载Prompt数据失败：{str(e)}")
    return prompts


def save_prompt_to_jsonl(prompt_name, prompt_content, file_path=PROMPTS_JSONL_FILE_PATH):
    """保存Prompt到JSONL文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        prompt_data = {"name": prompt_name, "prompt": prompt_content}
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(prompt_data, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        st.error(f"保存Prompt失败：{str(e)}")
        return False


def show_error_collection():
    """显示错题集页面"""
    st.header("📚 错题集")
    
    quest = load_questions_from_jsonl(JSONL_FILE_PATH)

    qs = []

    for questions in quest:
        if not questions:
            st.info("暂无保存的问题")
            return

        # 按时间倒序排列
        questions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        qs.append(questions)

    st.write(f"共找到 {len(qs)} 个问题")

    # 分页显示
    items_per_page = 5
    total_pages = (len(qs) - 1) // items_per_page + 1 if qs else 0

    if total_pages > 0:
        page = st.selectbox("选择页面：", range(1, total_pages + 1)) - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(qs))

        for i, question in enumerate(qs[start_idx:end_idx], start_idx + 1):
            for q in question:
                with st.expander(f"问题 {i}: {q.get('question', '')[:50]}..."):
                    st.write(f"**提问时间：** {q.get('timestamp', 'N/A')}")
                    st.write(f"**用户背景：** {q.get('user_background', 'N/A')}")
                    st.write(f"**问题：** {q.get('question', 'N/A')}")
                    st.write("**解答：**")
                    st.markdown(q.get('answer', 'N/A'))

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

        st.markdown("---")
        st.header("🔧 Prompt 设置")
        
        # 加载已有Prompts
        existing_prompts = load_prompts_from_jsonl()
        prompt_options = list(existing_prompts.keys())
        
        selected_prompt_name = st.selectbox(
            "选择一个Prompt模板：",
            options=prompt_options,
            index=0 # 默认选择第一个
        )
        
        custom_prompt_content = existing_prompts.get(selected_prompt_name, "")

        st.text_area(
            "当前选中的Prompt内容（只读）：",
            value=custom_prompt_content,
            height=100,
            disabled=True
        )

        with st.expander("添加新的Prompt模板"):
            new_prompt_name = st.text_input("新Prompt名称：")
            new_prompt_text = st.text_area("新Prompt内容：", height=150)
            if st.button("保存新Prompt"):
                if new_prompt_name and new_prompt_text:
                    if save_prompt_to_jsonl(new_prompt_name, new_prompt_text):
                        st.success(f"Prompt '{new_prompt_name}' 已保存！")
                        st.rerun() # 重新加载以更新下拉列表
                    else:
                        st.error("保存新Prompt失败。")
                else:
                    st.warning("请输入Prompt名称和内容。")

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
    # 新增：记录是否已经生成了解答
    if 'answer_generated' not in st.session_state:
        st.session_state.answer_generated = False
    # 新增：存储当前的解答内容
    if 'current_answer' not in st.session_state:
        st.session_state.current_answer = None
    if 'current_context' not in st.session_state:
        st.session_state.current_context = None
    if 'is_save' not in st.session_state:
        st.session_state.is_save = False

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
                problem = example
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

        # 获取解答按钮
        get_answer_clicked = st.button("🚀 获取解答", type="primary") and problem

        if get_answer_clicked:
            with st.spinner("正在处理问题..."):
                try:
                    st.session_state.is_save = False
                    # 初始化责任链
                    math_chain = MathChain(api_key)
                    
                    # 获取选中的prompt内容
                    selected_prompt_text = existing_prompts.get(selected_prompt_name, "")

                    # 处理问题
                    context = math_chain.process(problem, user_background, selected_prompt_text,
                                                 st.session_state.conversation_history)

                    # 获取处理步骤
                    steps = math_chain.get_processing_steps(context)

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
                    
                    # 模拟处理过程
                    # context = ChainContext(problem, user_background)
                    # context.final_answer = "123"

                    # 保存到会话状态
                    st.session_state.current_context = context
                    st.session_state.current_answer = context.final_answer
                    st.session_state.answer_generated = True
                    st.session_state.current_problem = problem

                    # 显示最终答案
                    if st.session_state.answer_generated and st.session_state.current_answer:
                        st.markdown("### 📚 详细解答")
                        img_path = context.metadata.get("img_path", None)
                        if img_path:
                            st.image(context.metadata.get("img_path", None), use_container_width=True)
                        st.markdown(st.session_state.current_answer)

                        # 添加到对话历史（只添加一次）
                        current_conv = {
                            'question': st.session_state.current_problem,
                            'answer': st.session_state.current_answer,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'user_background': user_background
                        }

                        # 检查是否已经添加过这个对话
                        if not st.session_state.conversation_history or \
                                st.session_state.conversation_history[-1]['question'] != current_conv['question']:
                            st.session_state.conversation_history.append(current_conv)

                except Exception as e:
                    st.error(f"处理过程中出现错误：{str(e)}")

        if st.session_state.answer_generated and st.session_state.current_answer and not st.session_state.is_save:
            # 问题解决确认
            st.markdown("---")

            if st.button("✅ 问题已解决", type="primary"):
                # 保存到数据库
                question_data = {
                    'problem': st.session_state.current_problem,
                    'answer': st.session_state.current_answer,
                    'user_background': user_background,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'conversation_history': st.session_state.conversation_history.copy()
                }

                if save_question_to_jsonl(st.session_state.conversation_history, JSONL_FILE_PATH):
                    st.success("✅ 问题已保存到错题集！")
                    # 清除相关状态
                    # st.session_state.conversation_history = []
                    st.session_state.current_problem = ""
                    st.session_state.problem_solved = True
                    st.session_state.answer_generated = False
                    st.session_state.current_answer = None
                    st.session_state.current_context = None
                    st.session_state.is_save = True
                    st.rerun()
                else:
                    st.error("保存失败，请重试")

        elif not problem:
            st.warning("请先输入数学问题")

    # 底部信息
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        🤖 由 DeepSeek AI 驱动的数学家教智能体 
        </div>
        """,
        unsafe_allow_html=True
    )

main()