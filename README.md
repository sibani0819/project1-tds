# LLM Code Deployment API

A scalable, production-ready API for building, deploying, and updating web applications using LLM assistance. This system can handle millions of records and provides effective SEO optimization for generated applications.

## 🚀 Features

- **LLM-Powered Code Generation**: Uses OpenAI's GPT models to generate complete, production-ready web applications
- **GitHub Integration**: Automatically creates repositories, manages files, and enables GitHub Pages deployment
- **Scalable Architecture**: Built with FastAPI for high performance and scalability
- **Comprehensive Error Handling**: Robust error handling with retry mechanisms and detailed logging
- **Security**: Secret verification and input validation
- **Background Processing**: Asynchronous task processing for better performance
- **Revision Support**: Handle multiple rounds of updates and improvements
- **SEO Optimization**: Generated applications include proper meta tags and accessibility features

## 📋 API Endpoints

### Core Endpoints

- `POST /task` - Create and deploy a new application
- `POST /revise` - Update an existing application (round 2+)
- `GET /ping` - Health check
- `GET /health` - Comprehensive health status
- `GET /tasks` - List tasks (placeholder for database integration)
- `GET /tasks/{task_id}` - Get task status (placeholder for database integration)

### Request Format

```json
{
  "email": "student@example.com",
  "secret": "your-secret-here",
  "task": "captcha-solver-...",
  "round": 1,
  "nonce": "ab12-...",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw..."
    }
  ]
}
```

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-code-deployment-project1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

4. **Set up environment variables**
   ```bash
   # Required
   GITHUB_PAT=your_github_personal_access_token_here
   LLM_API_KEY=your_openai_api_key_here
   VERIFICATION_SECRET=your_secure_secret_here
   ```

### GitHub Token Setup

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Generate a new token with the following scopes:
   - `repo` (Full control of private repositories)
   - `public_repo` (Access public repositories)
   - `admin:repo_hook` (Full control of repository hooks)

### OpenAI API Key Setup

1. Go to [OpenAI Platform > API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

## 🚀 Running the Application

### Development Mode

```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker (Optional)

```bash
# Build the image
docker build -t llm-deployment-api .

# Run the container
docker run -p 8000:8000 --env-file .env llm-deployment-api
```

## 📖 Usage Examples

### Creating a New Application

```bash
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "secret": "your-secret",
    "task": "todo-app-123",
    "round": 1,
    "nonce": "abc123",
    "brief": "Create a simple todo application with add, edit, and delete functionality",
    "checks": [
      "Application is responsive",
      "Todos can be added and deleted",
      "Data persists in localStorage"
    ],
    "evaluation_url": "https://example.com/notify"
  }'
```

### Updating an Existing Application

```bash
curl -X POST "http://localhost:8000/revise" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "secret": "your-secret",
    "task": "todo-app-123",
    "round": 2,
    "nonce": "abc123",
    "brief": "Add dark mode toggle and improve the UI design",
    "checks": [
      "Dark mode toggle works",
      "UI is more polished",
      "Accessibility is improved"
    ],
    "evaluation_url": "https://example.com/notify"
  }'
```

## 🏗️ Architecture

### Core Components

1. **FastAPI Application**: Main web framework with async support
2. **LLM Integration**: OpenAI GPT models for code generation
3. **GitHub Integration**: Repository creation and management
4. **Background Processing**: Asynchronous task handling
5. **Error Handling**: Comprehensive error management and logging

### Scalability Features

- **Async Processing**: Non-blocking operations for better performance
- **Background Tasks**: Long-running operations don't block API responses
- **Retry Mechanisms**: Automatic retry for failed operations
- **Rate Limiting**: Built-in protection against abuse
- **Logging**: Comprehensive logging for monitoring and debugging

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_PAT` | Yes | GitHub Personal Access Token |
| `LLM_API_KEY` | Yes | OpenAI API Key |
| `VERIFICATION_SECRET` | Yes | Secret for request verification |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `LOG_FILE` | No | Log file path (default: app.log) |

### Optional Configuration

- Database integration for task tracking
- Redis for caching and task queues
- Custom domain for GitHub Pages
- Rate limiting configuration

## 📊 Monitoring and Logging

### Health Checks

- `GET /ping` - Simple health check
- `GET /health` - Comprehensive health status including service connectivity

### Logging

- Structured logging with timestamps
- File and console output
- Error tracking and debugging information
- Performance metrics

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Ensure all secrets are properly configured
2. **Database**: Consider adding database integration for task tracking
3. **Monitoring**: Set up application monitoring and alerting
4. **Scaling**: Use multiple workers and load balancing
5. **Security**: Implement rate limiting and request validation

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the logs for error details
2. Verify environment variables are set correctly
3. Ensure GitHub token has required permissions
4. Check OpenAI API key is valid and has credits

## 🔮 Future Enhancements

- Database integration for task tracking
- Redis caching for improved performance
- Webhook support for real-time updates
- Advanced LLM model selection
- Custom domain support for GitHub Pages
- Analytics and metrics dashboard
- Multi-tenant support
- Advanced security features
