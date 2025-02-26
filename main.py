import os
import streamlit as st
import subprocess
import platform
from dotenv import load_dotenv
import autogen

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Define AI Agents
problem_analyzer_agent = autogen.ConversableAgent(
    name="ProblemAnalyzer",
    system_message="Analyze the problem and break it into logical steps. **Do NOT generate code.**",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": api_key}]},
)

code_writer_agent = autogen.ConversableAgent(
    name="CodeWriter",
    system_message="Write clean, well-documented code in the user-specified language. **Do not assume Python as default.**",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": api_key}]},
)

debugger_agent = autogen.ConversableAgent(
    name="Debugger",
    system_message="Fix syntax errors in the provided code and return only the corrected version.",
    llm_config={"config_list": [{"model": "o1-preview", "api_key": api_key}]},
)

tester_agent = autogen.ConversableAgent(
    name="Tester",
    system_message="Generate unit tests in the specified language, ensuring correctness. **Do NOT add explanations.**",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": api_key}]},
)

final_debugger_agent = autogen.ConversableAgent(
    name="FinalDebugger",
    system_message="Fix any syntax errors in test cases and return corrected code.",
    llm_config={"config_list": [{"model": "o1-preview", "api_key": api_key}]},
)

debugging_agent = autogen.ConversableAgent(
    name="Optimizer",
    system_message="Optimize the code for time and space complexity while maintaining correctness.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": api_key}]},
)

complexity_analysis_agent = autogen.ConversableAgent(
    name="ComplexityAnalyzer",
    system_message="Analyze and provide the time and space complexity of the given code.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": api_key}]},
)

# Streamlit UI
st.title("💡 AI-Powered Intelligent IDE")

# User inputs
user_problem = st.text_area("Enter a programming problem:")
user_language = st.selectbox("Select programming language:", ["Python", "Java", "C++", "JavaScript", "Other"])

if st.button("Generate Code"):
    if not user_problem:
        st.warning("Please enter a problem statement.")
    else:
        st.write("🔹 **Analyzing Problem...**")
        problem_breakdown = problem_analyzer_agent.generate_reply(
            messages=[{"role": "user", "content": user_problem}]
        )
        st.write(problem_breakdown)

        st.write(f"🔹 **Generating Code in {user_language}...**")
        code_prompt = f"Write {user_language} code for this task:\n\n{problem_breakdown}"
        generated_code = code_writer_agent.generate_reply(
            messages=[{"role": "user", "content": code_prompt}]
        )
        st.code(generated_code, language=user_language.lower())

        st.write("🔹 **Analyzing Time and Space Complexity...**")
        complexity_analysis = complexity_analysis_agent.generate_reply(
            messages=[{"role": "user", "content": generated_code}]
        )
        st.write(complexity_analysis)

        st.write("🔹 **Debugging Code for Syntax Errors...**")
        debugged_code = debugger_agent.generate_reply(
            messages=[{"role": "user", "content": generated_code}]
        )
        st.code(debugged_code, language=user_language.lower())

        st.write("🔹 **Generating Unit Tests...**")
        test_prompt = f"Write valid {user_language} unit tests:\n\n{debugged_code}"
        generated_tests = tester_agent.generate_reply(
            messages=[{"role": "user", "content": test_prompt}]
        )
        st.code(generated_tests, language=user_language.lower())

        st.write("🔹 **Debugging Test Code for Syntax Errors...**")
        debugged_tests = final_debugger_agent.generate_reply(
            messages=[{"role": "user", "content": generated_tests}]
        )
        st.code(debugged_tests, language=user_language.lower())

        # Optimization button
        if st.button("🔄 Optimize Code"):
            st.write("🔹 **Optimizing Code for Better Time/Space Complexity...**")
            optimize_prompt = f"Optimize the following {user_language} code:\n\n{debugged_code}"
            optimized_code = debugging_agent.generate_reply(
                messages=[{"role": "user", "content": optimize_prompt}]
            )
            st.code(optimized_code, language=user_language.lower())

            # Updated Complexity Analysis for Optimized Code
            st.write("🔹 **Updated Time and Space Complexity Analysis...**")
            updated_complexity_analysis = complexity_analysis_agent.generate_reply(
                messages=[{"role": "user", "content": optimized_code}]
            )
            st.write(updated_complexity_analysis)

            # Store optimized code for download
            final_code = optimized_code
        else:
            final_code = debugged_code

        # Provide a Download Button
        st.download_button(
            label="📥 Download Final Code",
            data=final_code,
            file_name="generated_code.txt",
            mime="text/plain"
        )

st.write("🚀 **AI-powered coding assistant for all your development needs!**")
