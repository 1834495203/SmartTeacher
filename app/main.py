import streamlit as st
from chain.math_chain import MathChain


def main():
    st.set_page_config(
        page_title="数学家教智能体",
        page_icon="🧮",
        layout="wide"
    )
    
    st.title("🧮 数学家教智能体")
    st.markdown("---")
    
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
        
        user_background = f"教育阶段：{education_level}，数学水平：{math_level}，学习偏好：{learning_style}"
        
        st.markdown("---")
        st.markdown("**当前背景信息：**")
        st.text(user_background)
    
    # 主界面
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("❓ 提出问题")
        
        # 问题输入
        problem = st.text_area(
            "请输入您的数学问题：",
            height=150,
            placeholder="例如：解方程 x² - 5x + 6 = 0"
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
                st.session_state.problem = example
                st.rerun()
        
        # 从session_state获取问题
        if 'problem' in st.session_state:
            problem = st.session_state.problem
    
    with col2:
        st.header("💡 解答")
        
        if st.button("🚀 获取解答", type="primary") and problem:
            with st.spinner("正在处理问题..."):
                try:
                    # 初始化责任链
                    math_chain = MathChain()
                    
                    # 处理问题
                    context = math_chain.process(problem, user_background)
                    
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
                    
                    # 显示最终答案
                    st.markdown("### 📚 详细解答")
                    if context.final_answer:
                        st.markdown(context.final_answer)
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
        策略规划 → 工具执行 → 答案整合
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
