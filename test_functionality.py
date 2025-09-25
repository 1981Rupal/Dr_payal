#!/usr/bin/env python3
"""
Comprehensive functionality test for Dr. Payal's Hospital CRM
Tests all major components and user roles
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_CREDENTIALS = {
    'superadmin': {'username': 'superadmin', 'password': 'admin123'},
    'doctor': {'username': 'doctor', 'password': 'doctor123'},
    'staff': {'username': 'staff', 'password': 'staff123'}
}

class CRMTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
    
    def log_result(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append(f"{status} {test_name}: {message}")
        print(f"{status} {test_name}: {message}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_result("Health Check", success, f"Status: {data.get('status', 'unknown')}")
            return success
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False
    
    def test_login(self, role):
        """Test login for specific role"""
        try:
            # Get login page first
            response = self.session.get(f"{BASE_URL}/auth/login")
            if response.status_code != 200:
                self.log_result(f"Login Page ({role})", False, "Cannot access login page")
                return False
            
            # Attempt login
            credentials = TEST_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", data=credentials)
            
            # Check if redirected to dashboard (successful login)
            success = response.status_code in [200, 302] and 'dashboard' in response.url
            self.log_result(f"Login ({role})", success, f"Credentials: {credentials['username']}")
            return success
        except Exception as e:
            self.log_result(f"Login ({role})", False, str(e))
            return False
    
    def test_dashboard_access(self, role):
        """Test dashboard access"""
        try:
            response = self.session.get(f"{BASE_URL}/dashboard")
            success = response.status_code == 200
            self.log_result(f"Dashboard Access ({role})", success)
            return success
        except Exception as e:
            self.log_result(f"Dashboard Access ({role})", False, str(e))
            return False
    
    def test_page_access(self, role, page_name, url):
        """Test access to specific pages"""
        try:
            response = self.session.get(f"{BASE_URL}{url}")
            success = response.status_code == 200
            self.log_result(f"{page_name} Access ({role})", success)
            return success
        except Exception as e:
            self.log_result(f"{page_name} Access ({role})", False, str(e))
            return False
    
    def test_api_endpoints(self, role):
        """Test API endpoints"""
        endpoints = [
            ("/api/patients", "Patients API"),
            ("/api/appointments", "Appointments API"),
            ("/api/users", "Users API")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                success = response.status_code in [200, 401, 403]  # 401/403 are valid for unauthorized access
                self.log_result(f"{name} ({role})", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"{name} ({role})", False, str(e))
    
    def test_whatsapp_functionality(self, role):
        """Test WhatsApp functionality (admin only)"""
        if role not in ['superadmin']:
            return
        
        try:
            response = self.session.get(f"{BASE_URL}/test-whatsapp")
            success = response.status_code in [200, 302]  # 302 for redirect after test
            self.log_result(f"WhatsApp Test ({role})", success)
        except Exception as e:
            self.log_result(f"WhatsApp Test ({role})", False, str(e))
    
    def test_role_functionality(self, role):
        """Test functionality for specific role"""
        print(f"\n🔍 Testing {role.upper()} role functionality...")
        
        # Login
        if not self.test_login(role):
            return False
        
        # Dashboard
        self.test_dashboard_access(role)
        
        # Core pages that should work for all roles
        core_pages = [
            ("Patients", "/patients/"),
            ("Appointments Calendar", "/appointments/calendar"),
        ]
        
        for page_name, url in core_pages:
            self.test_page_access(role, page_name, url)
        
        # Role-specific pages
        if role in ['superadmin', 'admin']:
            admin_pages = [
                ("Users Management", "/users"),
                ("Settings", "/settings"),
                ("Reports", "/reports"),
                ("Billing Packages", "/billing/packages")
            ]
            for page_name, url in admin_pages:
                self.test_page_access(role, page_name, url)
        
        # Test API endpoints
        self.test_api_endpoints(role)
        
        # Test WhatsApp (admin only)
        self.test_whatsapp_functionality(role)
        
        # Logout
        try:
            response = self.session.get(f"{BASE_URL}/auth/logout")
            success = response.status_code in [200, 302]
            self.log_result(f"Logout ({role})", success)
        except Exception as e:
            self.log_result(f"Logout ({role})", False, str(e))
        
        return True
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🏥 Dr. Payal's Hospital CRM - Comprehensive Functionality Test")
        print("=" * 60)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed. Application may not be running.")
            return
        
        # Test all user roles
        for role in ['superadmin', 'doctor', 'staff']:
            self.test_role_functionality(role)
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results if "✅ PASS" in result)
        failed = sum(1 for result in self.results if "❌ FAIL" in result)
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        print(f"\n{'🎉 ALL TESTS PASSED!' if failed == 0 else '⚠️  SOME TESTS FAILED'}")
        
        return failed == 0

if __name__ == "__main__":
    tester = CRMTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
