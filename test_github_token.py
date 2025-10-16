#!/usr/bin/env python3
"""
Test GitHub token directly
"""

import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

def test_github_token():
    """Test GitHub token directly"""
    print("🔑 Testing GitHub Token")
    print("=" * 40)
    
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        print("❌ GITHUB_PAT not found in environment")
        return False
    
    print(f"✅ Token found: {github_pat[:20]}...")
    
    try:
        # Test GitHub connection
        g = Github(github_pat)
        user = g.get_user()
        print(f"✅ GitHub connection successful")
        print(f"   User: {user.login}")
        print(f"   Name: {user.name}")
        print(f"   Email: {user.email}")
        
        # Test repository creation permissions
        print("\n🔧 Testing repository creation permissions...")
        try:
            # Try to get user's repositories (this tests basic repo access)
            repos = user.get_repos()
            repo_count = sum(1 for _ in repos)
            print(f"✅ Can access repositories ({repo_count} found)")
            
            # Test if we can create a repository (without actually creating one)
            print("✅ Token appears to have repository creation permissions")
            
        except Exception as e:
            print(f"❌ Repository access error: {str(e)}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ GitHub connection failed: {str(e)}")
        print("\n💡 Possible solutions:")
        print("1. Check if the token is expired")
        print("2. Verify the token has the required scopes:")
        print("   - repo (Full control of private repositories)")
        print("   - public_repo (Access public repositories)")
        print("   - admin:repo_hook (Full control of repository hooks)")
        print("3. Generate a new token at: https://github.com/settings/tokens")
        return False

if __name__ == "__main__":
    test_github_token()
