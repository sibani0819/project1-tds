#!/usr/bin/env python3
"""
Test Current Configuration Script
This script tests the current configuration without requiring all tokens.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_basic_config():
    """Test basic configuration."""
    print("🧪 Testing Current Configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Check verification secret
    verification_secret = os.getenv('VERIFICATION_SECRET')
    if verification_secret and verification_secret != 'your_verification_secret_here':
        print(f"✅ Verification secret configured: {verification_secret[:10]}...")
    else:
        print("❌ Verification secret not configured")
        return False
    
    # Check GitHub username
    github_username = os.getenv('GITHUB_USERNAME')
    if github_username and github_username != 'your_github_username_here':
        print(f"✅ GitHub username configured: {github_username}")
    else:
        print("❌ GitHub username not configured")
        return False
    
    # Check GitHub PAT (optional for basic test)
    github_pat = os.getenv('GITHUB_PAT')
    if github_pat and github_pat != 'your_github_token_here':
        print(f"✅ GitHub PAT configured: {github_pat[:10]}...")
        
        # Test GitHub connection
        try:
            from github import Github
            g = Github(github_pat)
            user = g.get_user()
            print(f"✅ GitHub connection successful - User: {user.login}")
        except Exception as e:
            print(f"⚠️  GitHub connection failed: {str(e)}")
            print("   This is expected if you haven't added your token yet")
    else:
        print("⚠️  GitHub PAT not configured (this is expected)")
        print("   You'll need to add your GitHub token to test GitHub integration")
    
    return True

def test_application_startup():
    """Test if the application can start without errors."""
    print("\n🚀 Testing Application Startup...")
    print("=" * 50)
    
    try:
        # Test syntax
        import py_compile
        py_compile.compile('main.py', doraise=True)
        print("✅ Python syntax check passed")
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error: {e}")
        return False
    
    # Test imports
    try:
        import fastapi
        import uvicorn
        import github
        import openai
        print("✅ All required packages imported successfully")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    return True

def show_next_steps():
    """Show next steps for the user."""
    print("\n📋 Next Steps:")
    print("=" * 50)
    print("1. 🔑 Add GitHub Personal Access Token:")
    print("   • Go to: https://github.com/settings/tokens")
    print("   • Generate new token with scopes: repo, public_repo, admin:repo_hook, workflow")
    print("   • Update GITHUB_PAT in .env file")
    
    print("\n2. 🚀 Start the application:")
    print("   • python main.py")
    print("   • Or: python build_and_deploy.py")
    
    print("\n3. 🧪 Test the application:")
    print("   • python test_api.py")
    print("   • python test_complete_workflow.py")
    
    print("\n4. 🌐 Access your applications:")
    print("   • Local API: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    
    print("\n5. 🔗 Your GitHub Pages URLs:")
    print("   • https://sibani0819.github.io/llm-project-test-captcha-solver-11536b70-31627fe0")
    print("   • https://sibani0819.github.io/llm-project-test-captcha-solver-b821db72-043fa67a")
    print("   • https://sibani0819.github.io/llm-project-test-captcha-solver-3ebf2ef2-5916fdff")

def main():
    """Main test function."""
    print("🔧 LLM Code Deployment - Configuration Test")
    print("=" * 60)
    
    # Test basic config
    if not test_basic_config():
        print("\n❌ Basic configuration test failed")
        return False
    
    # Test application startup
    if not test_application_startup():
        print("\n❌ Application startup test failed")
        return False
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Configuration test completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
