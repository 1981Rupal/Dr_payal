#!/usr/bin/env python3
"""
Test Runner for Hospital CRM System
Runs all tests and generates coverage reports
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def install_test_dependencies():
    """Install test dependencies"""
    dependencies = [
        'pytest>=7.4.3',
        'pytest-flask>=1.3.0',
        'pytest-cov>=4.1.0',
        'coverage>=7.3.0',
        'black>=23.11.0',
        'flake8>=6.1.0',
        'mypy>=1.7.0'
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    return True

def run_linting():
    """Run code linting"""
    print("\n" + "="*60)
    print("RUNNING CODE QUALITY CHECKS")
    print("="*60)
    
    # Black formatting check
    if not run_command("black --check --diff .", "Black formatting check"):
        print("Code formatting issues found. Run 'black .' to fix them.")
        return False
    
    # Flake8 linting
    if not run_command("flake8 --max-line-length=88 --extend-ignore=E203,W503 .", "Flake8 linting"):
        print("Linting issues found. Please fix them before running tests.")
        return False
    
    return True

def run_type_checking():
    """Run type checking with mypy"""
    print("\n" + "="*60)
    print("RUNNING TYPE CHECKING")
    print("="*60)
    
    # Create mypy config if it doesn't exist
    mypy_config = """[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-flask.*]
ignore_missing_imports = True

[mypy-sqlalchemy.*]
ignore_missing_imports = True

[mypy-twilio.*]
ignore_missing_imports = True

[mypy-openai.*]
ignore_missing_imports = True
"""
    
    if not os.path.exists('mypy.ini'):
        with open('mypy.ini', 'w') as f:
            f.write(mypy_config)
    
    return run_command("mypy .", "MyPy type checking")

def run_tests(coverage=True, verbose=False):
    """Run the test suite"""
    print("\n" + "="*60)
    print("RUNNING TEST SUITE")
    print("="*60)
    
    # Base pytest command
    cmd = "pytest"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=. --cov-report=html --cov-report=term-missing"
        cmd += " --cov-exclude=tests/* --cov-exclude=venv/*"
    
    # Add test directory
    cmd += " tests/"
    
    return run_command(cmd, "Running tests with coverage")

def run_specific_test(test_path):
    """Run a specific test file or test function"""
    cmd = f"pytest -v {test_path}"
    return run_command(cmd, f"Running specific test: {test_path}")

def generate_coverage_report():
    """Generate detailed coverage report"""
    print("\n" + "="*60)
    print("GENERATING COVERAGE REPORT")
    print("="*60)
    
    if run_command("coverage html", "Generating HTML coverage report"):
        print("\nCoverage report generated in htmlcov/index.html")
        return True
    return False

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Hospital CRM Test Runner')
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install test dependencies')
    parser.add_argument('--no-lint', action='store_true', 
                       help='Skip linting checks')
    parser.add_argument('--no-type-check', action='store_true', 
                       help='Skip type checking')
    parser.add_argument('--no-coverage', action='store_true', 
                       help='Skip coverage reporting')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose test output')
    parser.add_argument('--test', type=str, 
                       help='Run specific test file or function')
    parser.add_argument('--quick', action='store_true', 
                       help='Quick test run (skip linting and type checking)')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("Hospital CRM Test Runner")
    print("="*60)
    print(f"Working directory: {os.getcwd()}")
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            print("Failed to install test dependencies")
            sys.exit(1)
        print("Test dependencies installed successfully")
    
    # Run specific test if requested
    if args.test:
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    
    # Quick mode - skip quality checks
    if args.quick:
        success = run_tests(coverage=not args.no_coverage, verbose=args.verbose)
        sys.exit(0 if success else 1)
    
    # Full test suite
    all_passed = True
    
    # Code quality checks
    if not args.no_lint:
        if not run_linting():
            all_passed = False
    
    if not args.no_type_check:
        if not run_type_checking():
            print("Type checking failed, but continuing with tests...")
            # Don't fail the entire suite for type checking issues
    
    # Run tests
    if not run_tests(coverage=not args.no_coverage, verbose=args.verbose):
        all_passed = False
    
    # Generate coverage report
    if not args.no_coverage:
        generate_coverage_report()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if all_passed:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Review coverage report in htmlcov/index.html")
        print("2. Fix any issues found in the tests")
        print("3. Add more tests for better coverage")
    else:
        print("❌ Some tests failed!")
        print("\nPlease fix the failing tests before proceeding.")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
