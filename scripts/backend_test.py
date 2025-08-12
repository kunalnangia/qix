#!/usr/bin/env python3
"""
Comprehensive Backend Testing for IntelliTest AI Automation Platform
Tests all backend components including database, authentication, AI services, WebSocket, and API endpoints.
"""

import asyncio
import json
import requests
import websockets
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test configuration
BACKEND_URL = "https://fc5ff279-e1c6-4df7-8c71-e9eef6e672b2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"
WS_BASE = BACKEND_URL.replace("https://", "wss://") + "/api/ws"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_project_id = None
        self.test_case_id = None
        self.test_execution_id = None
        self.test_comment_id = None
        self.results = {}
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.results[test_name] = {
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if not success and details:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{API_BASE}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                return self.session.get(url, headers=request_headers, params=data)
            elif method.upper() == "POST":
                return self.session.post(url, headers=request_headers, json=data)
            elif method.upper() == "PUT":
                return self.session.put(url, headers=request_headers, json=data)
            elif method.upper() == "DELETE":
                return self.session.delete(url, headers=request_headers)
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = self.make_request("GET", "/health")
            if response and response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_test("Health Check", True, "Backend is healthy")
                    return True
                else:
                    self.log_test("Health Check", False, "Invalid health response", data)
            else:
                self.log_test("Health Check", False, f"Health check failed with status {response.status_code if response else 'No response'}")
        except Exception as e:
            self.log_test("Health Check", False, f"Health check error: {str(e)}")
        return False
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            user_data = {
                "email": "sarah.johnson@intellitest.com",
                "full_name": "Sarah Johnson",
                "password": "SecurePass123!"
            }
            
            response = self.make_request("POST", "/auth/register", user_data)
            if response and response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_test("User Registration", True, f"User registered successfully: {data['user']['email']}")
                    return True
                else:
                    self.log_test("User Registration", False, "Invalid registration response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("User Registration", False, f"Registration failed: {error_msg}")
        except Exception as e:
            self.log_test("User Registration", False, f"Registration error: {str(e)}")
        return False
    
    def test_user_login(self):
        """Test user login"""
        try:
            login_data = {
                "email": "sarah.johnson@intellitest.com",
                "password": "SecurePass123!"
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            if response and response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_test("User Login", True, f"User logged in successfully: {data['user']['email']}")
                    return True
                else:
                    self.log_test("User Login", False, "Invalid login response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("User Login", False, f"Login failed: {error_msg}")
        except Exception as e:
            self.log_test("User Login", False, f"Login error: {str(e)}")
        return False
    
    def test_get_current_user(self):
        """Test getting current user info"""
        try:
            response = self.make_request("GET", "/auth/me")
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test("Get Current User", True, f"Retrieved user info: {data['email']}")
                    return True
                else:
                    self.log_test("Get Current User", False, "Invalid user info response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Get Current User", False, f"Get user info failed: {error_msg}")
        except Exception as e:
            self.log_test("Get Current User", False, f"Get user info error: {str(e)}")
        return False
    
    def test_create_project(self):
        """Test project creation"""
        try:
            project_data = {
                "name": "E-Commerce Platform Testing",
                "description": "Comprehensive testing suite for our e-commerce platform including payment processing, user management, and inventory systems."
            }
            
            response = self.make_request("POST", "/projects", project_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "name" in data:
                    self.test_project_id = data["id"]
                    self.log_test("Create Project", True, f"Project created: {data['name']}")
                    return True
                else:
                    self.log_test("Create Project", False, "Invalid project creation response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Create Project", False, f"Project creation failed: {error_msg}")
        except Exception as e:
            self.log_test("Create Project", False, f"Project creation error: {str(e)}")
        return False
    
    def test_get_projects(self):
        """Test getting user projects"""
        try:
            response = self.make_request("GET", "/projects")
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Projects", True, f"Retrieved {len(data)} projects")
                    return True
                else:
                    self.log_test("Get Projects", False, "No projects found or invalid response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Get Projects", False, f"Get projects failed: {error_msg}")
        except Exception as e:
            self.log_test("Get Projects", False, f"Get projects error: {str(e)}")
        return False
    
    def test_create_test_case(self):
        """Test test case creation"""
        try:
            test_case_data = {
                "title": "User Login Functionality Test",
                "description": "Verify that users can successfully log into the system with valid credentials and receive appropriate error messages for invalid attempts.",
                "project_id": self.test_project_id,
                "test_type": "functional",
                "priority": "high",
                "status": "active",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Navigate to the login page",
                        "expected_result": "Login form is displayed with email and password fields"
                    },
                    {
                        "step_number": 2,
                        "description": "Enter valid email and password",
                        "expected_result": "Credentials are accepted and form is ready for submission"
                    },
                    {
                        "step_number": 3,
                        "description": "Click the login button",
                        "expected_result": "User is successfully logged in and redirected to dashboard"
                    }
                ],
                "expected_result": "User successfully logs in and accesses the dashboard",
                "tags": ["authentication", "login", "security"],
                "prerequisites": "User account must exist in the system",
                "test_data": {
                    "valid_email": "test@example.com",
                    "valid_password": "TestPass123!",
                    "invalid_email": "invalid@example.com"
                }
            }
            
            response = self.make_request("POST", "/test-cases", test_case_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.test_case_id = data["id"]
                    self.log_test("Create Test Case", True, f"Test case created: {data['title']}")
                    return True
                else:
                    self.log_test("Create Test Case", False, "Invalid test case creation response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Create Test Case", False, f"Test case creation failed: {error_msg}")
        except Exception as e:
            self.log_test("Create Test Case", False, f"Test case creation error: {str(e)}")
        return False
    
    def test_get_test_cases(self):
        """Test getting test cases"""
        try:
            response = self.make_request("GET", "/test-cases", {"project_id": self.test_project_id})
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Test Cases", True, f"Retrieved {len(data)} test cases")
                    return True
                else:
                    self.log_test("Get Test Cases", False, "No test cases found or invalid response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Get Test Cases", False, f"Get test cases failed: {error_msg}")
        except Exception as e:
            self.log_test("Get Test Cases", False, f"Get test cases error: {str(e)}")
        return False
    
    def test_update_test_case(self):
        """Test test case update"""
        try:
            update_data = {
                "description": "Updated: Comprehensive test for user login functionality including edge cases and security validations.",
                "priority": "critical",
                "tags": ["authentication", "login", "security", "critical-path"]
            }
            
            response = self.make_request("PUT", f"/test-cases/{self.test_case_id}", update_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and data["priority"] == "critical":
                    self.log_test("Update Test Case", True, f"Test case updated successfully")
                    return True
                else:
                    self.log_test("Update Test Case", False, "Invalid test case update response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Update Test Case", False, f"Test case update failed: {error_msg}")
        except Exception as e:
            self.log_test("Update Test Case", False, f"Test case update error: {str(e)}")
        return False
    
    def test_create_comment(self):
        """Test comment creation"""
        try:
            comment_data = {
                "test_case_id": self.test_case_id,
                "comment_type": "suggestion",
                "content": "Consider adding additional test scenarios for password complexity validation and account lockout mechanisms."
            }
            
            response = self.make_request("POST", "/comments", comment_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "content" in data:
                    self.test_comment_id = data["id"]
                    self.log_test("Create Comment", True, f"Comment created successfully")
                    return True
                else:
                    self.log_test("Create Comment", False, "Invalid comment creation response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Create Comment", False, f"Comment creation failed: {error_msg}")
        except Exception as e:
            self.log_test("Create Comment", False, f"Comment creation error: {str(e)}")
        return False
    
    def test_get_comments(self):
        """Test getting comments"""
        try:
            response = self.make_request("GET", f"/comments/{self.test_case_id}")
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Get Comments", True, f"Retrieved {len(data)} comments")
                    return True
                else:
                    self.log_test("Get Comments", False, "No comments found or invalid response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Get Comments", False, f"Get comments failed: {error_msg}")
        except Exception as e:
            self.log_test("Get Comments", False, f"Get comments error: {str(e)}")
        return False
    
    def test_create_test_execution(self):
        """Test test execution creation"""
        try:
            execution_data = {
                "test_case_id": self.test_case_id
            }
            
            response = self.make_request("POST", "/executions", execution_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "test_case_id" in data:
                    self.test_execution_id = data["id"]
                    self.log_test("Create Test Execution", True, f"Test execution created successfully")
                    return True
                else:
                    self.log_test("Create Test Execution", False, "Invalid test execution creation response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Create Test Execution", False, f"Test execution creation failed: {error_msg}")
        except Exception as e:
            self.log_test("Create Test Execution", False, f"Test execution creation error: {str(e)}")
        return False
    
    def test_update_execution_status(self):
        """Test execution status update"""
        try:
            response = self.make_request("PUT", f"/executions/{self.test_execution_id}/status", {"status": "completed"})
            if response and response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Update Execution Status", True, f"Execution status updated successfully")
                    return True
                else:
                    self.log_test("Update Execution Status", False, "Invalid execution status update response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Update Execution Status", False, f"Execution status update failed: {error_msg}")
        except Exception as e:
            self.log_test("Update Execution Status", False, f"Execution status update error: {str(e)}")
        return False
    
    def test_ai_generate_tests(self):
        """Test AI test generation"""
        try:
            ai_request = {
                "project_id": self.test_project_id,
                "prompt": "Generate comprehensive test cases for user registration functionality including email validation, password strength requirements, and duplicate account prevention.",
                "test_type": "functional",
                "priority": "high",
                "count": 2
            }
            
            response = self.make_request("POST", "/ai/generate-tests", ai_request)
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("AI Generate Tests", True, f"Generated {len(data)} test cases using AI")
                    return True
                else:
                    self.log_test("AI Generate Tests", False, "No test cases generated or invalid response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("AI Generate Tests", False, f"AI test generation failed: {error_msg}")
        except Exception as e:
            self.log_test("AI Generate Tests", False, f"AI test generation error: {str(e)}")
        return False
    
    def test_ai_debug_test(self):
        """Test AI test debugging"""
        try:
            debug_request = {
                "test_case_id": self.test_case_id,
                "execution_id": self.test_execution_id,
                "error_description": "Login test failed with timeout error when clicking submit button",
                "logs": "ERROR: Element not found - submit button selector '#login-submit' timed out after 30 seconds"
            }
            
            response = self.make_request("POST", "/ai/debug-test", debug_request)
            if response and response.status_code == 200:
                data = response.json()
                if "analysis" in data and "suggestions" in data:
                    self.log_test("AI Debug Test", True, f"AI debugging completed successfully")
                    return True
                else:
                    self.log_test("AI Debug Test", False, "Invalid AI debugging response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("AI Debug Test", False, f"AI debugging failed: {error_msg}")
        except Exception as e:
            self.log_test("AI Debug Test", False, f"AI debugging error: {str(e)}")
        return False
    
    def test_ai_prioritize_tests(self):
        """Test AI test prioritization"""
        try:
            prioritization_request = {
                "project_id": self.test_project_id,
                "context": "Critical release deployment - focus on core user authentication and payment processing functionality",
                "test_case_ids": [self.test_case_id]
            }
            
            response = self.make_request("POST", "/ai/prioritize-tests", prioritization_request)
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("AI Prioritize Tests", True, f"AI prioritization completed for {len(data)} test cases")
                    return True
                else:
                    self.log_test("AI Prioritize Tests", False, "No prioritized tests or invalid response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("AI Prioritize Tests", False, f"AI prioritization failed: {error_msg}")
        except Exception as e:
            self.log_test("AI Prioritize Tests", False, f"AI prioritization error: {str(e)}")
        return False
    
    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        try:
            response = self.make_request("GET", "/dashboard/stats")
            if response and response.status_code == 200:
                data = response.json()
                if "total_test_cases" in data and "total_executions" in data:
                    self.log_test("Dashboard Stats", True, f"Dashboard stats retrieved successfully")
                    return True
                else:
                    self.log_test("Dashboard Stats", False, "Invalid dashboard stats response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Dashboard Stats", False, f"Dashboard stats failed: {error_msg}")
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Dashboard stats error: {str(e)}")
        return False
    
    def test_activity_feed(self):
        """Test activity feed"""
        try:
            response = self.make_request("GET", "/dashboard/activity")
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Activity Feed", True, f"Activity feed retrieved with {len(data)} activities")
                    return True
                else:
                    self.log_test("Activity Feed", False, "Invalid activity feed response", data)
            else:
                error_msg = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Activity Feed", False, f"Activity feed failed: {error_msg}")
        except Exception as e:
            self.log_test("Activity Feed", False, f"Activity feed error: {str(e)}")
        return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        try:
            if not self.test_user_id:
                self.log_test("WebSocket Connection", False, "No user ID available for WebSocket test")
                return False
            
            ws_url = f"{WS_BASE}/{self.test_user_id}"
            
            async with websockets.connect(ws_url) as websocket:
                # Test connection
                await asyncio.sleep(1)  # Wait for connection confirmation
                
                # Test joining a room
                join_message = {
                    "type": "join_room",
                    "room_id": f"project_{self.test_project_id}"
                }
                await websocket.send(json.dumps(join_message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    if data.get("type") == "room_joined":
                        self.log_test("WebSocket Connection", True, "WebSocket connection and room joining successful")
                        return True
                    else:
                        self.log_test("WebSocket Connection", False, "Unexpected WebSocket response", data)
                except asyncio.TimeoutError:
                    self.log_test("WebSocket Connection", False, "WebSocket response timeout")
                
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"WebSocket connection error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting IntelliTest AI Backend Testing...")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Create Project", self.test_create_project),
            ("Get Projects", self.test_get_projects),
            ("Create Test Case", self.test_create_test_case),
            ("Get Test Cases", self.test_get_test_cases),
            ("Update Test Case", self.test_update_test_case),
            ("Create Comment", self.test_create_comment),
            ("Get Comments", self.test_get_comments),
            ("Create Test Execution", self.test_create_test_execution),
            ("Update Execution Status", self.test_update_execution_status),
            ("AI Generate Tests", self.test_ai_generate_tests),
            ("AI Debug Test", self.test_ai_debug_test),
            ("AI Prioritize Tests", self.test_ai_prioritize_tests),
            ("Dashboard Stats", self.test_dashboard_stats),
            ("Activity Feed", self.test_activity_feed),
        ]
        
        # Run synchronous tests
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            test_func()
        
        # Run WebSocket test
        print(f"\n🧪 Running WebSocket Connection...")
        asyncio.run(self.test_websocket_connection())
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results.values() if result["success"])
        total = len(self.results)
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for test_name, result in self.results.items():
                if not result["success"]:
                    print(f"   • {test_name}: {result['message']}")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    tester = BackendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()