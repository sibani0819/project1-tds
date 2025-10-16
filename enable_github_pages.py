#!/usr/bin/env python3
"""
Enable GitHub Pages for existing repositories
This script helps enable GitHub Pages for repositories that were created before the automatic setup.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def enable_github_pages(repo_name: str):
    """Enable GitHub Pages for a specific repository."""
    github_pat = os.getenv("GITHUB_PAT")
    github_username = os.getenv("GITHUB_USERNAME", "sibani0819")
    
    if not github_pat:
        print("❌ GITHUB_PAT not found in environment variables")
        return False
    
    headers = {
        "Authorization": f"token {github_pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Enable GitHub Pages
    pages_url = f"https://api.github.com/repos/{github_username}/{repo_name}/pages"
    pages_data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    try:
        response = requests.post(pages_url, headers=headers, json=pages_data)
        
        if response.status_code == 201:
            print(f"✅ GitHub Pages enabled for {repo_name}")
            print(f"🌐 URL: https://{github_username}.github.io/{repo_name}")
            return True
        elif response.status_code == 409:
            print(f"⚠️  GitHub Pages already enabled for {repo_name}")
            return True
        else:
            print(f"❌ Failed to enable GitHub Pages: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enabling GitHub Pages: {str(e)}")
        return False

def create_github_actions_workflow(repo_name: str):
    """Create GitHub Actions workflow for automatic deployment."""
    github_pat = os.getenv("GITHUB_PAT")
    github_username = os.getenv("GITHUB_USERNAME", "sibani0819")
    
    if not github_pat:
        print("❌ GITHUB_PAT not found in environment variables")
        return False
    
    headers = {
        "Authorization": f"token {github_pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    workflow_content = """name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
    
    # Create the workflow file
    import base64
    workflow_url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/.github/workflows/deploy.yml"
    workflow_data = {
        "message": "Add GitHub Actions workflow for Pages deployment",
        "content": base64.b64encode(workflow_content.encode('utf-8')).decode('utf-8')
    }
    
    try:
        response = requests.put(workflow_url, headers=headers, json=workflow_data)
        
        if response.status_code in [201, 200]:
            print(f"✅ GitHub Actions workflow created for {repo_name}")
            return True
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating workflow: {str(e)}")
        return False

def main():
    """Main function to enable GitHub Pages for all repositories."""
    print("🔧 GitHub Pages Setup Script")
    print("=" * 50)
    
    # List of repositories to enable GitHub Pages for
    repositories = [
        "llm-project-test-captcha-solver-59c6f535-d52bbca2",  # Latest
        "llm-project-test-captcha-solver-11536b70-31627fe0",
        "llm-project-test-captcha-solver-b821db72-043fa67a",
        "llm-project-test-captcha-solver-3ebf2ef2-5916fdff"
    ]
    
    print(f"📋 Found {len(repositories)} repositories to configure")
    print()
    
    success_count = 0
    
    for i, repo_name in enumerate(repositories, 1):
        print(f"🔧 Processing Repository {i}/{len(repositories)}: {repo_name}")
        print("-" * 60)
        
        # Enable GitHub Pages
        if enable_github_pages(repo_name):
            success_count += 1
        
        # Create GitHub Actions workflow
        create_github_actions_workflow(repo_name)
        
        print()
    
    print("=" * 50)
    print(f"✅ Successfully configured {success_count}/{len(repositories)} repositories")
    
    if success_count > 0:
        print("\n🌐 Your GitHub Pages URLs:")
        print("-" * 30)
        for repo_name in repositories:
            print(f"• https://sibani0819.github.io/{repo_name}")
    
    print("\n📝 Next Steps:")
    print("1. Wait 5-10 minutes for GitHub Pages to build")
    print("2. Check the Actions tab in your repositories")
    print("3. Visit the GitHub Pages URLs above")
    print("4. If Pages don't work, check repository Settings > Pages")

if __name__ == "__main__":
    main()
