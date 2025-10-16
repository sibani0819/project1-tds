#!/usr/bin/env python3
"""
Production Deployment Script for LLM Code Deployment Project
This script handles production deployment with proper monitoring and health checks.
"""

import os
import sys
import subprocess
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description="", check_output=False):
    """Run a command and return the result."""
    print(f"🔧 {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout and check_output:
                return result.stdout.strip()
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def check_production_requirements():
    """Check production requirements."""
    print("🔍 Checking Production Requirements...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please create it with required variables.")
        return False
    
    # Check required environment variables
    required_vars = ['GITHUB_PAT', 'VERIFICATION_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Production requirements met")
    return True

def setup_logging():
    """Setup production logging."""
    print("📝 Setting up Production Logging...")
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Setup log rotation
    log_config = """
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler,rotatingFileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_app]
level=INFO
handlers=rotatingFileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailedFormatter
args=('logs/app.log',)

[handler_rotatingFileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=detailedFormatter
args=('logs/app.log', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s
"""
    
    with open('logging.conf', 'w') as f:
        f.write(log_config)
    
    print("✅ Logging configuration created")
    return True

def create_systemd_service():
    """Create systemd service file for Linux systems."""
    print("🔧 Creating Systemd Service...")
    
    service_content = f"""[Unit]
Description=LLM Code Deployment API
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getenv('PATH')}
ExecStart=/usr/bin/python3 {os.getcwd()}/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('llm-code-deployment.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created: llm-code-deployment.service")
    print("To install: sudo cp llm-code-deployment.service /etc/systemd/system/")
    print("To enable: sudo systemctl enable llm-code-deployment")
    print("To start: sudo systemctl start llm-code-deployment")
    return True

def create_nginx_config():
    """Create nginx configuration for reverse proxy."""
    print("🌐 Creating Nginx Configuration...")
    
    nginx_config = """
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
"""
    
    with open('nginx-llm-deployment.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Nginx configuration created: nginx-llm-deployment.conf")
    print("To install: sudo cp nginx-llm-deployment.conf /etc/nginx/sites-available/")
    print("To enable: sudo ln -s /etc/nginx/sites-available/nginx-llm-deployment.conf /etc/nginx/sites-enabled/")
    print("To reload: sudo nginx -t && sudo systemctl reload nginx")
    return True

def create_monitoring_script():
    """Create monitoring script for production."""
    print("📊 Creating Monitoring Script...")
    
    monitor_script = """#!/bin/bash
# LLM Code Deployment Monitoring Script

API_URL="http://localhost:8000"
LOG_FILE="logs/monitor.log"
ALERT_EMAIL="your-email@example.com"  # Replace with your email

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Function to check API health
check_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)
    if [ $response -eq 200 ]; then
        log "✅ API Health Check: OK"
        return 0
    else
        log "❌ API Health Check: FAILED (HTTP $response)"
        return 1
    fi
}

# Function to check API ping
check_ping() {
    response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/ping)
    if [ $response -eq 200 ]; then
        log "✅ API Ping: OK"
        return 0
    else
        log "❌ API Ping: FAILED (HTTP $response)"
        return 1
    fi
}

# Function to send alert
send_alert() {
    log "🚨 ALERT: $1"
    # Add email notification here if needed
    # echo "$1" | mail -s "LLM Deployment Alert" $ALERT_EMAIL
}

# Main monitoring loop
log "🔍 Starting monitoring check"

if ! check_health; then
    send_alert "API Health Check Failed"
    exit 1
fi

if ! check_ping; then
    send_alert "API Ping Failed"
    exit 1
fi

log "✅ All checks passed"
exit 0
"""
    
    with open('monitor.sh', 'w') as f:
        f.write(monitor_script)
    
    # Make it executable
    os.chmod('monitor.sh', 0o755)
    
    print("✅ Monitoring script created: monitor.sh")
    print("To run: ./monitor.sh")
    print("To schedule: Add to crontab: */5 * * * * /path/to/monitor.sh")
    return True

def create_backup_script():
    """Create backup script for production data."""
    print("💾 Creating Backup Script...")
    
    backup_script = """#!/bin/bash
