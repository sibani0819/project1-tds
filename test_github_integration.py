#!/usr/bin/env python3
"""
Test GitHub integration without LLM dependency
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_SECRET = "sibani_secret19_key"

def test_github_direct():
    """Test GitHub integration directly"""
    print("🔧 Testing GitHub Integration Directly")
    print("=" * 50)
    
    # Test with a simple request that should work
    task_id = f"test-github-{uuid.uuid4().hex[:8]}"
    nonce = uuid.uuid4().hex[:8]
    
    test_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": "Create a simple HTML page with a title and basic content",
        "checks": [
            "Page has a title",
            "Page displays content",
            "Page is responsive"
        ],
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        print(f"📤 Sending test request for task: {task_id}")
        response = requests.post(
            f"{BASE_URL}/task",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request accepted: {result}")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Status: {result.get('status')}")
            print("\n⏳ The task will fail at LLM generation due to quota limits,")
            print("   but you can check the logs to see the GitHub integration attempt.")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return False

def test_github_health():
    """Test GitHub connectivity"""
    print("\n🏥 Testing GitHub Health")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            github_status = health.get('services', {}).get('github')
            print(f"GitHub Status: {github_status}")
            
            if "connected" in github_status:
                print("✅ GitHub is connected and ready")
                return True
            else:
                print("❌ GitHub connection issue")
                return False
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 GitHub Integration Test")
    print("=" * 50)
    
    # Test GitHub health first
    github_ok = test_github_health()
    
    if github_ok:
        # Test GitHub integration
        test_github_direct()
        
        print("\n📋 What's happening:")
        print("1. ✅ API accepts the request")
        print("2. ✅ Background processing starts")
        print("3. ❌ LLM generation fails (quota limit)")
        print("4. ❌ GitHub repo creation never happens")
        print("\n💡 To fix this:")
        print("- Add OpenAI API credits to your account")
        print("- Or use a different OpenAI API key with credits")
        print("- The GitHub integration will work once LLM generation succeeds")
    else:
        print("❌ GitHub connection issue - check your GITHUB_PAT")
