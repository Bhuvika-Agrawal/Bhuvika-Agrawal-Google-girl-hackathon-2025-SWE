"""
Command-line interface for AI-Powered Intelligent IDE
Provides a non-GUI way to interact with the IDE features
"""

import argparse
import sys
import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
import autogen

from config import Config
from utils import (
    extract_code_from_markdown,
    save_code_to_file,
    load_code_from_file,
    estimate_complexity,
    generate_git_commit_message
)

# Load environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_agent(name: str, system_message: str, model: str = "gpt-4") -> autogen.ConversableAgent:
    """Create an AI agent"""
    return autogen.ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config={
            "config_list": [{
                "model": model,
                "api_key": api_key,
                "temperature": 0.7
            }]
        },
        human_input_mode="NEVER"
    )


def generate_code(problem: str, language: str, output_file: Optional[str] = None) -> bool:
    """Generate code from problem statement"""
    logger.info(f"Generating {language} code for problem...")
    
    try:
        # Create agents
        analyzer = create_agent("Analyzer", Config.AGENT_MESSAGES["problem_analyzer"])
        coder = create_agent("Coder", Config.AGENT_MESSAGES["code_writer"])
        
        # Analyze problem
        print("\n🔍 Analyzing problem...")
        analysis = analyzer.generate_reply(
            messages=[{"role": "user", "content": f"Analyze this problem for {language}: {problem}"}]
        )
        print(f"\n{analysis}\n")
        
        # Generate code
        print(f"\n💻 Generating {language} code...")
        code = coder.generate_reply(
            messages=[{"role": "user", "content": f"Write {language} code: {analysis}"}]
        )
        
        # Extract and clean code
        code = extract_code_from_markdown(code, language)
        
        print("\n" + "="*80)
        print("GENERATED CODE:")
        print("="*80)
        print(code)
        print("="*80 + "\n")
        
        # Save to file
        if output_file:
            success, error = save_code_to_file(code, output_file)
            if success:
                print(f"✅ Code saved to {output_file}")
            else:
                print(f"❌ Error saving code: {error}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def debug_code(input_file: str, output_file: Optional[str] = None) -> bool:
    """Debug existing code"""
    logger.info(f"Debugging code from {input_file}...")
    
    try:
        # Load code
        code, error = load_code_from_file(input_file)
        if error:
            print(f"❌ Error loading file: {error}")
            return False
        
        print(f"\n🔧 Debugging code from {input_file}...")
        
        # Create debugger
        debugger = create_agent("Debugger", Config.AGENT_MESSAGES["debugger"])
        
        # Debug code
        fixed_code = debugger.generate_reply(
            messages=[{"role": "user", "content": f"Fix all issues in this code:\n\n{code}"}]
        )
        
        # Extract code
        fixed_code = extract_code_from_markdown(fixed_code)
        
        print("\n" + "="*80)
        print("DEBUGGED CODE:")
        print("="*80)
        print(fixed_code)
        print("="*80 + "\n")
        
        # Save
        if output_file:
            success, error = save_code_to_file(fixed_code, output_file)
            if success:
                print(f"✅ Fixed code saved to {output_file}")
            else:
                print(f"❌ Error saving: {error}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error debugging code: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def generate_tests(input_file: str, language: str, output_file: Optional[str] = None) -> bool:
    """Generate tests for existing code"""
    logger.info(f"Generating tests for {input_file}...")
    
    try:
        # Load code
        code, error = load_code_from_file(input_file)
        if error:
            print(f"❌ Error loading file: {error}")
            return False
        
        print(f"\n🧪 Generating {language} tests...")
        
        # Create tester
        tester = create_agent("Tester", Config.AGENT_MESSAGES["tester"])
        
        # Generate tests
        tests = tester.generate_reply(
            messages=[{"role": "user", "content": f"Generate comprehensive {language} tests for:\n\n{code}"}]
        )
        
        # Extract tests
        tests = extract_code_from_markdown(tests, language)
        
        print("\n" + "="*80)
        print("GENERATED TESTS:")
        print("="*80)
        print(tests)
        print("="*80 + "\n")
        
        # Save
        if output_file:
            success, error = save_code_to_file(tests, output_file)
            if success:
                print(f"✅ Tests saved to {output_file}")
            else:
                print(f"❌ Error saving: {error}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating tests: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def optimize_code(input_file: str, output_file: Optional[str] = None) -> bool:
    """Optimize existing code"""
    logger.info(f"Optimizing code from {input_file}...")
    
    try:
        # Load code
        code, error = load_code_from_file(input_file)
        if error:
            print(f"❌ Error loading file: {error}")
            return False
        
        print(f"\n⚡ Optimizing code from {input_file}...")
        
        # Create optimizer
        optimizer = create_agent("Optimizer", Config.AGENT_MESSAGES["optimizer"])
        
        # Optimize
        optimized = optimizer.generate_reply(
            messages=[{"role": "user", "content": f"Optimize this code:\n\n{code}"}]
        )
        
        # Extract code
        optimized = extract_code_from_markdown(optimized)
        
        print("\n" + "="*80)
        print("OPTIMIZED CODE:")
        print("="*80)
        print(optimized)
        print("="*80 + "\n")
        
        # Save
        if output_file:
            success, error = save_code_to_file(optimized, output_file)
            if success:
                print(f"✅ Optimized code saved to {output_file}")
            else:
                print(f"❌ Error saving: {error}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error optimizing code: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def analyze_complexity(input_file: str) -> bool:
    """Analyze code complexity"""
    logger.info(f"Analyzing complexity of {input_file}...")
    
    try:
        # Load code
        code, error = load_code_from_file(input_file)
        if error:
            print(f"❌ Error loading file: {error}")
            return False
        
        print(f"\n📊 Analyzing complexity...")
        
        # Basic metrics
        metrics = estimate_complexity(code)
        print("\n" + "="*80)
        print("BASIC METRICS:")
        print("="*80)
        for key, value in metrics.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("="*80 + "\n")
        
        # AI analysis
        analyzer = create_agent("Analyzer", Config.AGENT_MESSAGES["complexity_analyzer"])
        analysis = analyzer.generate_reply(
            messages=[{"role": "user", "content": f"Analyze the complexity of this code:\n\n{code}"}]
        )
        
        print("="*80)
        print("AI ANALYSIS:")
        print("="*80)
        print(analysis)
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error analyzing complexity: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI-Powered Intelligent IDE - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate code
  python cli.py generate -p "Implement binary search" -l Python -o binary_search.py
  
  # Debug code
  python cli.py debug -i buggy_code.py -o fixed_code.py
  
  # Generate tests
  python cli.py test -i my_code.py -l Python -o test_my_code.py
  
  # Optimize code
  python cli.py optimize -i code.py -o optimized_code.py
  
  # Analyze complexity
  python cli.py analyze -i code.py
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate code from problem statement')
    gen_parser.add_argument('-p', '--problem', required=True, help='Problem statement')
    gen_parser.add_argument('-l', '--language', required=True, help='Programming language')
    gen_parser.add_argument('-o', '--output', help='Output file path')
    
    # Debug command
    debug_parser = subparsers.add_parser('debug', help='Debug existing code')
    debug_parser.add_argument('-i', '--input', required=True, help='Input file path')
    debug_parser.add_argument('-o', '--output', help='Output file path')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Generate tests for code')
    test_parser.add_argument('-i', '--input', required=True, help='Input file path')
    test_parser.add_argument('-l', '--language', required=True, help='Programming language')
    test_parser.add_argument('-o', '--output', help='Output file path')
    
    # Optimize command
    opt_parser = subparsers.add_parser('optimize', help='Optimize code')
    opt_parser.add_argument('-i', '--input', required=True, help='Input file path')
    opt_parser.add_argument('-o', '--output', help='Output file path')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code complexity')
    analyze_parser.add_argument('-i', '--input', required=True, help='Input file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    success = False
    if args.command == 'generate':
        success = generate_code(args.problem, args.language, args.output)
    elif args.command == 'debug':
        success = debug_code(args.input, args.output)
    elif args.command == 'test':
        success = generate_tests(args.input, args.language, args.output)
    elif args.command == 'optimize':
        success = optimize_code(args.input, args.output)
    elif args.command == 'analyze':
        success = analyze_complexity(args.input)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
