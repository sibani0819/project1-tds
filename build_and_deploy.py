#!/usr/bin/env python3
"""
Build and Deploy Script for LLM Code Deployment Project
This script helps build, test, and deploy the application properly.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description=""):
    """Run a command and return the result."""
    print(f"🔧 {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking Environment Variables...")
    required_vars = ['GITHUB_PAT', 'VERIFICATION_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def install_dependencies():
    """Install project dependencies."""
    print("\n📦 Installing Dependencies...")
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def run_tests():
    """Run the test suite."""
    print("\n🧪 Running Tests...")
    
    # Test 1: Syntax check
    if not run_command("python -m py_compile main.py", "Syntax check"):
        return False
    
    # Test 2: API tests
    if not run_command("python test_api.py", "API functionality tests"):
        return False
    
    # Test 3: Complete workflow test
    if not run_command("python test_complete_workflow.py", "Complete workflow test"):
        return False
    
    return True

def build_docker():
    """Build Docker image."""
    print("\n🐳 Building Docker Image...")
    return run_command("docker build -t llm-code-deployment .", "Building Docker image")

def start_application():
    """Start the application."""
    print("\n🚀 Starting Application...")
    
    # Kill any existing Python processes
    run_command("taskkill /f /im python.exe", "Killing existing Python processes")
    time.sleep(2)
    
    # Start the application
    return run_command("python main.py", "Starting FastAPI application")

def check_application_health():
    """Check if the application is running and healthy."""
    print("\n🏥 Checking Application Health...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Application is healthy and running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for application to start... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(3)
    
    print("❌ Application failed to start or is not responding")
    return False

def deploy_to_production():
    """Deploy to production (example with Docker)."""
    print("\n🚀 Deploying to Production...")
    
    # Stop existing containers
    run_command("docker-compose down", "Stopping existing containers")
    
    # Start new containers
    if run_command("docker-compose up -d", "Starting production containers"):
        print("✅ Application deployed successfully")
        return True
    else:
        print("❌ Deployment failed")
        return False

def show_deployment_info():
    """Show deployment information and URLs."""
    print("\n📋 Deployment Information")
    print("=" * 50)
    print("🌐 Application URLs:")
    print("   • Local: http://localhost:8000")
    print("   • Health Check: http://localhost:8000/health")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Ping: http://localhost:8000/ping")
    
    print("\n🔗 GitHub Pages URLs (from recent deployments):")
    repos = [
        'llm-project-test-captcha-solver-3ebf2ef2-5916fdff',
        'llm-project-test-captcha-solver-b821db72-043fa67a', 
        'llm-project-test-captcha-solver-11536b70-31627fe0'
    ]
    
    for i, repo in enumerate(repos, 1):
        print(f"   • Repository {i}: https://sibani0819.github.io/{repo}")
    
    print("\n📝 Next Steps:")
    print("   1. Test the API endpoints")
    print("   2. Send a test request to /task")
    print("   3. Check GitHub for new repositories")
    print("   4. Verify GitHub Pages are enabled")
    print("   5. Monitor application logs")

def main():
    """Main build and deploy process."""
    print("🏗️  LLM Code Deployment - Build & Deploy Script")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        return False
    
    # Step 3: Run tests
    if not run_tests():
        print("\n❌ Tests failed. Please fix the issues above.")
        return False
    
    # Step 4: Build Docker (optional)
    print("\n🐳 Docker Build (Optional)")
    build_docker()  # Don't fail if Docker build fails
    
    # Step 5: Start application
    if not start_application():
        print("\n❌ Failed to start application.")
        return False
    
    # Step 6: Check health
    if not check_application_health():
        print("\n❌ Application health check failed.")
        return False
    
    # Step 7: Show deployment info
    show_deployment_info()
    
    print("\n🎉 Build and Deploy Process Completed Successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
