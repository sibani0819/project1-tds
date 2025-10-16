# Deployment Guide

This guide covers different deployment options for the LLM Code Deployment API.

## 🚀 Quick Start

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd llm-code-deployment-project1
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Start the application**
   
   **Windows:**
   ```cmd
   start.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

4. **Test the API**
   ```bash
   python test_api.py
   ```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Setup environment**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Check status**
   ```bash
   docker-compose ps
   docker-compose logs llm-deployment-api
   ```

### Using Docker directly

1. **Build image**
   ```bash
   docker build -t llm-deployment-api .
   ```

2. **Run container**
   ```bash
   docker run -p 8000:8000 --env-file .env llm-deployment-api
   ```

## ☁️ Cloud Deployment

### AWS ECS/Fargate

1. **Create ECS cluster**
   ```bash
   aws ecs create-cluster --cluster-name llm-deployment
   ```

2. **Create task definition**
   ```json
   {
     "family": "llm-deployment-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "llm-deployment-api",
         "image": "your-account.dkr.ecr.region.amazonaws.com/llm-deployment-api:latest",
         "portMappings": [{"containerPort": 8000}],
         "environment": [
           {"name": "GITHUB_PAT", "value": "your-github-pat"},
           {"name": "LLM_API_KEY", "value": "your-openai-key"},
           {"name": "VERIFICATION_SECRET", "value": "your-secret"}
         ]
       }
     ]
   }
   ```

3. **Deploy service**
   ```bash
   aws ecs create-service \
     --cluster llm-deployment \
     --service-name llm-deployment-api \
     --task-definition llm-deployment-api \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

### Google Cloud Run

1. **Build and push image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/llm-deployment-api
   ```

2. **Deploy service**
   ```bash
   gcloud run deploy llm-deployment-api \
     --image gcr.io/PROJECT-ID/llm-deployment-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GITHUB_PAT=your-github-pat,LLM_API_KEY=your-openai-key,VERIFICATION_SECRET=your-secret
   ```

### Azure Container Instances

1. **Create resource group**
   ```bash
   az group create --name llm-deployment-rg --location eastus
   ```

2. **Deploy container**
   ```bash
   az container create \
     --resource-group llm-deployment-rg \
     --name llm-deployment-api \
     --image your-registry.azurecr.io/llm-deployment-api:latest \
     --dns-name-label llm-deployment-api \
     --ports 8000 \
     --environment-variables \
       GITHUB_PAT=your-github-pat \
       LLM_API_KEY=your-openai-key \
       VERIFICATION_SECRET=your-secret
   ```

## 🔧 Production Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GITHUB_PAT` | Yes | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `LLM_API_KEY` | Yes | OpenAI API Key | `sk-xxxxxxxxxxxx` |
| `VERIFICATION_SECRET` | Yes | Secret for request verification | `secure-random-string` |
| `LOG_LEVEL` | No | Logging level | `INFO` |
| `LOG_FILE` | No | Log file path | `app.log` |

### Security Considerations

1. **Environment Variables**
   - Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
   - Never commit secrets to version control
   - Rotate secrets regularly

2. **Network Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Use WAF for additional protection

3. **Access Control**
   - Implement authentication for admin endpoints
   - Use API keys for client access
   - Monitor and log all requests

### Monitoring and Logging

1. **Application Logs**
   ```bash
   # View logs
   docker-compose logs -f llm-deployment-api
   
   # Or with Docker
   docker logs -f container-name
   ```

2. **Health Monitoring**
   ```bash
   # Check health
   curl http://localhost:8000/health
   
   # Simple ping
   curl http://localhost:8000/ping
   ```

3. **Metrics Collection**
   - Use Prometheus for metrics collection
   - Set up Grafana dashboards
   - Monitor API response times and error rates

### Scaling Considerations

1. **Horizontal Scaling**
   - Use load balancers (AWS ALB, GCP Load Balancer)
   - Deploy multiple instances
   - Use container orchestration (Kubernetes, ECS)

2. **Database Integration**
   - Add PostgreSQL for task tracking
   - Use Redis for caching and task queues
   - Implement database connection pooling

3. **Performance Optimization**
   - Use CDN for static assets
   - Implement caching strategies
   - Optimize LLM API calls

## 🚨 Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   ```bash
   # Check if .env file exists and is readable
   ls -la .env
   cat .env
   ```

2. **GitHub API Errors**
   ```bash
   # Check GitHub token permissions
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

3. **OpenAI API Errors**
   ```bash
   # Check OpenAI API key
   curl -H "Authorization: Bearer YOUR_KEY" https://api.openai.com/v1/models
   ```

4. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill process
   kill -9 PID
   ```

### Log Analysis

1. **Application Logs**
   ```bash
   # View recent logs
   tail -f app.log
   
   # Search for errors
   grep -i error app.log
   ```

2. **Docker Logs**
   ```bash
   # View container logs
   docker logs container-name
   
   # Follow logs
   docker logs -f container-name
   ```

### Performance Issues

1. **High Memory Usage**
   - Monitor memory usage: `docker stats`
   - Increase container memory limits
   - Optimize LLM API calls

2. **Slow Response Times**
   - Check network connectivity
   - Monitor external API response times
   - Implement caching

3. **Rate Limiting**
   - Check GitHub API rate limits
   - Monitor OpenAI API usage
   - Implement request queuing

## 📊 Monitoring Setup

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/ping

# Comprehensive health check
curl http://localhost:8000/health
```

### Metrics Endpoints

- `/ping` - Simple health check
- `/health` - Detailed health status
- `/docs` - API documentation
- `/openapi.json` - OpenAPI specification

### Alerting

Set up alerts for:
- API response time > 5 seconds
- Error rate > 5%
- Health check failures
- High memory usage
- GitHub API rate limit exceeded

## 🔄 Updates and Maintenance

### Application Updates

1. **Code Updates**
   ```bash
   git pull origin main
   docker-compose build
   docker-compose up -d
   ```

2. **Dependency Updates**
   ```bash
   pip install -r requirements.txt --upgrade
   docker-compose build
   docker-compose up -d
   ```

3. **Database Migrations**
   ```bash
   # When database integration is added
   alembic upgrade head
   ```

### Backup and Recovery

1. **Configuration Backup**
   ```bash
   cp .env .env.backup
   ```

2. **Log Rotation**
   ```bash
   # Set up logrotate
   sudo logrotate /etc/logrotate.d/llm-deployment
   ```

3. **Disaster Recovery**
   - Keep environment variables in secure storage
   - Document deployment procedures
   - Test recovery procedures regularly
