"""
Utility functions for the AI-Powered Intelligent IDE
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)

def extract_code_from_markdown(text: str, language: Optional[str] = None) -> str:
    """
    Extract code from markdown code blocks
    
    Args:
        text: The text containing markdown code blocks
        language: Optional language specifier to match specific code blocks
    
    Returns:
        Extracted code as a string
    """
    if not text:
        return ""
    
    # Try language-specific code block
    if language:
        pattern = f"```{language.lower()}\\s*\\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0].strip()
    
    # Try generic code blocks
    pattern = r"```(?:\w+)?\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[0].strip()
    
    # Return as is if no code blocks found
    return text.strip()

def clean_code_response(response: str) -> str:
    """
    Clean up code response by removing common artifacts
    
    Args:
        response: Raw response from the AI agent
    
    Returns:
        Cleaned code string
    """
    # Remove markdown code blocks
    response = extract_code_from_markdown(response)
    
    # Remove common explanatory phrases
    phrases_to_remove = [
        "Here's the code:",
        "Here is the code:",
        "The code is:",
        "Here's the implementation:",
        "Here is the implementation:",
    ]
    
    for phrase in phrases_to_remove:
        if response.lower().startswith(phrase.lower()):
            response = response[len(phrase):].strip()
    
    return response

def save_code_to_file(code: str, filename: str, create_backup: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Save code to a file with error handling and optional backup
    
    Args:
        code: The code content to save
        filename: The target filename
        create_backup: Whether to create a backup if file exists
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Create backup if file exists
        if create_backup and os.path.exists(filename):
            backup_name = f"{filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(filename, backup_name)
            logger.info(f"Created backup: {backup_name}")
        
        # Save new content
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        logger.info(f"Saved code to {filename}")
        return True, None
    
    except Exception as e:
        error_msg = f"Error saving to {filename}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def load_code_from_file(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Load code from a file
    
    Args:
        filename: The file to load
    
    Returns:
        Tuple of (code_content, error_message)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except Exception as e:
        error_msg = f"Error reading {filename}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def validate_code_syntax(code: str, language: str) -> Tuple[bool, List[str]]:
    """
    Validate code syntax for supported languages
    
    Args:
        code: The code to validate
        language: The programming language
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if language.lower() == "python":
        try:
            compile(code, '<string>', 'exec')
            return True, []
        except SyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.msg}")
            return False, errors
    
    # For other languages, we'll rely on the AI agents
    # In a production system, you'd integrate language-specific validators
    return True, []

def estimate_complexity(code: str) -> Dict[str, Any]:
    """
    Provide a rough estimate of code complexity
    
    Args:
        code: The code to analyze
    
    Returns:
        Dictionary with complexity metrics
    """
    lines = code.split('\n')
    non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    # Count control structures
    loops = len(re.findall(r'\b(for|while)\b', code))
    conditionals = len(re.findall(r'\bif\b', code))
    functions = len(re.findall(r'\bdef\b|\bfunction\b|\bpublic\s+\w+\s+\w+\s*\(', code))
    
    return {
        "lines_of_code": len(non_empty_lines),
        "loops": loops,
        "conditionals": conditionals,
        "functions": functions,
        "cyclomatic_complexity": 1 + conditionals + loops  # Simplified McCabe complexity
    }

def format_error_message(error: Exception) -> str:
    """
    Format exception for user-friendly display
    
    Args:
        error: The exception to format
    
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    return f"**{error_type}**: {error_msg}"

def create_project_structure(base_path: str, language: str) -> Dict[str, str]:
    """
    Create a standard project structure for the given language
    
    Args:
        base_path: Base directory for the project
        language: Programming language
    
    Returns:
        Dictionary mapping purpose to created paths
    """
    structure = {
        "src": os.path.join(base_path, "src"),
        "tests": os.path.join(base_path, "tests"),
        "docs": os.path.join(base_path, "docs"),
        "config": os.path.join(base_path, "config")
    }
    
    try:
        for purpose, path in structure.items():
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created directory: {path}")
        
        return structure
    
    except Exception as e:
        logger.error(f"Error creating project structure: {str(e)}")
        return {}

def generate_requirements_file(dependencies: List[str], filename: str = "requirements.txt") -> bool:
    """
    Generate a requirements.txt file from a list of dependencies
    
    Args:
        dependencies: List of Python packages
        filename: Output filename
    
    Returns:
        Success status
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for dep in sorted(set(dependencies)):
                f.write(f"{dep}\n")
        logger.info(f"Generated {filename}")
        return True
    except Exception as e:
        logger.error(f"Error generating {filename}: {str(e)}")
        return False

