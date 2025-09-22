#!/usr/bin/env python3
"""
Comprehensive test runner for Hospital CRM
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ {description} completed successfully in {duration:.2f}s")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✗ {description} failed after {duration:.2f}s")
        print(f"Exit code: {e.returncode}")
        
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        
        return False

def setup_test_environment():
    """Setup test environment"""
    print("Setting up test environment...")
    
    # Set test environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['WTF_CSRF_ENABLED'] = 'false'
    
    # Create test directories
    test_dirs = ['logs', 'uploads', 'static/uploads']
    for dir_name in test_dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✓ Test environment setup completed")

def run_unit_tests():
    """Run unit tests"""
    commands = [
        ("python -m pytest tests/test_models.py -v", "Model Tests"),
        ("python -m pytest tests/test_auth.py -v", "Authentication Tests"),
        ("python -m pytest tests/test_services.py -v", "Service Tests"),
        ("python -m pytest tests/test_config.py -v", "Configuration Tests"),
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    return results

def run_api_tests():
    """Run API tests"""
    command = "python -m pytest tests/test_api.py -v"
    success = run_command(command, "API Tests")
    return [("API Tests", success)]

def run_integration_tests():
    """Run integration tests"""
    command = "python -m pytest tests/test_integration.py -v"
    success = run_command(command, "Integration Tests")
    return [("Integration Tests", success)]

def run_performance_tests():
    """Run performance tests"""
    command = "python -m pytest tests/test_performance.py -v -s"
    success = run_command(command, "Performance Tests")
    return [("Performance Tests", success)]

def run_coverage_tests():
    """Run tests with coverage"""
    commands = [
        ("python -m pytest --cov=. --cov-report=html --cov-report=term", "Coverage Tests"),
        ("python -m coverage report", "Coverage Report")
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    return results

def run_linting():
    """Run code linting"""
    commands = [
        ("python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Critical Linting"),
        ("python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics", "Full Linting"),
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    return results

def run_security_tests():
    """Run security tests"""
    commands = [
        ("python -m bandit -r . -f json -o bandit-report.json", "Security Scan (Bandit)"),
        ("python -m safety check", "Dependency Security Check"),
    ]
    
    results = []
    for command, description in commands:
        # Security tools might not be installed, so don't fail if they're missing
        try:
            success = run_command(command, description)
            results.append((description, success))
        except Exception as e:
            print(f"⚠ {description} skipped: {e}")
            results.append((description, None))
    
    return results

def run_docker_tests():
    """Run Docker-related tests"""
    commands = [
        ("docker --version", "Docker Version Check"),
        ("docker-compose --version", "Docker Compose Version Check"),
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    # Test Docker build if Docker is available
    if all(result[1] for result in results):
        build_command = "docker build -t hospital-crm-test ."
        success = run_command(build_command, "Docker Build Test")
        results.append(("Docker Build Test", success))
    
    return results

def generate_test_report(all_results):
    """Generate a comprehensive test report"""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST REPORT")
    print(f"{'='*80}")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category}:")
        print("-" * len(category))
        
        for test_name, status in results:
            total_tests += 1
            
            if status is True:
                print(f"  ✓ {test_name}")
                passed_tests += 1
            elif status is False:
                print(f"  ✗ {test_name}")
                failed_tests += 1
            else:
                print(f"  ⚠ {test_name} (skipped)")
                skipped_tests += 1
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Skipped: {skipped_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n❌ {failed_tests} TESTS FAILED")
        return False

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Hospital CRM Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--coverage", action="store_true", help="Run coverage tests")
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--docker", action="store_true", help="Run Docker tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only (unit + API)")
    
    args = parser.parse_args()
    
    # Setup test environment
    setup_test_environment()
    
    all_results = {}
    
    # Determine which tests to run
    if args.unit or args.all or (not any([args.api, args.integration, args.performance, args.coverage, args.lint, args.security, args.docker, args.quick])):
        all_results["Unit Tests"] = run_unit_tests()
    
    if args.api or args.all or args.quick:
        all_results["API Tests"] = run_api_tests()
    
    if args.integration or args.all:
        all_results["Integration Tests"] = run_integration_tests()
    
    if args.performance or args.all:
        all_results["Performance Tests"] = run_performance_tests()
    
    if args.coverage or args.all:
        all_results["Coverage Tests"] = run_coverage_tests()
    
    if args.lint or args.all:
        all_results["Code Linting"] = run_linting()
    
    if args.security or args.all:
        all_results["Security Tests"] = run_security_tests()
    
    if args.docker or args.all:
        all_results["Docker Tests"] = run_docker_tests()
    
    # Generate comprehensive report
    success = generate_test_report(all_results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
