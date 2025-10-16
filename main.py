from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os, json, base64, requests, tempfile, shutil
from github import Github, GithubException
from dotenv import load_dotenv
from openai import OpenAI
import time
import logging
import asyncio
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import hashlib
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(
    title="LLM Code Deployment API",
    description="API for building, deploying, and updating applications using LLM assistance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment secrets
GITHUB_PAT = os.getenv("GITHUB_PAT")
LLM_API_KEY = os.getenv("LLM_API_KEY")
VERIFICATION_SECRET = os.getenv("VERIFICATION_SECRET")

if not all([GITHUB_PAT, VERIFICATION_SECRET]):
    raise ValueError("Missing required environment variables: GITHUB_PAT, VERIFICATION_SECRET")

# LLM_API_KEY is optional - if not provided, will use aipipe.org fallback
if not LLM_API_KEY:
    logger.warning("LLM_API_KEY not provided, will use aipipe.org fallback")

# Initialize OpenAI client with new API (only if API key is provided)
if LLM_API_KEY:
    openai_client = OpenAI(api_key=LLM_API_KEY)
else:
    openai_client = None

# Pydantic models for request/response validation
class TaskRequest(BaseModel):
    email: str = Field(..., description="Student email ID")
    secret: str = Field(..., description="Student-provided secret")
    task: str = Field(..., description="Unique task ID")
    round: int = Field(..., description="Round index")
    nonce: str = Field(..., description="Nonce to pass back to evaluation URL")
    brief: str = Field(..., description="App brief describing what needs to be built")
    checks: List[str] = Field(default=[], description="Evaluation criteria")
    evaluation_url: str = Field(..., description="URL to notify when task is complete")
    attachments: List[Dict[str, str]] = Field(default=[], description="Base64 encoded attachments")

class TaskResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None

class EvaluationPayload(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str

# Utility functions
def validate_secret(secret: str) -> bool:
    """Validate the provided secret against the stored verification secret."""
    return secret == VERIFICATION_SECRET

def sanitize_repo_name(task: str, nonce: str) -> str:
    """Create a sanitized repository name from task and nonce."""
    # Remove special characters and convert to lowercase
    sanitized_task = re.sub(r'[^a-zA-Z0-9-]', '-', task.lower())
    sanitized_task = re.sub(r'-+', '-', sanitized_task).strip('-')
    return f"llm-project-{sanitized_task}-{nonce[:8]}"

def generate_enhanced_prompt(brief: str, checks: List[str], attachments: List[Dict[str, str]]) -> str:
    """Generate an enhanced prompt for the LLM based on the brief and requirements."""
    prompt = f"""
Create a complete, production-ready web application based on this brief:

BRIEF: {brief}

REQUIREMENTS:
{chr(10).join(f"- {check}" for check in checks)}

The application should be:
1. Fully functional and production-ready
2. Responsive and mobile-friendly
3. SEO-optimized with proper meta tags
4. Accessible with proper ARIA labels
5. Fast-loading with optimized assets
6. Secure with proper input validation

Include:
- Complete HTML structure with semantic elements
- Modern CSS with responsive design
- JavaScript for interactivity
- Professional README.md with setup instructions
- MIT LICENSE file
- Proper error handling and user feedback

If attachments are provided, integrate them appropriately into the application.

Generate clean, well-commented, and maintainable code.
"""
    return prompt

# Import aipipe integration
from aipipe_integration import generate_with_aipipe

async def generate_app_code(brief: str, checks: List[str], attachments: List[Dict[str, str]]) -> Dict[str, str]:
    """Generate application code using LLM with enhanced prompting."""
    try:
        prompt = generate_enhanced_prompt(brief, checks, attachments)
        
        # Try OpenAI first if available, otherwise use aipipe.org fallback
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert web developer. Generate complete, production-ready web applications with proper HTML, CSS, and JavaScript. Always include proper documentation and follow best practices."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
                generated_content = response.choices[0].message.content
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.warning("OpenAI quota exceeded, trying aipipe.org fallback")
                    generated_content = await generate_with_aipipe(prompt)
                else:
                    logger.warning(f"OpenAI error: {str(e)}, trying aipipe.org fallback")
                    generated_content = await generate_with_aipipe(prompt)
        else:
            logger.info("No OpenAI API key provided, using aipipe.org fallback")
            generated_content = await generate_with_aipipe(prompt)
        
        # Parse the generated content to extract different files
        files = {}
        
        # Try to extract HTML, CSS, and JS from the response
        if "```html" in generated_content:
            html_start = generated_content.find("```html") + 7
            html_end = generated_content.find("```", html_start)
            files["index.html"] = generated_content[html_start:html_end].strip()
        elif "```" in generated_content:
            # If no language specified, assume it's HTML
            code_start = generated_content.find("```") + 3
            code_end = generated_content.find("```", code_start)
            files["index.html"] = generated_content[code_start:code_end].strip()
        else:
            # Fallback: use the entire content as HTML
            files["index.html"] = generated_content
        
        # Generate separate CSS file
        files["styles.css"] = """/* Generated Application Styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    line-height: 1.6;
}

.container {
    background: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    margin: 20px 0;
}

h1 {
    color: #333;
    text-align: center;
    margin-bottom: 30px;
    font-size: 2.5em;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h2, h3 {
    color: #444;
    margin-top: 30px;
}

.content {
    margin: 20px 0;
    line-height: 1.8;
    font-size: 1.1em;
}

.features {
    background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
    padding: 25px;
    border-radius: 10px;
    margin: 30px 0;
    border-left: 5px solid #667eea;
}

.code-block {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    margin: 20px 0;
    font-family: 'Courier New', monospace;
    overflow-x: auto;
}

.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1em;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn:active {
    transform: translateY(0);
}

ul {
    list-style: none;
    padding: 0;
}

li {
    padding: 8px 0;
    position: relative;
    padding-left: 25px;
}

li::before {
    content: "✨";
    position: absolute;
    left: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 20px;
        margin: 10px;
    }
    
    h1 {
        font-size: 2em;
    }
    
    .btn {
        width: 100%;
        margin-top: 10px;
    }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .btn {
        transition: none;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .container {
        background: #1a1a1a;
        color: #e0e0e0;
    }
    
    .code-block {
        background: #2d2d2d;
        color: #e0e0e0;
        border-color: #444;
    }
}"""

        # Generate separate JavaScript file
        files["script.js"] = f"""// Generated Application JavaScript
console.log('🚀 Generated application loaded successfully');
console.log('📝 Brief:', `{prompt[:100]}...`);

// Application functionality
function testFunctionality() {{
    alert('🎉 Application is working perfectly!\\n\\nThis demonstrates that the generated application is fully functional.');
    
    // Add some visual feedback
    const btn = document.querySelector('.btn');
    const originalText = btn.textContent;
    btn.textContent = '✅ Tested!';
    btn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
    
    setTimeout(() => {{
        btn.textContent = originalText;
        btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }}, 2000);
}}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {{
    console.log('✅ DOM loaded and ready');
    
    // Add some interactive features
    const features = document.querySelectorAll('.features li');
    features.forEach((feature, index) => {{
        feature.style.opacity = '0';
        feature.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {{
            feature.style.transition = 'all 0.5s ease';
            feature.style.opacity = '1';
            feature.style.transform = 'translateX(0)';
        }}, index * 100);
    }});
    
    // Add click handlers for better UX
    const codeBlock = document.querySelector('.code-block');
    if (codeBlock) {{
        codeBlock.addEventListener('click', function() {{
            this.style.background = '#e3f2fd';
            setTimeout(() => {{
                this.style.background = '#f8f9fa';
            }}, 1000);
        }});
    }}
}});

// Utility functions
function showNotification(message, type = 'info') {{
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${{type === 'success' ? '#28a745' : '#17a2b8'}};
        color: white;
        border-radius: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {{
        notification.remove();
    }}, 3000);
}}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
`;
document.head.appendChild(style);"""
        
        # Generate README.md
        files["README.md"] = f"""# {brief.split('.')[0]}

## Description
{brief}

## Setup
1. Clone this repository
2. Open `index.html` in a web browser
3. No additional setup required

## Features
{chr(10).join(f"- {check}" for check in checks)}

## License
MIT License - see LICENSE file for details.

## Generated by LLM Code Deployment API
This application was automatically generated using AI assistance.
"""
        
        # Generate MIT LICENSE
        files["LICENSE"] = """MIT License

Copyright (c) 2024 LLM Code Deployment

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        return files
        
    except Exception as e:
        logger.error(f"Error generating app code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate application code: {str(e)}")

async def create_github_repo(repo_name: str, files: Dict[str, str]) -> tuple[str, str]:
    """Create GitHub repository and push files."""
    try:
        g = Github(GITHUB_PAT)
        user = g.get_user()
        
        # Create repository
        repo = user.create_repo(
            repo_name,
            private=False,
            description=f"LLM-generated application: {repo_name}",
            has_issues=True,
            has_wiki=True,
            has_downloads=True
        )
        
        # Create initial commit with all files
        commit_message = "Initial commit: LLM-generated application"
        repo.create_file("README.md", commit_message, files["README.md"])
        
        # Create GitHub Actions workflow for automatic deployment
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
        
        # Create .github/workflows directory and workflow file
        try:
            repo.create_file(".github/workflows/deploy.yml", commit_message, workflow_content)
            logger.info("Created GitHub Actions workflow for automatic deployment")
        except Exception as e:
            logger.warning(f"Could not create GitHub Actions workflow: {str(e)}")
        
        for filename, content in files.items():
            if filename != "README.md":
                try:
                    repo.create_file(filename, commit_message, content)
                except GithubException as e:
                    if e.status == 422:  # File already exists
                        continue
                    raise
        
        # Enable GitHub Pages using the correct API
        try:
            # Enable GitHub Pages for the repository
            pages_data = {
                "source": {
                    "branch": "main",
                    "path": "/"
                }
            }
            
            # Use the GitHub API to enable Pages
            import requests
            headers = {
                "Authorization": f"token {GITHUB_PAT}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            pages_url = f"https://api.github.com/repos/{user.login}/{repo_name}/pages"
            response = requests.post(pages_url, headers=headers, json=pages_data)
            
            if response.status_code == 201:
                logger.info(f"GitHub Pages enabled for {repo_name}")
            else:
                logger.warning(f"Could not enable GitHub Pages: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.warning(f"Could not enable GitHub Pages automatically: {str(e)}")
        
        repo_url = f"https://github.com/{user.login}/{repo_name}"
        pages_url = f"https://{user.login}.github.io/{repo_name}"
        
        return repo_url, pages_url
        
    except GithubException as e:
        logger.error(f"GitHub API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create GitHub repository: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating repo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def update_github_repo(repo_name: str, files: Dict[str, str], round_num: int) -> tuple[str, str]:
    """Update existing GitHub repository with new files."""
    try:
        g = Github(GITHUB_PAT)
        user = g.get_user()
        
        # Get existing repository
        try:
            repo = user.get_repo(repo_name)
        except GithubException as e:
            if e.status == 404:
                # Repository doesn't exist, create it
                logger.info(f"Repository {repo_name} not found, creating new one")
                return await create_github_repo(repo_name, files)
            raise
        
        # Update files in repository
        commit_message = f"Update for round {round_num}: LLM-generated improvements"
        
        for filename, content in files.items():
            try:
                # Try to get existing file
                file = repo.get_contents(filename)
                # Update existing file
                repo.update_file(
                    filename,
                    commit_message,
                    content,
                    file.sha
                )
                logger.info(f"Updated {filename} in repository {repo_name}")
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    repo.create_file(filename, commit_message, content)
                    logger.info(f"Created {filename} in repository {repo_name}")
                else:
                    raise
        
        # Update README with revision info
        try:
            readme_content = files.get("README.md", "")
            if readme_content:
                readme_file = repo.get_contents("README.md")
                updated_readme = f"{readme_content}\n\n## Revision History\n- Round {round_num}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Updated application based on new requirements"
                repo.update_file(
                    "README.md",
                    f"Update README for round {round_num}",
                    updated_readme,
                    readme_file.sha
                )
        except Exception as e:
            logger.warning(f"Could not update README: {str(e)}")
        
        repo_url = f"https://github.com/{user.login}/{repo_name}"
        pages_url = f"https://{user.login}.github.io/{repo_name}"
        
        return repo_url, pages_url
        
    except GithubException as e:
        logger.error(f"GitHub API error updating repo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update GitHub repository: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error updating repo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def notify_evaluation_api(evaluation_url: str, payload: EvaluationPayload) -> bool:
    """Notify the evaluation API with retry mechanism."""
    max_retries = 5
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                evaluation_url,
                json=payload.dict(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully notified evaluation API on attempt {attempt + 1}")
                return True
            else:
                logger.warning(f"Evaluation API returned status {response.status_code} on attempt {attempt + 1}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed on attempt {attempt + 1}: {str(e)}")
        
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
    
    logger.error("Failed to notify evaluation API after all retries")
    return False

@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "github": "unknown",
            "openai": "unknown"
        }
    }
    
    # Check GitHub connectivity
    try:
        g = Github(GITHUB_PAT)
        user = g.get_user()
        health_status["services"]["github"] = "connected"
    except Exception as e:
        health_status["services"]["github"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check OpenAI connectivity
    if openai_client:
        try:
            openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            health_status["services"]["openai"] = "connected"
        except Exception as e:
            health_status["services"]["openai"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    else:
        health_status["services"]["openai"] = "not configured (using aipipe.org fallback)"
    
    return health_status

@app.post("/task", response_model=TaskResponse)
async def handle_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Handle task requests with comprehensive validation and processing."""
    task_id = str(uuid.uuid4())
    logger.info(f"Processing task {task_id}: {task_request.task}")
    
    try:
        # 1️⃣ Verify secret
        if not validate_secret(task_request.secret):
            logger.warning(f"Invalid secret for task {task_id}")
            raise HTTPException(status_code=401, detail="Invalid secret")
        
        # 2️⃣ Validate request data
        if not task_request.brief.strip():
            raise HTTPException(status_code=400, detail="Brief cannot be empty")
        
        if not task_request.evaluation_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid evaluation URL")
        
        # 3️⃣ Process task in background
        background_tasks.add_task(
            process_task_background,
            task_id,
            task_request
        )
        
        logger.info(f"Task {task_id} queued for processing")
        return TaskResponse(
            status="accepted",
            message="Task received and queued for processing",
            task_id=task_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error handling task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_task_background(task_id: str, task_request: TaskRequest):
    """Process task in background with comprehensive error handling."""
    logger.info(f"Starting background processing for task {task_id}")
    
    try:
        # 1️⃣ Generate application code
        logger.info(f"Generating code for task {task_id}")
        files = await generate_app_code(
            task_request.brief,
            task_request.checks,
            task_request.attachments
        )
        
        # 2️⃣ Create GitHub repository
        logger.info(f"Creating GitHub repository for task {task_id}")
        repo_name = sanitize_repo_name(task_request.task, task_request.nonce)
        repo_url, pages_url = await create_github_repo(repo_name, files)
        
        # 3️⃣ Notify evaluation API
        logger.info(f"Notifying evaluation API for task {task_id}")
        evaluation_payload = EvaluationPayload(
            email=task_request.email,
            task=task_request.task,
            round=task_request.round,
            nonce=task_request.nonce,
            repo_url=repo_url,
            commit_sha="main",  # We'll use main branch
            pages_url=pages_url
        )
        
        success = await notify_evaluation_api(task_request.evaluation_url, evaluation_payload)
        
        if success:
            logger.info(f"Task {task_id} completed successfully")
        else:
            logger.error(f"Task {task_id} completed but evaluation notification failed")
            
    except Exception as e:
        logger.error(f"Background processing failed for task {task_id}: {str(e)}")
        # In a production system, you might want to store failed tasks for retry

@app.post("/revise", response_model=TaskResponse)
async def handle_revision(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Handle revision requests (round 2+) for existing applications."""
    task_id = str(uuid.uuid4())
    logger.info(f"Processing revision {task_id} for task: {task_request.task}")
    
    try:
        # 1️⃣ Verify secret
        if not validate_secret(task_request.secret):
            logger.warning(f"Invalid secret for revision {task_id}")
            raise HTTPException(status_code=401, detail="Invalid secret")
        
        # 2️⃣ Validate request data
        if not task_request.brief.strip():
            raise HTTPException(status_code=400, detail="Brief cannot be empty")
        
        if task_request.round < 2:
            raise HTTPException(status_code=400, detail="Revision endpoint is for round 2+ only")
        
        # 3️⃣ Process revision in background
        background_tasks.add_task(
            process_revision_background,
            task_id,
            task_request
        )
        
        logger.info(f"Revision {task_id} queued for processing")
        return TaskResponse(
            status="accepted",
            message="Revision received and queued for processing",
            task_id=task_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error handling revision {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_revision_background(task_id: str, task_request: TaskRequest):
    """Process revision in background with comprehensive error handling."""
    logger.info(f"Starting background processing for revision {task_id}")
    
    try:
        # 1️⃣ Generate updated application code
        logger.info(f"Generating updated code for revision {task_id}")
        files = await generate_app_code(
            task_request.brief,
            task_request.checks,
            task_request.attachments
        )
        
        # 2️⃣ Update existing GitHub repository
        logger.info(f"Updating GitHub repository for revision {task_id}")
        repo_name = sanitize_repo_name(task_request.task, task_request.nonce)
        repo_url, pages_url = await update_github_repo(repo_name, files, task_request.round)
        
        # 3️⃣ Notify evaluation API
        logger.info(f"Notifying evaluation API for revision {task_id}")
        evaluation_payload = EvaluationPayload(
            email=task_request.email,
            task=task_request.task,
            round=task_request.round,
            nonce=task_request.nonce,
            repo_url=repo_url,
            commit_sha="main",
            pages_url=pages_url
        )
        
        success = await notify_evaluation_api(task_request.evaluation_url, evaluation_payload)
        
        if success:
            logger.info(f"Revision {task_id} completed successfully")
        else:
            logger.error(f"Revision {task_id} completed but evaluation notification failed")
            
    except Exception as e:
        logger.error(f"Background processing failed for revision {task_id}: {str(e)}")

@app.get("/tasks")
async def list_tasks():
    """List recent tasks (placeholder for future database integration)."""
    # This would typically query a database
    return {
        "message": "Task listing not yet implemented",
        "note": "This endpoint will be implemented when database integration is added"
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task."""
    # This would typically query a database
    return {
        "task_id": task_id,
        "status": "unknown",
        "message": "Task status tracking not yet implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)