import os
import streamlit as st
import subprocess
import platform
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Try to import autogen with the new package structure
try:
    import autogen
except ImportError:
    try:
        from autogen import ConversableAgent as autogen_ConversableAgent
        # Create a mock autogen module
        class MockAutogen:
            ConversableAgent = autogen_ConversableAgent
        autogen = MockAutogen()
    except ImportError:
        st.error("⚠️ AutoGen not properly installed. Please run: pip install pyautogen")
        st.stop()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ide_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    st.error("⚠️ Please set OPENAI_API_KEY in your .env file")
    st.stop()

# LLM Configuration with fallback
def get_llm_config(model: str = "gpt-4") -> Dict:
    """Get LLM configuration with error handling"""
    return {
        "config_list": [{
            "model": model,
            "api_key": api_key,
            "temperature": 0.7,
            "timeout": 120
        }],
        "cache_seed": None  # Disable caching for fresh responses
    }

# Define AI Agents with enhanced capabilities
problem_analyzer_agent = autogen.ConversableAgent(
    name="ProblemAnalyzer",
    system_message=(
        "You are an expert software architect. Analyze the problem statement and:\n"
        "1. Identify the core problem and requirements\n"
        "2. Break it into logical components and steps\n"
        "3. Suggest optimal data structures and algorithms\n"
        "4. Identify potential edge cases and constraints\n"
        "5. Provide a clear implementation roadmap\n"
        "**Do NOT generate code. Focus on analysis and design.**"
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)

code_writer_agent = autogen.ConversableAgent(
    name="CodeWriter",
    system_message=(
        "You are an expert software developer. Write production-ready code that:\n"
        "1. Follows best practices and coding standards for the specified language\n"
        "2. Includes comprehensive docstrings and comments\n"
        "3. Implements proper error handling\n"
        "4. Uses appropriate design patterns\n"
        "5. Is modular, readable, and maintainable\n"
        "6. Includes type hints where applicable\n"
        "**Generate only compilable/executable code without explanatory text.**"
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)

bug_detector_agent = autogen.ConversableAgent(
    name="BugDetector",
    system_message=(
        "You are an expert code reviewer and bug detector. Analyze code for:\n"
        "1. Logic errors and potential bugs\n"
        "2. Security vulnerabilities\n"
        "3. Performance bottlenecks\n"
        "4. Code smells and anti-patterns\n"
        "5. Memory leaks and resource management issues\n"
        "6. Edge cases not handled\n"
        "Provide a detailed bug report with severity levels and fix suggestions."
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)

debugger_agent = autogen.ConversableAgent(
    name="Debugger",
    system_message=(
        "You are an expert debugger. Fix all issues in the code:\n"
        "1. Syntax errors\n"
        "2. Logic bugs\n"
        "3. Runtime errors\n"
        "4. Security vulnerabilities\n"
        "5. Performance issues\n"
        "Return ONLY the corrected, production-ready code without explanations."
    ),
    llm_config=get_llm_config("gpt-4o"),
    human_input_mode="NEVER"
)

tester_agent = autogen.ConversableAgent(
    name="Tester",
    system_message=(
        "You are an expert test engineer. Generate comprehensive unit tests that:\n"
        "1. Cover all functions and methods\n"
        "2. Test edge cases and boundary conditions\n"
        "3. Include positive and negative test cases\n"
        "4. Follow testing best practices (AAA pattern: Arrange, Act, Assert)\n"
        "5. Are executable and include necessary imports\n"
        "6. Use appropriate testing frameworks (pytest, JUnit, Jest, etc.)\n"
        "**Generate only test code without explanations.**"
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)

test_debugger_agent = autogen.ConversableAgent(
    name="TestDebugger",
    system_message=(
        "Fix any syntax or logic errors in test code. "
        "Ensure tests are executable and follow testing framework conventions. "
        "Return ONLY the corrected test code."
    ),
    llm_config=get_llm_config("gpt-4o"),
    human_input_mode="NEVER"
)

optimizer_agent = autogen.ConversableAgent(
    name="Optimizer",
    system_message=(
        "You are an expert in algorithm optimization. Optimize code for:\n"
        "1. Time complexity (reduce Big-O)\n"
        "2. Space complexity (memory efficiency)\n"
        "3. Code readability and maintainability\n"
        "4. Scalability\n"
        "Maintain correctness while improving performance. "
        "Return ONLY the optimized code."
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)

complexity_analyzer_agent = autogen.ConversableAgent(
    name="ComplexityAnalyzer",
    system_message=(
        "You are an expert in algorithm analysis. Provide:\n"
        "1. Time complexity (Big-O notation) with explanation\n"
        "2. Space complexity with explanation\n"
        "3. Best, average, and worst case scenarios\n"
        "4. Optimization suggestions if applicable\n"
        "Be precise and educational in your analysis."
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)

code_reviewer_agent = autogen.ConversableAgent(
    name="CodeReviewer",
    system_message=(
        "You are a senior code reviewer. Review code for:\n"
        "1. Code quality and best practices\n"
        "2. SOLID principles compliance\n"
        "3. Documentation quality\n"
        "4. Security considerations\n"
        "5. Performance implications\n"
        "6. Maintainability and scalability\n"
        "Provide a detailed review with ratings (1-10) and actionable feedback."
    ),
    llm_config=get_llm_config("gpt-4"),
    human_input_mode="NEVER"
)


# Helper Functions
def safe_agent_call(agent: autogen.ConversableAgent, prompt: str, context: str = "") -> Tuple[Optional[str], Optional[str]]:
    """
    Safely call an agent with error handling
    Returns: (response, error_message)
    """
    try:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        response = agent.generate_reply(
            messages=[{"role": "user", "content": full_prompt}]
        )
        logger.info(f"Agent {agent.name} responded successfully")
        return response, None
    except Exception as e:
        error_msg = f"Error in {agent.name}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def save_to_file(content: str, filename: str) -> bool:
    """Save content to a file with error handling"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved content to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving to {filename}: {str(e)}")
        return False

def extract_code_from_response(response: str, language: str) -> str:
    """Extract code from markdown code blocks if present"""
    import re
    # Try to find code blocks
    pattern = f"```{language.lower()}\\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()
    
    # Try generic code blocks
    pattern = "```\\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return matches[0].strip()
    
    # Return as is if no code blocks found
    return response.strip()

# Session State Management
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'debugged_code' not in st.session_state:
    st.session_state.debugged_code = None
if 'optimized_code' not in st.session_state:
    st.session_state.optimized_code = None
if 'test_code' not in st.session_state:
    st.session_state.test_code = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'bug_reports' not in st.session_state:
    st.session_state.bug_reports = []

# Streamlit UI Configuration
st.set_page_config(
    page_title="AI-Powered Intelligent IDE",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<h1 class="main-header">💻 AI-Powered Intelligent IDE</h1>', unsafe_allow_html=True)
st.markdown("**Automated Code Generation, Testing & Debugging with Advanced AI**")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    user_language = st.selectbox(
        "Programming Language:",
        ["Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust", "C#"],
        help="Select the target programming language"
    )
    
    st.divider()
    
    st.subheader("🔧 Features")
    enable_bug_detection = st.checkbox("Advanced Bug Detection", value=True)
    enable_optimization = st.checkbox("Code Optimization", value=True)
    enable_complexity_analysis = st.checkbox("Complexity Analysis", value=True)
    enable_code_review = st.checkbox("Code Review", value=True)
    
    st.divider()
    
    st.subheader("📊 Statistics")
    st.metric("Problems Analyzed", len(st.session_state.analysis_history))
    st.metric("Bugs Detected", len(st.session_state.bug_reports))
    
    st.divider()
    
    if st.button("🗑️ Clear Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session cleared!")
        st.rerun()

# Main Content Area
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Code Generation", "🐛 Debug & Optimize", "📝 Test Generation", "📊 Analysis & Review"])

with tab1:
    st.markdown('<div class="section-header">Problem Statement</div>', unsafe_allow_html=True)
    user_problem = st.text_area(
        "Enter your programming problem:",
        height=150,
        placeholder="E.g., Create a function to find the longest palindromic substring in a given string...",
        help="Describe the problem you want to solve. Be specific about requirements and constraints."
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        generate_button = st.button("🎯 Generate Solution", type="primary", use_container_width=True)
    
    with col2:
        if st.session_state.generated_code:
            st.button("🔄 Regenerate", use_container_width=True)
    
    if generate_button:
        if not user_problem:
            st.warning("⚠️ Please enter a problem statement.")
        else:
            # Save to history
            st.session_state.analysis_history.append({
                'timestamp': datetime.now().isoformat(),
                'problem': user_problem,
                'language': user_language
            })
            
            with st.spinner("🔍 Analyzing problem..."):
                problem_breakdown, error = safe_agent_call(
                    problem_analyzer_agent,
                    f"Analyze this problem for {user_language} implementation:\n\n{user_problem}"
                )
                
                if error:
                    st.error(f"❌ {error}")
                    st.stop()
                
                with st.expander("📋 Problem Analysis", expanded=True):
                    st.markdown(problem_breakdown)
            
            with st.spinner(f"💻 Generating {user_language} code..."):
                code_prompt = f"Write {user_language} code based on this analysis:\n\n{problem_breakdown}"
                generated_code, error = safe_agent_call(code_writer_agent, code_prompt)
                
                if error:
                    st.error(f"❌ {error}")
                    st.stop()
                
                # Extract code from response
                generated_code = extract_code_from_response(generated_code, user_language)
                st.session_state.generated_code = generated_code
                
                st.markdown('<div class="section-header">Generated Code</div>', unsafe_allow_html=True)
                st.code(generated_code, language=user_language.lower())
                
                # Save generated code
                filename = f"generated_code.{user_language.lower()}"
                if save_to_file(generated_code, filename):
                    st.success(f"✅ Code saved to `{filename}`")
            
            # Bug Detection
            if enable_bug_detection:
                with st.spinner("🔍 Detecting potential bugs..."):
                    bug_report, error = safe_agent_call(
                        bug_detector_agent,
                        f"Analyze this {user_language} code for bugs:\n\n{generated_code}"
                    )
                    
                    if bug_report and not error:
                        st.session_state.bug_reports.append({
                            'timestamp': datetime.now().isoformat(),
                            'report': bug_report
                        })
                        
                        with st.expander("🐛 Bug Detection Report", expanded=False):
                            st.markdown(bug_report)
            
            # Complexity Analysis
            if enable_complexity_analysis:
                with st.spinner("📊 Analyzing complexity..."):
                    complexity_analysis, error = safe_agent_call(
                        complexity_analyzer_agent,
                        f"Analyze the complexity of this {user_language} code:\n\n{generated_code}"
                    )
                    
                    if complexity_analysis and not error:
                        with st.expander("📈 Complexity Analysis", expanded=True):
                            st.markdown(complexity_analysis)

with tab2:
    st.markdown('<div class="section-header">Debug & Optimize Code</div>', unsafe_allow_html=True)
    
    if st.session_state.generated_code:
        st.markdown("**Current Code:**")
        st.code(st.session_state.generated_code, language=user_language.lower())
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔧 Debug Code", type="primary", use_container_width=True):
                with st.spinner("🔧 Debugging code..."):
                    debugged_code, error = safe_agent_call(
                        debugger_agent,
                        f"Fix all issues in this {user_language} code:\n\n{st.session_state.generated_code}"
                    )
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        debugged_code = extract_code_from_response(debugged_code, user_language)
                        st.session_state.debugged_code = debugged_code
                        
                        st.success("✅ Code debugged successfully!")
                        st.markdown("**Debugged Code:**")
                        st.code(debugged_code, language=user_language.lower())
                        
                        # Save debugged code
                        filename = f"debugged_code.{user_language.lower()}"
                        if save_to_file(debugged_code, filename):
                            st.info(f"💾 Saved to `{filename}`")
        
        with col2:
            if st.button("⚡ Optimize Code", type="primary", use_container_width=True) and enable_optimization:
                code_to_optimize = st.session_state.debugged_code or st.session_state.generated_code
                
                with st.spinner("⚡ Optimizing code..."):
                    optimized_code, error = safe_agent_call(
                        optimizer_agent,
                        f"Optimize this {user_language} code:\n\n{code_to_optimize}"
                    )
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        optimized_code = extract_code_from_response(optimized_code, user_language)
                        st.session_state.optimized_code = optimized_code
                        
                        st.success("✅ Code optimized successfully!")
                        st.markdown("**Optimized Code:**")
                        st.code(optimized_code, language=user_language.lower())
                        
                        # Save optimized code
                        filename = f"optimized_code.{user_language.lower()}"
                        if save_to_file(optimized_code, filename):
                            st.info(f"💾 Saved to `{filename}`")
                        
                        # Updated complexity analysis
                        with st.spinner("📊 Analyzing optimized code complexity..."):
                            complexity_analysis, error = safe_agent_call(
                                complexity_analyzer_agent,
                                f"Analyze the complexity of this optimized {user_language} code:\n\n{optimized_code}"
                            )
                            
                            if complexity_analysis and not error:
                                with st.expander("📈 Updated Complexity Analysis", expanded=True):
                                    st.markdown(complexity_analysis)
    else:
        st.info("ℹ️ Generate code first in the 'Code Generation' tab.")

with tab3:
    st.markdown('<div class="section-header">Test Generation</div>', unsafe_allow_html=True)
    
    final_code = st.session_state.optimized_code or st.session_state.debugged_code or st.session_state.generated_code
    
    if final_code:
        st.markdown("**Code to Test:**")
        st.code(final_code, language=user_language.lower())
        
        if st.button("🧪 Generate Tests", type="primary", use_container_width=True):
            with st.spinner("🧪 Generating comprehensive unit tests..."):
                test_prompt = f"Generate comprehensive unit tests for this {user_language} code:\n\n{final_code}"
                generated_tests, error = safe_agent_call(tester_agent, test_prompt)
                
                if error:
                    st.error(f"❌ {error}")
                else:
                    generated_tests = extract_code_from_response(generated_tests, user_language)
                    
                    # Debug test code
                    with st.spinner("🔧 Debugging test code..."):
                        debugged_tests, error = safe_agent_call(
                            test_debugger_agent,
                            f"Fix any issues in these {user_language} tests:\n\n{generated_tests}"
                        )
                        
                        if not error:
                            debugged_tests = extract_code_from_response(debugged_tests, user_language)
                            st.session_state.test_code = debugged_tests
                        else:
                            st.session_state.test_code = generated_tests
                    
                    st.success("✅ Tests generated successfully!")
                    st.markdown("**Generated Tests:**")
                    st.code(st.session_state.test_code, language=user_language.lower())
                    
                    # Save test code
                    filename = f"test_generated_code.{user_language.lower()}"
                    if save_to_file(st.session_state.test_code, filename):
                        st.info(f"💾 Saved to `{filename}`")
                    
                    # Provide execution instructions
                    with st.expander("▶️ How to Run Tests", expanded=True):
                        if user_language == "Python":
                            st.code("pytest test_generated_code.py -v", language="bash")
                        elif user_language == "Java":
                            st.code("javac test_generated_code.java && java org.junit.runner.JUnitCore TestClass", language="bash")
                        elif user_language == "JavaScript":
                            st.code("npm test", language="bash")
                        elif user_language == "C++":
                            st.code("g++ test_generated_code.cpp -o test && ./test", language="bash")
    else:
        st.info("ℹ️ Generate code first in the 'Code Generation' tab.")

with tab4:
    st.markdown('<div class="section-header">Code Analysis & Review</div>', unsafe_allow_html=True)
    
    final_code = st.session_state.optimized_code or st.session_state.debugged_code or st.session_state.generated_code
    
    if final_code and enable_code_review:
        if st.button("📝 Perform Code Review", type="primary", use_container_width=True):
            with st.spinner("📝 Conducting comprehensive code review..."):
                review_prompt = f"Review this {user_language} code:\n\n{final_code}"
                code_review, error = safe_agent_call(code_reviewer_agent, review_prompt)
                
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.success("✅ Code review completed!")
                    with st.expander("📋 Detailed Code Review", expanded=True):
                        st.markdown(code_review)
    
    # Display History
    st.divider()
    st.subheader("📜 Session History")
    
    if st.session_state.analysis_history:
        for idx, item in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(f"Problem {len(st.session_state.analysis_history) - idx}: {item['problem'][:50]}..."):
                st.write(f"**Language:** {item['language']}")
                st.write(f"**Timestamp:** {item['timestamp']}")
                st.write(f"**Problem:** {item['problem']}")
    else:
        st.info("No history yet. Start by generating some code!")

# Download Section
st.divider()
st.markdown('<div class="section-header">📥 Download Generated Files</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if final_code:
        st.download_button(
            label="📄 Download Code",
            data=final_code,
            file_name=f"generated_code.{user_language.lower()}",
            mime="text/plain",
            use_container_width=True
        )

with col2:
    if st.session_state.test_code:
        st.download_button(
            label="🧪 Download Tests",
            data=st.session_state.test_code,
            file_name=f"test_code.{user_language.lower()}",
            mime="text/plain",
            use_container_width=True
        )

with col3:
    # Generate project report
    if final_code:
        report = f"""# AI-Generated Code Report

## Problem Statement
{user_problem if user_problem else 'N/A'}

## Generated Code ({user_language})
```{user_language.lower()}
{final_code}
```

## Tests
```{user_language.lower()}
{st.session_state.test_code if st.session_state.test_code else 'N/A'}
```

## Generation Details
- Language: {user_language}
- Timestamp: {datetime.now().isoformat()}
- Features: {'Bug Detection, ' if enable_bug_detection else ''}{'Optimization, ' if enable_optimization else ''}{'Complexity Analysis' if enable_complexity_analysis else ''}
"""
        st.download_button(
            label="📊 Download Report",
            data=report,
            file_name="code_report.md",
            mime="text/markdown",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🚀 <strong>AI-Powered Intelligent IDE</strong></p>
    <p>Automated Code Generation • Advanced Debugging • Comprehensive Testing • CI/CD Ready</p>
    <p style='font-size: 0.9rem;'>Built for Google Girl Hackathon 2025 | Developer Productivity Solution</p>
</div>
""", unsafe_allow_html=True)

