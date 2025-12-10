#!/usr/bin/env python3

import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class LegalMeAPITester:
    def __init__(self, base_url="https://legal-advisor-8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED: {details}")
            self.failed_tests.append({"test": test_name, "error": details})

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200 and "LegalMe API" in response.text
            self.log_result("API Root", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("API Root", False, str(e))
            return False

    def test_get_laws(self):
        """Test laws endpoint"""
        try:
            response = requests.get(f"{self.api_url}/laws", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = isinstance(data, list) and len(data) > 0
                if success and len(data) > 0:
                    # Check if law entries have required fields
                    first_law = data[0]
                    required_fields = ['id', 'title', 'description', 'url']
                    success = all(field in first_law for field in required_fields)
            self.log_result("Get Laws", success, f"Status: {response.status_code}, Laws count: {len(data) if success else 0}")
            return success
        except Exception as e:
            self.log_result("Get Laws", False, str(e))
            return False

    def test_get_topics(self):
        """Test topics endpoint"""
        try:
            response = requests.get(f"{self.api_url}/topics", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = isinstance(data, list) and len(data) == 4
                if success:
                    # Check if topics have required fields
                    required_fields = ['id', 'name', 'icon']
                    success = all(all(field in topic for field in required_fields) for topic in data)
            self.log_result("Get Topics", success, f"Status: {response.status_code}, Topics count: {len(data) if success else 0}")
            return success
        except Exception as e:
            self.log_result("Get Topics", False, str(e))
            return False

    def test_chat_endpoint(self):
        """Test chat functionality"""
        try:
            chat_data = {
                "session_id": self.session_id,
                "message": "What is rental law in Germany?"
            }
            response = requests.post(
                f"{self.api_url}/chat", 
                json=chat_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = 'response' in data and 'session_id' in data
                if success:
                    # Check if response contains expected elements
                    ai_response = data['response']
                    success = (
                        len(ai_response) > 50 and  # Substantial response
                        'Next Steps' in ai_response and  # Required section
                        '<a href=' in ai_response  # HTML links
                    )
            self.log_result("Chat Endpoint", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Chat Endpoint", False, str(e))
            return False

    def test_contract_analysis_no_file(self):
        """Test contract analysis endpoint without file (should fail)"""
        try:
            response = requests.post(f"{self.api_url}/contract/analyze", timeout=10)
            # Should return 422 (validation error) for missing file
            success = response.status_code == 422
            self.log_result("Contract Analysis (No File)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Contract Analysis (No File)", False, str(e))
            return False

    def test_contract_analysis_with_sample_pdf(self):
        """Test contract analysis with a sample PDF"""
        try:
            # Create a simple PDF-like content for testing
            # Note: This is a mock test since we don't have a real PDF
            # In a real scenario, you'd upload an actual PDF file
            
            # For now, let's test the endpoint structure
            files = {'file': ('test.txt', 'This is not a PDF', 'text/plain')}
            response = requests.post(
                f"{self.api_url}/contract/analyze",
                files=files,
                timeout=30
            )
            
            # Should fail because it's not a PDF, but endpoint should be reachable
            success = response.status_code in [400, 422, 500]  # Expected error codes
            self.log_result("Contract Analysis (Invalid File)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Contract Analysis (Invalid File)", False, str(e))
            return False

    def test_get_alternatives(self):
        """Test alternatives endpoint"""
        try:
            response = requests.get(f"{self.api_url}/alternatives/rental", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = 'category' in data and 'resources' in data
                if success:
                    success = isinstance(data['resources'], list) and len(data['resources']) > 0
            self.log_result("Get Alternatives", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Get Alternatives", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting LegalMe Backend API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API Root failed - stopping tests")
            return False
            
        # Test all endpoints
        self.test_get_laws()
        self.test_get_topics()
        self.test_chat_endpoint()
        self.test_contract_analysis_no_file()
        self.test_contract_analysis_with_sample_pdf()
        self.test_get_alternatives()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80  # Consider 80%+ as passing

def main():
    tester = LegalMeAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())