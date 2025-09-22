#!/usr/bin/env python3
"""
Deployment validation script for Hospital CRM
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (missing)")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists"""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"✓ {description}: {dir_path}")
        return True
    else:
        print(f"✗ {description}: {dir_path} (missing)")
        return False

def check_docker_files():
    """Check Docker-related files"""
    print("\n🐳 Docker Configuration:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("Dockerfile", "Production Dockerfile"))
    results.append(check_file_exists("Dockerfile.dev", "Development Dockerfile"))
    results.append(check_file_exists("docker-compose.yml", "Production Docker Compose"))
    results.append(check_file_exists("docker-compose.dev.yml", "Development Docker Compose"))
    results.append(check_file_exists(".dockerignore", "Docker ignore file"))
    
    return all(results)

def check_render_files():
    """Check Render deployment files"""
    print("\n🚀 Render Configuration:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("render.yaml", "Render configuration"))
    results.append(check_file_exists("scripts/render_deploy.sh", "Render deployment script"))
    results.append(check_file_exists("build.sh", "Build script"))
    
    return all(results)

def check_application_files():
    """Check core application files"""
    print("\n🏥 Application Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("app.py", "Basic Flask app"))
    results.append(check_file_exists("app_enhanced.py", "Enhanced Flask app"))
    results.append(check_file_exists("wsgi.py", "WSGI entry point"))
    results.append(check_file_exists("config.py", "Configuration module"))
    results.append(check_file_exists("models.py", "Database models"))
    results.append(check_file_exists("requirements.txt", "Python dependencies"))
    results.append(check_file_exists(".env.example", "Environment template"))
    
    return all(results)

def check_routes():
    """Check route files"""
    print("\n🛣️ Route Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("routes/auth.py", "Authentication routes"))
    results.append(check_file_exists("routes/main.py", "Main routes"))
    results.append(check_file_exists("routes/patients.py", "Patient routes"))
    results.append(check_file_exists("routes/appointments.py", "Appointment routes"))
    results.append(check_file_exists("routes/billing.py", "Billing routes"))
    results.append(check_file_exists("routes/api.py", "API routes"))
    
    return all(results)

def check_templates():
    """Check template files"""
    print("\n🎨 Template Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("templates/base.html", "Base template"))
    results.append(check_file_exists("templates/index.html", "Index template"))
    results.append(check_file_exists("templates/auth/login.html", "Login template"))
    results.append(check_file_exists("templates/patients/list.html", "Patient list template"))
    results.append(check_file_exists("templates/appointments/list.html", "Appointment list template"))
    results.append(check_file_exists("templates/appointments/calendar.html", "Calendar template"))
    results.append(check_file_exists("templates/billing/list.html", "Billing template"))
    
    return all(results)

def check_services():
    """Check service files"""
    print("\n🔧 Service Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("services/whatsapp_service.py", "WhatsApp service"))
    results.append(check_file_exists("services/chatbot_service.py", "Chatbot service"))
    results.append(check_file_exists("services/appointment_service.py", "Appointment service"))
    results.append(check_file_exists("services/billing_service.py", "Billing service"))
    
    return all(results)

def check_utilities():
    """Check utility files"""
    print("\n🛠️ Utility Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("utils/logging_config.py", "Logging configuration"))
    results.append(check_file_exists("utils/backup_system.py", "Backup system"))
    results.append(check_file_exists("utils/security.py", "Security utilities"))
    results.append(check_file_exists("utils/monitoring.py", "Monitoring utilities"))
    
    return all(results)

def check_tests():
    """Check test files"""
    print("\n🧪 Test Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("tests/conftest.py", "Test configuration"))
    results.append(check_file_exists("tests/test_models.py", "Model tests"))
    results.append(check_file_exists("tests/test_auth.py", "Authentication tests"))
    results.append(check_file_exists("tests/test_services.py", "Service tests"))
    results.append(check_file_exists("tests/test_api.py", "API tests"))
    results.append(check_file_exists("tests/test_integration.py", "Integration tests"))
    results.append(check_file_exists("tests/test_performance.py", "Performance tests"))
    results.append(check_file_exists("tests/test_config.py", "Configuration tests"))
    results.append(check_file_exists("pytest.ini", "Pytest configuration"))
    
    return all(results)

def check_scripts():
    """Check script files"""
    print("\n📜 Script Files:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("scripts/run_tests.py", "Test runner"))
    results.append(check_file_exists("scripts/docker_manager.sh", "Docker manager"))
    results.append(check_file_exists("scripts/render_deploy.sh", "Render deploy script"))
    results.append(check_file_exists("migrations_setup.py", "Database setup"))
    
    return all(results)

def check_documentation():
    """Check documentation files"""
    print("\n📚 Documentation:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("README.md", "Main README"))
    results.append(check_file_exists("docs/DEPLOYMENT.md", "Deployment guide"))
    results.append(check_file_exists("docs/API.md", "API documentation"))
    
    return all(results)

def check_monitoring():
    """Check monitoring configuration"""
    print("\n📊 Monitoring Configuration:")
    print("-" * 40)
    
    results = []
    results.append(check_file_exists("monitoring/prometheus.yml", "Prometheus config"))
    results.append(check_file_exists("monitoring/grafana/dashboards/dashboard.yml", "Grafana dashboard"))
    results.append(check_file_exists("monitoring/grafana/datasources/prometheus.yml", "Grafana datasource"))
    
    return all(results)

def check_static_files():
    """Check static file directories"""
    print("\n🎯 Static Files:")
    print("-" * 40)
    
    results = []
    results.append(check_directory_exists("static", "Static directory"))
    results.append(check_directory_exists("static/css", "CSS directory"))
    results.append(check_directory_exists("static/js", "JavaScript directory"))
    results.append(check_directory_exists("static/img", "Images directory"))
    
    return all(results)

def check_configuration_validity():
    """Check configuration file validity"""
    print("\n⚙️ Configuration Validation:")
    print("-" * 40)
    
    try:
        # Check if config.py can be imported
        import config
        print("✓ Configuration module imports successfully")
        
        # Check if all config classes exist
        config_classes = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'RenderConfig']
        for cls_name in config_classes:
            if hasattr(config, cls_name):
                print(f"✓ {cls_name} class exists")
            else:
                print(f"✗ {cls_name} class missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return False

def check_docker_syntax():
    """Check Docker file syntax"""
    print("\n🐳 Docker Syntax Check:")
    print("-" * 40)
    
    try:
        # Check if docker is available
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Docker is available")
            
            # Check Dockerfile syntax by parsing it
            dockerfile_path = os.path.join(project_root, 'Dockerfile')
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()

            # Basic syntax checks
            lines = dockerfile_content.strip().split('\n')
            valid_instructions = [
                'FROM', 'RUN', 'CMD', 'LABEL', 'EXPOSE', 'ENV', 'ADD', 'COPY',
                'ENTRYPOINT', 'VOLUME', 'USER', 'WORKDIR', 'ARG', 'ONBUILD',
                'STOPSIGNAL', 'HEALTHCHECK', 'SHELL'
            ]

            in_continuation = False

            for i, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Handle continuation lines
                if in_continuation:
                    # If this line doesn't end with \, we're done with continuation
                    if not line.endswith('\\'):
                        in_continuation = False
                    continue

                # Check if this line starts a continuation
                if line.endswith('\\'):
                    in_continuation = True

                # Extract instruction (first word)
                parts = line.split()
                if parts:
                    instruction = parts[0].upper()
                    if instruction not in valid_instructions:
                        print(f"✗ Dockerfile syntax error at line {i}: Unknown instruction '{instruction}'")
                        return False

            print("✓ Dockerfile syntax appears valid")
            return True
        else:
            print("⚠ Docker not available, skipping syntax check")
            return True
            
    except FileNotFoundError:
        print("⚠ Docker not found, skipping syntax check")
        return True
    except Exception as e:
        print(f"✗ Docker syntax check failed: {e}")
        return False

def check_python_syntax():
    """Check Python file syntax"""
    print("\n🐍 Python Syntax Check:")
    print("-" * 40)
    
    python_files = [
        "app.py",
        "app_enhanced.py",
        "config.py",
        "models.py",
        "wsgi.py"
    ]
    
    results = []
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✓ {file_path} syntax is valid")
                results.append(True)
            except SyntaxError as e:
                print(f"✗ {file_path} syntax error: {e}")
                results.append(False)
        else:
            print(f"⚠ {file_path} not found")
            results.append(True)  # Don't fail for missing files
    
    return all(results)

def generate_validation_report():
    """Generate comprehensive validation report"""
    print("🏥 Hospital CRM Deployment Validation")
    print("=" * 60)
    
    checks = [
        ("Application Files", check_application_files),
        ("Route Files", check_routes),
        ("Template Files", check_templates),
        ("Service Files", check_services),
        ("Utility Files", check_utilities),
        ("Test Files", check_tests),
        ("Script Files", check_scripts),
        ("Documentation", check_documentation),
        ("Monitoring Config", check_monitoring),
        ("Static Files", check_static_files),
        ("Docker Files", check_docker_files),
        ("Render Files", check_render_files),
        ("Configuration", check_configuration_validity),
        ("Python Syntax", check_python_syntax),
        ("Docker Syntax", check_docker_syntax),
    ]
    
    results = {}
    total_checks = len(checks)
    passed_checks = 0
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if result:
                passed_checks += 1
        except Exception as e:
            print(f"✗ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {check_name}")
    
    print(f"\nTotal Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Success Rate: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        print("✅ The Hospital CRM system is ready for deployment!")
        return True
    else:
        print(f"\n❌ {total_checks - passed_checks} VALIDATION CHECKS FAILED")
        print("⚠️  Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = generate_validation_report()
    sys.exit(0 if success else 1)
