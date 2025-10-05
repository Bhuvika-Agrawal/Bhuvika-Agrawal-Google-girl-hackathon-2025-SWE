"""
Unit tests for configuration module
"""

import pytest
from config import Config, config

def test_config_validation():
    """Test configuration validation"""
    # This will fail if OPENAI_API_KEY is not set
    # In a real test environment, you'd mock this
    assert Config.DEFAULT_MODEL is not None
    assert Config.FAST_MODEL is not None

def test_supported_languages():
    """Test that all expected languages are supported"""
    expected_languages = ["Python", "Java", "JavaScript", "C++", "Go", "Rust", "C#", "TypeScript"]
    for lang in expected_languages:
        assert lang in Config.SUPPORTED_LANGUAGES
        lang_config = Config.SUPPORTED_LANGUAGES[lang]
        assert "extension" in lang_config
        assert "test_framework" in lang_config
        assert "run_command" in lang_config
        assert "test_command" in lang_config

def test_get_language_config():
    """Test getting language-specific configuration"""
    python_config = Config.get_language_config("Python")
    assert python_config["extension"] == "py"
    assert python_config["test_framework"] == "pytest"
    
    # Test unknown language
    unknown_config = Config.get_language_config("UnknownLang")
    assert unknown_config == {}

def test_agent_messages():
    """Test that all agent messages are defined"""
    expected_agents = [
        "problem_analyzer",
        "code_writer",
        "bug_detector",
        "debugger",
        "tester",
        "optimizer",
        "complexity_analyzer",
        "code_reviewer"
    ]
    for agent in expected_agents:
        assert agent in Config.AGENT_MESSAGES
        assert len(Config.AGENT_MESSAGES[agent]) > 0

def test_temperature_settings():
    """Test temperature settings are within valid range"""
    assert 0 <= Config.TEMPERATURE_CREATIVE <= 1
    assert 0 <= Config.TEMPERATURE_PRECISE <= 1
    assert 0 <= Config.TEMPERATURE_ANALYSIS <= 1

def test_timeout_settings():
    """Test timeout settings are positive"""
    assert Config.API_TIMEOUT > 0
    assert Config.QUICK_TIMEOUT > 0

def test_file_naming_conventions():
    """Test file naming conventions are set"""
    assert Config.CODE_FILE_PREFIX is not None
    assert Config.TEST_FILE_PREFIX is not None
    assert Config.OPTIMIZED_FILE_PREFIX is not None
    assert Config.DEBUGGED_FILE_PREFIX is not None

def test_ci_cd_templates():
    """Test CI/CD templates are available"""
    assert "github_actions" in Config.CICD_TEMPLATES
    assert "docker" in Config.CICD_TEMPLATES
    assert len(Config.CICD_TEMPLATES["github_actions"]) > 0
    assert len(Config.CICD_TEMPLATES["docker"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
