# 🏗️ Build and Deploy Guide

This guide will help you build, test, and deploy the LLM Code Deployment application.

## 📋 Prerequisites

- Python 3.8+ installed
- Git installed
- GitHub account with Personal Access Token
- (Optional) OpenAI API key
- (Optional) Docker for containerized deployment

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Run the environment setup script
python setup_environment.py
```

This will create a `.env` file with all required environment variables.

### 2. Configure Environment Variables

Edit the `.env` file and add your actual tokens:

```bash
# Required: GitHub Personal Access Token
GITHUB_PAT=your_actual_github_token_here

# Required: Verification Secret (auto-generated)
VERIFICATION_SECRET=OA4G*oFKS446t%S^XNnYODdQmSX%bykK

# Optional: OpenAI API Key
LLM_API_KEY=your_openai_api_key_here

# Optional: GitHub Username
GITHUB_USERNAME=sibani0819
```

### 3. Get GitHub Personal Access Token

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select these scopes:
   - `repo` (Full control of private repositories)
   - `public_repo` (Access public repositories)
   - `admin:repo_hook` (Full control of repository hooks)
   - `workflow` (Update GitHub Action workflows)
4. Copy the token and update `GITHUB_PAT` in your `.env` file

### 4. Test Environment

```bash
# Test if environment is configured correctly
python setup_environment.py
```

## 🏗️ Build and Deploy

### Option 1: Automated Build and Deploy

```bash
# Run the complete build and deploy process
python build_and_deploy.py
```

This script will:
- ✅ Check environment variables
- ✅ Install dependencies
- ✅ Run syntax checks
- ✅ Run API tests
- ✅ Run complete workflow tests
- ✅ Start the application
- ✅ Verify health checks

### Option 2: Manual Build and Deploy

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run tests
python test_api.py
python test_complete_workflow.py

# 3. Start application
python main.py
```

### Option 3: Docker Deployment

```bash
# Build Docker image
docker build -t llm-code-deployment .

# Run with Docker Compose
docker-compose up -d
```

## 🧪 Testing

### Run All Tests

```bash
# Complete test suite
python build_and_deploy.py
```

### Individual Tests

```bash
# API functionality tests
python test_api.py

# Complete workflow test
python test_complete_workflow.py

# GitHub integration test
python test_github_integration.py
```

## 🚀 Production Deployment

### Automated Production Deployment

```bash
# Deploy to production with monitoring
python deploy_production.py
```

This will create:
- Systemd service file
- Nginx configuration
- Monitoring scripts
- Backup scripts
- Logging configuration

### Manual Production Setup

1. **Create systemd service:**
   ```bash
   sudo cp llm-code-deployment.service /etc/systemd/system/
   sudo systemctl enable llm-code-deployment
   sudo systemctl start llm-code-deployment
   ```

2. **Setup Nginx reverse proxy:**
   ```bash
   sudo cp nginx-llm-deployment.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/nginx-llm-deployment.conf /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

3. **Setup monitoring:**
   ```bash
   # Run monitoring script
   ./monitor.sh
   
   # Schedule monitoring (every 5 minutes)
   crontab -e
   # Add: */5 * * * * /path/to/monitor.sh
   ```

4. **Setup backups:**
   ```bash
   # Run backup script
   ./backup.sh
   
   # Schedule backups (daily at 2 AM)
   crontab -e
   # Add: 0 2 * * * /path/to/backup.sh
   ```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check API ping
curl http://localhost:8000/ping
```

### Logs

```bash
# View application logs
tail -f logs/app.log

# View systemd logs
sudo journalctl -u llm-code-deployment -f
```

### Backup and Restore

```bash
# Create backup
./backup.sh

# Restore from backup
tar -xzf backups/llm-deployment-backup-YYYYMMDD_HHMMSS.tar.gz
```

## 🔗 Your GitHub Pages URLs

Based on your recent deployments, here are your GitHub Pages URLs:

### Repository 1: `llm-project-test-captcha-solver-3ebf2ef2-5916fdff`
- **GitHub Pages**: https://sibani0819.github.io/llm-project-test-captcha-solver-3ebf2ef2-5916fdff
- **Repository**: https://github.com/sibani0819/llm-project-test-captcha-solver-3ebf2ef2-5916fdff

### Repository 2: `llm-project-test-captcha-solver-b821db72-043fa67a`
- **GitHub Pages**: https://sibani0819.github.io/llm-project-test-captcha-solver-b821db72-043fa67a
- **Repository**: https://github.com/sibani0819/llm-project-test-captcha-solver-b821db72-043fa67a

### Repository 3: `llm-project-test-captcha-solver-11536b70-31627fe0` (Latest)
- **GitHub Pages**: https://sibani0819.github.io/llm-project-test-captcha-solver-11536b70-31627fe0
- **Repository**: https://github.com/sibani0819/llm-project-test-captcha-solver-11536b70-31627fe0

## 🛠️ Troubleshooting

### Common Issues

1. **Environment variables not loaded:**
   ```bash
   # Make sure .env file exists and has correct values
   python setup_environment.py
   ```

2. **GitHub API errors:**
   - Check your GitHub token has correct scopes
   - Verify token is not expired
   - Check rate limits

3. **Application won't start:**
   ```bash
   # Check for syntax errors
   python -m py_compile main.py
   
   # Check logs
   tail -f logs/app.log
   ```

4. **Port already in use:**
   ```bash
   # Kill existing processes
   taskkill /f /im python.exe
   # Or on Linux: pkill -f python
   ```

### Getting Help

1. Check the logs: `tail -f logs/app.log`
2. Run diagnostics: `python diagnose_github.py`
3. Test individual components: `python test_api.py`

## 📈 Performance Optimization

### For High Traffic

1. **Use a reverse proxy (Nginx):**
   ```bash
   # Install and configure Nginx
   sudo apt install nginx
   sudo cp nginx-llm-deployment.conf /etc/nginx/sites-available/
   ```

2. **Enable caching:**
   ```bash
   # Add to nginx config
   location /static {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Database integration:**
   - Add PostgreSQL for task tracking
   - Implement Redis for caching
   - Use connection pooling

### Scaling

1. **Horizontal scaling:**
   - Use load balancer
   - Multiple application instances
   - Database clustering

2. **Vertical scaling:**
   - Increase server resources
   - Optimize Python code
   - Use async processing

## 🎉 Success!

Once everything is set up, you should have:

- ✅ LLM Code Deployment API running
- ✅ GitHub integration working
- ✅ Separate CSS/JS files being generated
- ✅ GitHub Pages deployment
- ✅ Monitoring and backup systems
- ✅ Production-ready configuration

Your application will be available at:
- **Local**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

And your generated applications will be available at the GitHub Pages URLs listed above!