# LLM Code Deployment Backup Script

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="llm-deployment-backup-$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_DIR/$BACKUP_FILE \\
    --exclude='__pycache__' \\
    --exclude='*.pyc' \\
    --exclude='.git' \\
    --exclude='logs' \\
    --exclude='backups' \\
    .

echo "✅ Backup created: $BACKUP_DIR/$BACKUP_FILE"

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t llm-deployment-backup-*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Old backups cleaned up"
"""
    
    with open('backup.sh', 'w') as f:
        f.write(backup_script)
    
    # Make it executable
    os.chmod('backup.sh', 0o755)
    
    print("✅ Backup script created: backup.sh")
    print("To run: ./backup.sh")
    print("To schedule: Add to crontab: 0 2 * * * /path/to/backup.sh")
    return True

def deploy_production():
    """Deploy to production."""
    print("🚀 Deploying to Production...")
    
    # Stop any existing processes
    run_command("pkill -f 'python.*main.py'", "Stopping existing processes")
    time.sleep(2)
    
    # Start the application
    if run_command("nohup python main.py > logs/app.log 2>&1 &", "Starting production application"):
        print("✅ Application started in background")
        time.sleep(5)
        
        # Check if it's running
        if check_application_health():
            print("✅ Production deployment successful")
            return True
        else:
            print("❌ Application failed to start properly")
            return False
    else:
        print("❌ Failed to start application")
        return False

def check_application_health():
    """Check if the application is running and healthy."""
    print("🏥 Checking Application Health...")
    
    max_attempts = 5
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

def show_production_info():
    """Show production deployment information."""
    print("\n📋 Production Deployment Information")
    print("=" * 60)
    print("🌐 Application URLs:")
    print("   • Local: http://localhost:8000")
    print("   • Health Check: http://localhost:8000/health")
    print("   • API Docs: http://localhost:8000/docs")
    
    print("\n📁 Files Created:")
    print("   • logging.conf - Logging configuration")
    print("   • llm-code-deployment.service - Systemd service")
    print("   • nginx-llm-deployment.conf - Nginx configuration")
    print("   • monitor.sh - Monitoring script")
    print("   • backup.sh - Backup script")
    
    print("\n🔧 Production Setup Commands:")
    print("   • Install service: sudo cp llm-code-deployment.service /etc/systemd/system/")
    print("   • Enable service: sudo systemctl enable llm-code-deployment")
    print("   • Start service: sudo systemctl start llm-code-deployment")
    print("   • Check status: sudo systemctl status llm-code-deployment")
    
    print("\n📊 Monitoring:")
    print("   • Run monitor: ./monitor.sh")
    print("   • Schedule monitoring: */5 * * * * /path/to/monitor.sh")
    print("   • Run backup: ./backup.sh")
    print("   • Schedule backup: 0 2 * * * /path/to/backup.sh")

def main():
    """Main production deployment process."""
    print("🚀 LLM Code Deployment - Production Deployment")
    print("=" * 60)
    
    # Step 1: Check requirements
    if not check_production_requirements():
        print("\n❌ Production requirements not met.")
        return False
    
    # Step 2: Setup logging
    if not setup_logging():
        print("\n❌ Logging setup failed.")
        return False
    
    # Step 3: Create systemd service
    create_systemd_service()
    
    # Step 4: Create nginx config
    create_nginx_config()
    
    # Step 5: Create monitoring script
    create_monitoring_script()
    
    # Step 6: Create backup script
    create_backup_script()
    
    # Step 7: Deploy to production
    if not deploy_production():
        print("\n❌ Production deployment failed.")
        return False
    
    # Step 8: Show production info
    show_production_info()
    
    print("\n🎉 Production Deployment Completed Successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