def run_code_in_sandbox(code: str, language: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """
    Run code in a sandboxed environment (requires Docker)
    
    Args:
        code: The code to run
        language: Programming language
        timeout: Maximum execution time in seconds
    
    Returns:
        Tuple of (success, stdout, stderr)
    """
    # This is a placeholder implementation
    # In production, you'd use Docker or a secure sandbox
    logger.warning("Sandbox execution not implemented - use with caution")
    return False, "", "Sandbox execution not available"

def generate_git_commit_message(changes: Dict[str, Any]) -> str:
    """
    Generate a meaningful git commit message based on changes
    
    Args:
        changes: Dictionary describing the changes made
    
    Returns:
        Git commit message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    msg_parts = [
        "feat: AI-generated code updates",
        "",
        f"Generated at: {timestamp}",
    ]
    
    if changes.get("language"):
        msg_parts.append(f"Language: {changes['language']}")
    
    if changes.get("problem"):
        msg_parts.append(f"Problem: {changes['problem'][:100]}...")
    
    if changes.get("features"):
        msg_parts.append("")
        msg_parts.append("Features:")
        for feature in changes['features']:
            msg_parts.append(f"- {feature}")
    
    return "\n".join(msg_parts)

def parse_test_results(output: str, language: str) -> Dict[str, Any]:
    """
    Parse test execution results
    
    Args:
        output: Raw test output
        language: Programming language
    
    Returns:
        Dictionary with parsed test results
    """
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "duration": 0.0,
        "failures": []
    }
    
    # Python pytest parsing
    if language.lower() == "python":
        # Look for pytest summary
        match = re.search(r'(\d+) passed', output)
        if match:
            result["passed"] = int(match.group(1))
        
        match = re.search(r'(\d+) failed', output)
        if match:
            result["failed"] = int(match.group(1))
        
        result["total"] = result["passed"] + result["failed"]
    
    return result

def generate_ci_cd_config(language: str, test_command: str) -> str:
    """
    Generate CI/CD configuration for GitHub Actions
    
    Args:
        language: Programming language
        test_command: Command to run tests
    
    Returns:
        YAML configuration as string
    """
    if language.lower() == "python":
        return f"""name: Python CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: {test_command}
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.11'
"""
    
    # Add templates for other languages as needed
    return ""

def calculate_code_quality_score(metrics: Dict[str, Any]) -> float:
    """
    Calculate a code quality score based on various metrics
    
    Args:
        metrics: Dictionary of code metrics
    
    Returns:
        Quality score (0-100)
    """
    score = 100.0
    
    # Penalize high complexity
    complexity = metrics.get("cyclomatic_complexity", 0)
    if complexity > 10:
        score -= min(30, (complexity - 10) * 2)
    
    # Reward documentation
    if metrics.get("has_docstrings", False):
        score += 10
    
    # Penalize very long functions
    if metrics.get("max_function_length", 0) > 50:
        score -= 10
    
    return max(0.0, min(100.0, score))

class CodeMetrics:
    """Class to compute various code metrics"""
    
    @staticmethod
    def count_lines(code: str) -> Dict[str, int]:
        """Count different types of lines in code"""
        lines = code.split('\n')
        
        total = len(lines)
        empty = sum(1 for line in lines if not line.strip())
        comments = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
        code_lines = total - empty - comments
        
        return {
            "total": total,
            "code": code_lines,
            "comments": comments,
            "empty": empty
        }
    
    @staticmethod
    def find_functions(code: str, language: str) -> List[str]:
        """Find all function definitions in code"""
        functions = []
        
        if language.lower() == "python":
            pattern = r'def\s+(\w+)\s*\('
            functions = re.findall(pattern, code)
        elif language.lower() in ["java", "c++", "c#"]:
            pattern = r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\('
            functions = re.findall(pattern, code)
        elif language.lower() in ["javascript", "typescript"]:
            pattern = r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\('
            matches = re.findall(pattern, code)
            functions = [m[0] or m[1] for m in matches]
        
        return functions
