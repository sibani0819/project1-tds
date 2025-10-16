#!/usr/bin/env python3
"""
Complete workflow test for LLM Code Deployment API
Tests the full Build -> Evaluate -> Revise cycle
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "http://localhost:8000"
TEST_SECRET = os.getenv("VERIFICATION_SECRET", "sibani_secret19_key")

def test_complete_workflow():
    """Test the complete Build -> Revise workflow"""
    print("🚀 Testing Complete LLM Code Deployment Workflow")
    print("=" * 60)
    
    # Generate unique identifiers
    task_id = f"test-captcha-solver-{uuid.uuid4().hex[:8]}"
    nonce = uuid.uuid4().hex[:8]
    
    # Round 1: Build Phase
    print("\n📝 ROUND 1: Building Application")
    print("-" * 40)
    
    round1_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "attachments": [
            {
                "name": "sample.png",
                "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
        ]
    }
    
    try:
        print(f"📤 Sending Round 1 request for task: {task_id}")
        response = requests.post(
            f"{BASE_URL}/task",
            json=round1_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Round 1 accepted: {result}")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Round 1 failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Round 1 error: {str(e)}")
        return False
    
    # Wait for processing
    print("\n⏳ Waiting for Round 1 processing...")
    time.sleep(10)
    
    # Round 2: Revise Phase
    print("\n🔄 ROUND 2: Revising Application")
    print("-" * 40)
    
    round2_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 2,
        "nonce": nonce,
        "brief": "Add support for SVG images and improve the captcha solver interface with better error handling",
        "checks": [
            "SVG images are supported",
            "Better error handling is implemented",
            "Interface is more user-friendly",
            "Performance is optimized"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "attachments": [
            {
                "name": "sample.svg",
                "url": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iYmx1ZSIvPjwvc3ZnPg=="
            }
        ]
    }
    
    try:
        print(f"📤 Sending Round 2 request for task: {task_id}")
        response = requests.post(
            f"{BASE_URL}/revise",
            json=round2_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Round 2 accepted: {result}")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Round 2 failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Round 2 error: {str(e)}")
        return False
    
    # Wait for processing
    print("\n⏳ Waiting for Round 2 processing...")
    time.sleep(10)
    
    print("\n🎉 Complete Workflow Test Finished!")
    print("=" * 60)
    print("✅ Both Round 1 and Round 2 requests were accepted")
    print("✅ Background processing is handling the tasks")
    print("✅ GitHub repositories should be created/updated")
    print("✅ Evaluation APIs should be notified")
    
    return True

def test_health_checks():
    """Test health endpoints"""
    print("\n🏥 Testing Health Endpoints")
    print("-" * 40)
    
    try:
        # Test ping
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200:
            print("✅ Ping endpoint working")
        else:
            print("❌ Ping endpoint failed")
            
        # Test health
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check: {health.get('status')}")
            print(f"   GitHub: {health.get('services', {}).get('github')}")
            print(f"   OpenAI: {health.get('services', {}).get('openai')}")
        else:
            print("❌ Health check failed")
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

def test_invalid_requests():
    """Test invalid requests"""
    print("\n🚫 Testing Invalid Requests")
    print("-" * 40)
    
    # Test invalid secret
    invalid_data = {
        "email": "test@example.com",
        "secret": "invalid-secret",
        "task": "test-invalid",
        "round": 1,
        "nonce": "test",
        "brief": "Test brief",
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/task", json=invalid_data)
        if response.status_code == 401:
            print("✅ Invalid secret correctly rejected")
        else:
            print(f"❌ Invalid secret not rejected: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid secret test error: {str(e)}")

if __name__ == "__main__":
    print("🧪 LLM Code Deployment API - Complete Workflow Test")
    print("=" * 60)
    
    # Test health first
    test_health_checks()
    
    # Test invalid requests
    test_invalid_requests()
    
    # Test complete workflow
    success = test_complete_workflow()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Check your GitHub account for new repositories")
        print("2. Verify GitHub Pages are enabled")
        print("3. Test the generated applications")
        print("4. Check the evaluation API notifications")
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
