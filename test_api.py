#!/usr/bin/env python3
"""
Test script for LLM Code Deployment API
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "http://localhost:8000"
TEST_SECRET = os.getenv("VERIFICATION_SECRET", "test-secret-123")

def test_ping():
    """Test the ping endpoint."""
    print("Testing /ping endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200:
            print("✅ Ping successful:", response.json())
            return True
        else:
            print("❌ Ping failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Ping error:", str(e))
        return False

def test_health():
    """Test the health endpoint."""
    print("\nTesting /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check successful:")
            print(f"   Status: {health_data.get('status')}")
            print(f"   GitHub: {health_data.get('services', {}).get('github')}")
            print(f"   OpenAI: {health_data.get('services', {}).get('openai')}")
            return True
        else:
            print("❌ Health check failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Health check error:", str(e))
        return False

def test_task_creation():
    """Test task creation endpoint."""
    print("\nTesting /task endpoint...")
    
    task_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": "test-app-123",
        "round": 1,
        "nonce": "test-nonce-123",
        "brief": "Create a simple calculator application with basic arithmetic operations",
        "checks": [
            "Application is responsive",
            "Calculator performs basic operations",
            "UI is user-friendly"
        ],
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/task",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Task creation successful:")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Task ID: {result.get('task_id')}")
            return True
        else:
            print("❌ Task creation failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Task creation error:", str(e))
        return False

def test_revision():
    """Test revision endpoint."""
    print("\nTesting /revise endpoint...")
    
    revision_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": "test-app-123",
        "round": 2,
        "nonce": "test-nonce-123",
        "brief": "Add scientific calculator functions and improve the design",
        "checks": [
            "Scientific functions work",
            "Design is improved",
            "Performance is optimized"
        ],
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/revise",
            json=revision_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Revision successful:")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Task ID: {result.get('task_id')}")
            return True
        else:
            print("❌ Revision failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Revision error:", str(e))
        return False

def test_invalid_secret():
    """Test with invalid secret."""
    print("\nTesting invalid secret...")
    
    task_data = {
        "email": "test@example.com",
        "secret": "invalid-secret",
        "task": "test-app-456",
        "round": 1,
        "nonce": "test-nonce-456",
        "brief": "Test brief",
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/task",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            print("✅ Invalid secret correctly rejected")
            return True
        else:
            print("❌ Invalid secret not rejected:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Invalid secret test error:", str(e))
        return False

def main():
    """Run all tests."""
    print("🚀 Starting LLM Code Deployment API Tests")
    print("=" * 50)
    
    tests = [
        test_ping,
        test_health,
        test_invalid_secret,
        test_task_creation,
        test_revision
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
