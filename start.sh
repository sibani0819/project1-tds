#!/bin/bash

# LLM Code Deployment API Startup Script

echo "🚀 Starting LLM Code Deployment API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.example to .env and configure your environment variables:"
    echo "cp env.example .env"
    echo "Then edit .env with your actual values."
    exit 1
fi

# Check if required environment variables are set
source .env

if [ -z "$GITHUB_PAT" ]; then
    echo "❌ GITHUB_PAT not set in .env file"
    exit 1
fi

if [ -z "$LLM_API_KEY" ]; then
    echo "❌ LLM_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$VERIFICATION_SECRET" ]; then
    echo "❌ VERIFICATION_SECRET not set in .env file"
    exit 1
fi

echo "✅ Environment variables configured"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo "🔧 Starting application..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo "Health check at: http://localhost:8000/ping"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the application
python main.py
