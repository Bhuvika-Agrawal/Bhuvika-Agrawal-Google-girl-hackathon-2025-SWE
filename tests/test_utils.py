"""
Unit tests for utility functions
"""

import pytest
import os
from utils import (
    extract_code_from_markdown,
    clean_code_response,
    save_code_to_file,
    load_code_from_file,
    validate_code_syntax,
    estimate_complexity,
    format_error_message,
    generate_git_commit_message,
    CodeMetrics
)

def test_extract_code_from_markdown():
    """Test code extraction from markdown"""
    # Test Python code block
    text = "```python\nprint('hello')\n```"
    result = extract_code_from_markdown(text, "python")
    assert result == "print('hello')"
    
    # Test generic code block
    text = "```\nprint('hello')\n```"
    result = extract_code_from_markdown(text)
    assert result == "print('hello')"
    
    # Test no code blocks
    text = "Just plain text"
    result = extract_code_from_markdown(text)
    assert result == "Just plain text"

def test_clean_code_response():
    """Test cleaning of code responses"""
    response = "Here's the code:\n```python\nprint('hello')\n```"
    result = clean_code_response(response)
    assert "Here's the code:" not in result
    assert "print('hello')" in result

def test_save_and_load_code(tmp_path):
    """Test saving and loading code files"""
    # Test saving
    test_file = tmp_path / "test_code.py"
    code = "print('hello world')"
    success, error = save_code_to_file(code, str(test_file), create_backup=False)
    assert success
    assert error is None
    assert test_file.exists()
    
    # Test loading
    loaded_code, error = load_code_from_file(str(test_file))
    assert error is None
    assert loaded_code == code

def test_validate_code_syntax():
    """Test code syntax validation"""
    # Valid Python code
    valid_code = "print('hello')"
    is_valid, errors = validate_code_syntax(valid_code, "Python")
    assert is_valid
    assert len(errors) == 0
    
    # Invalid Python code
    invalid_code = "print('hello'"
    is_valid, errors = validate_code_syntax(invalid_code, "Python")
    assert not is_valid
    assert len(errors) > 0

def test_estimate_complexity():
    """Test complexity estimation"""
    code = """
def example():
    for i in range(10):
        if i > 5:
            print(i)
    """
    metrics = estimate_complexity(code)
    assert metrics["loops"] >= 1
    assert metrics["conditionals"] >= 1
    assert metrics["functions"] >= 1
    assert metrics["cyclomatic_complexity"] >= 2

def test_format_error_message():
    """Test error message formatting"""
    error = ValueError("Test error")
    formatted = format_error_message(error)
    assert "ValueError" in formatted
    assert "Test error" in formatted

def test_generate_git_commit_message():
    """Test git commit message generation"""
    changes = {
        "language": "Python",
        "problem": "Implement binary search",
        "features": ["Added binary search", "Added tests"]
    }
    message = generate_git_commit_message(changes)
    assert "Python" in message
    assert "binary search" in message
    assert "Added binary search" in message

def test_code_metrics_count_lines():
    """Test line counting"""
    code = """
# This is a comment
print('hello')

print('world')
"""
    metrics = CodeMetrics.count_lines(code)
    assert metrics["total"] > 0
    assert metrics["code"] >= 2
    assert metrics["comments"] >= 1
    assert metrics["empty"] >= 1

def test_code_metrics_find_functions():
    """Test function detection"""
    # Python
    python_code = """
def func1():
    pass
    
def func2(x, y):
    return x + y
"""
    functions = CodeMetrics.find_functions(python_code, "Python")
    assert len(functions) == 2
    assert "func1" in functions
    assert "func2" in functions

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
