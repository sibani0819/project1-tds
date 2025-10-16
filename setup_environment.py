#!/usr/bin/env python3
"""
Environment Setup Script for LLM Code Deployment Project
This script helps you set up the required environment variables.
"""

import os
import secrets
import string

def generate_secret(length=32):
    """Generate a secure random secret."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create .env file with template values."""
    print("🔧 Setting up Environment Variables...")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists. Backing up to .env.backup")
        if os.path.exists('.env.backup'):
            os.remove('.env.backup')
        os.rename('.env', '.env.backup')
    
    # Generate a secure verification secret
    verification_secret = generate_secret(32)
    
    env_content = f"""# LLM Code Deployment Environment Variables
# Generated on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# GitHub Personal Access Token (REQUIRED)
# Get from: https://github.com/settings/tokens
# Required scopes: repo, public_repo, admin:repo_hook, workflow
GITHUB_PAT=your_github_token_here

# Verification Secret (REQUIRED)
# Auto-generated secure secret
VERIFICATION_SECRET={verification_secret}

# LLM API Key (OPTIONAL - for OpenAI)
# Get from: https://platform.openai.com/api-keys
LLM_API_KEY=your_openai_api_key_here

# AIPipe.org credentials (OPTIONAL - for fallback)
AIPIPE_TOKEN=your_aipipe_token_here
AIPIPE_EMAIL=your_email_here

# GitHub Username (OPTIONAL - for display purposes)
GITHUB_USERNAME=sibani0819

# Logging Level (OPTIONAL)
LOG_LEVEL=INFO

# Rate Limiting (OPTIONAL)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print(f"🔐 Generated verification secret: {verification_secret}")
    return True

def show_setup_instructions():
    """Show setup instructions to the user."""
    print("\n📋 Setup Instructions")
    print("=" * 50)
    print("1. 🔑 Get GitHub Personal Access Token:")
    print("   • Go to: https://github.com/settings/tokens")
    print("   • Click 'Generate new token (classic)'")
    print("   • Select scopes: repo, public_repo, admin:repo_hook, workflow")
    print("   • Copy the token and update GITHUB_PAT in .env file")
    
    print("\n2. 🤖 Get OpenAI API Key (Optional):")
    print("   • Go to: https://platform.openai.com/api-keys")
    print("   • Create a new API key")
    print("   • Copy the key and update LLM_API_KEY in .env file")
    
    print("\n3. 🔧 Update .env file:")
    print("   • Open .env file in your editor")
    print("   • Replace 'your_github_token_here' with your actual GitHub token")
    print("   • Replace 'your_openai_api_key_here' with your OpenAI key (if you have one)")
    print("   • The VERIFICATION_SECRET is already generated for you")
    
    print("\n4. 🚀 Run the application:")
    print("   • python main.py")
    print("   • Or use: python build_and_deploy.py")

def test_environment():
    """Test if the environment is properly configured."""
    print("\n🧪 Testing Environment Configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    github_pat = os.getenv('GITHUB_PAT')
    verification_secret = os.getenv('VERIFICATION_SECRET')
    
    if not github_pat or github_pat == 'your_github_token_here':
        print("❌ GITHUB_PAT not configured properly")
        return False
    
    if not verification_secret or verification_secret == 'your_verification_secret_here':
        print("❌ VERIFICATION_SECRET not configured properly")
        return False
    
    print("✅ Environment variables are properly configured")
    
    # Test GitHub connection
    try:
        from github import Github
        g = Github(github_pat)
        user = g.get_user()
        print(f"✅ GitHub connection successful - User: {user.login}")
        return True
    except Exception as e:
        print(f"❌ GitHub connection failed: {str(e)}")
        print("Please check your GITHUB_PAT token")
        return False

def main():
    """Main setup process."""
    print("🔧 LLM Code Deployment - Environment Setup")
    print("=" * 60)
    
    # Step 1: Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Step 2: Show setup instructions
    show_setup_instructions()
    
    # Step 3: Test environment (if user has configured it)
    print("\n" + "=" * 60)
    print("📝 Next Steps:")
    print("1. Update the .env file with your actual tokens")
    print("2. Run this script again to test: python setup_environment.py")
    print("3. Start the application: python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Environment setup completed!")
    else:
        print("\n❌ Environment setup failed!")
