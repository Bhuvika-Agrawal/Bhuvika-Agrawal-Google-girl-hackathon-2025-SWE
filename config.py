"""
Configuration module for AI-Powered Intelligent IDE
Centralizes all configuration settings for the application
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL = "gpt-4"
    FAST_MODEL = "gpt-4o"
    REASONING_MODEL = "o1-preview"
    
    # Temperature settings for different tasks
    TEMPERATURE_CREATIVE = 0.7  # For code generation
    TEMPERATURE_PRECISE = 0.3   # For debugging and optimization
    TEMPERATURE_ANALYSIS = 0.5  # For analysis tasks
    
    # Timeout settings (in seconds)
    API_TIMEOUT = 120
    QUICK_TIMEOUT = 60
    
    # Language Support
    SUPPORTED_LANGUAGES = {
        "Python": {
            "extension": "py",
            "test_framework": "pytest",
            "run_command": "python {file}",
            "test_command": "pytest {file} -v"
        },
        "Java": {
            "extension": "java",
            "test_framework": "JUnit",
            "run_command": "javac {file} && java {classname}",
            "test_command": "javac {file} && java org.junit.runner.JUnitCore {classname}"
        },
        "JavaScript": {
            "extension": "js",
            "test_framework": "Jest",
            "run_command": "node {file}",
            "test_command": "npm test"
        },
        "TypeScript": {
            "extension": "ts",
            "test_framework": "Jest",
            "run_command": "ts-node {file}",
            "test_command": "npm test"
        },
        "C++": {
            "extension": "cpp",
            "test_framework": "Google Test",
            "run_command": "g++ {file} -o output && ./output",
            "test_command": "g++ {file} -lgtest -lgtest_main -pthread -o test && ./test"
        },
        "Go": {
            "extension": "go",
            "test_framework": "testing",
            "run_command": "go run {file}",
            "test_command": "go test -v"
        },
        "Rust": {
            "extension": "rs",
            "test_framework": "built-in",
            "run_command": "rustc {file} && ./output",
            "test_command": "cargo test"
        },
        "C#": {
            "extension": "cs",
            "test_framework": "NUnit",
            "run_command": "dotnet run",
            "test_command": "dotnet test"
        }
    }
    
    # File naming conventions
    CODE_FILE_PREFIX = "generated_code"
    TEST_FILE_PREFIX = "test_generated_code"
    OPTIMIZED_FILE_PREFIX = "optimized_code"
    DEBUGGED_FILE_PREFIX = "debugged_code"
    
    # Logging Configuration
    LOG_FILE = "ide_assistant.log"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # UI Configuration
    PAGE_TITLE = "AI-Powered Intelligent IDE"
    PAGE_ICON = "💻"
    LAYOUT = "wide"
    
    # Feature Flags
    ENABLE_BUG_DETECTION = True
    ENABLE_OPTIMIZATION = True
    ENABLE_COMPLEXITY_ANALYSIS = True
    ENABLE_CODE_REVIEW = True
    ENABLE_CI_CD_HINTS = True
    
    # Agent System Messages
    AGENT_MESSAGES = {
        "problem_analyzer": (
            "You are an expert software architect. Analyze the problem statement and:\n"
            "1. Identify the core problem and requirements\n"
            "2. Break it into logical components and steps\n"
            "3. Suggest optimal data structures and algorithms\n"
            "4. Identify potential edge cases and constraints\n"
            "5. Provide a clear implementation roadmap\n"
            "**Do NOT generate code. Focus on analysis and design.**"
        ),
        "code_writer": (
            "You are an expert software developer. Write production-ready code that:\n"
            "1. Follows best practices and coding standards for the specified language\n"
            "2. Includes comprehensive docstrings and comments\n"
            "3. Implements proper error handling\n"
            "4. Uses appropriate design patterns\n"
            "5. Is modular, readable, and maintainable\n"
            "6. Includes type hints where applicable\n"
            "**Generate only compilable/executable code without explanatory text.**"
        ),
        "bug_detector": (
            "You are an expert code reviewer and bug detector. Analyze code for:\n"
            "1. Logic errors and potential bugs\n"
            "2. Security vulnerabilities\n"
            "3. Performance bottlenecks\n"
            "4. Code smells and anti-patterns\n"
            "5. Memory leaks and resource management issues\n"
            "6. Edge cases not handled\n"
            "Provide a detailed bug report with severity levels and fix suggestions."
        ),
        "debugger": (
            "You are an expert debugger. Fix all issues in the code:\n"
            "1. Syntax errors\n"
            "2. Logic bugs\n"
            "3. Runtime errors\n"
            "4. Security vulnerabilities\n"
            "5. Performance issues\n"
            "Return ONLY the corrected, production-ready code without explanations."
        ),
        "tester": (
            "You are an expert test engineer. Generate comprehensive unit tests that:\n"
            "1. Cover all functions and methods\n"
            "2. Test edge cases and boundary conditions\n"
            "3. Include positive and negative test cases\n"
            "4. Follow testing best practices (AAA pattern: Arrange, Act, Assert)\n"
            "5. Are executable and include necessary imports\n"
            "6. Use appropriate testing frameworks\n"
            "**Generate only test code without explanations.**"
        ),
        "optimizer": (
            "You are an expert in algorithm optimization. Optimize code for:\n"
            "1. Time complexity (reduce Big-O)\n"
            "2. Space complexity (memory efficiency)\n"
            "3. Code readability and maintainability\n"
            "4. Scalability\n"
            "Maintain correctness while improving performance. Return ONLY the optimized code."
        ),
        "complexity_analyzer": (
            "You are an expert in algorithm analysis. Provide:\n"
            "1. Time complexity (Big-O notation) with explanation\n"
            "2. Space complexity with explanation\n"
            "3. Best, average, and worst case scenarios\n"
            "4. Optimization suggestions if applicable\n"
            "Be precise and educational in your analysis."
        ),
        "code_reviewer": (
            "You are a senior code reviewer. Review code for:\n"
            "1. Code quality and best practices\n"
            "2. SOLID principles compliance\n"
            "3. Documentation quality\n"
            "4. Security considerations\n"
            "5. Performance implications\n"
            "6. Maintainability and scalability\n"
            "Provide a detailed review with ratings (1-10) and actionable feedback."
        )
    }
    
    # CI/CD Integration Templates
    CICD_TEMPLATES = {
        "github_actions": """# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
""",
        "docker": """# Dockerfile for production deployment
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
    }
    
    @classmethod
    def get_language_config(cls, language: str) -> Dict:
        """Get configuration for a specific language"""
        return cls.SUPPORTED_LANGUAGES.get(language, {})
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.OPENAI_API_KEY:
            return False
        return True

# Export configuration instance
config = Config()
