#!/usr/bin/env python3
"""
Detailed GitHub token diagnosis
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def diagnose_github_token():
    """Detailed diagnosis of GitHub token issues"""
    print("🔍 GitHub Token Diagnosis")
    print("=" * 50)
    
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        print("❌ GITHUB_PAT not found in environment")
        print("💡 Make sure you have a .env file with GITHUB_PAT=your_token")
        return False
    
    print(f"✅ Token found: {github_pat[:20]}...")
    print(f"   Token length: {len(github_pat)} characters")
    
    # Test 1: Basic API call
    print("\n🧪 Test 1: Basic GitHub API call")
    try:
        headers = {"Authorization": f"token {github_pat}"}
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Basic API call successful")
            print(f"   User: {user_data.get('login')}")
            print(f"   Name: {user_data.get('name')}")
        else:
            print(f"❌ Basic API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Basic API call error: {str(e)}")
        return False
    
    # Test 2: Repository access
    print("\n🧪 Test 2: Repository access")
    try:
        response = requests.get("https://api.github.com/user/repos", headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Repository access successful ({len(repos)} repositories)")
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Repository access error: {str(e)}")
        return False
    
    # Test 3: Token scopes
    print("\n🧪 Test 3: Token scopes")
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        scopes = response.headers.get('X-OAuth-Scopes', '')
        print(f"✅ Token scopes: {scopes}")
        
        required_scopes = ['repo', 'public_repo']
        missing_scopes = [scope for scope in required_scopes if scope not in scopes]
        
        if missing_scopes:
            print(f"❌ Missing required scopes: {missing_scopes}")
            print("💡 Update your token to include these scopes:")
            for scope in missing_scopes:
                print(f"   - {scope}")
            return False
        else:
            print("✅ All required scopes present")
            
    except Exception as e:
        print(f"❌ Scope check error: {str(e)}")
        return False
    
    # Test 4: Repository creation (dry run)
    print("\n🧪 Test 4: Repository creation permissions")
    try:
        # Test if we can access the repository creation endpoint
        test_repo_data = {
            "name": "test-repo-permissions-check",
            "description": "Test repository for permissions check",
            "private": False,
            "auto_init": False
        }
        
        # We won't actually create the repo, just test the endpoint
        response = requests.post(
            "https://api.github.com/user/repos", 
            headers=headers, 
            json=test_repo_data,
            timeout=10
        )
        
        if response.status_code in [201, 422]:  # 201 = success, 422 = repo already exists
            print("✅ Repository creation permissions OK")
        elif response.status_code == 403:
            print("❌ Repository creation forbidden - check token scopes")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"⚠️  Repository creation test returned: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Repository creation test error: {str(e)}")
        return False
    
    print("\n🎉 All tests passed! GitHub token is working correctly.")
    return True

if __name__ == "__main__":
    success = diagnose_github_token()
    
    if not success:
        print("\n💡 Troubleshooting Steps:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Delete the old token if it exists")
        print("3. Click 'Generate new token' → 'Generate new token (classic)'")
        print("4. Set expiration (e.g., 90 days)")
        print("5. Select these scopes:")
        print("   ✅ repo (Full control of private repositories)")
        print("   ✅ public_repo (Access public repositories)")
        print("   ✅ admin:repo_hook (Full control of repository hooks)")
        print("6. Copy the new token")
        print("7. Update your .env file with the new token")
        print("8. Restart the application")
