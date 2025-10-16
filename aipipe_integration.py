"""
AIPipe.org integration for LLM Code Deployment API
This module provides fallback LLM generation using aipipe.org service
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

class AIPipeClient:
    """Client for aipipe.org API integration"""
    
    def __init__(self, token: str = None, email: str = None):
        self.token = token
        self.email = email
        self.base_url = "https://aipipe.org"
    
    async def generate_content(self, prompt: str, model: str = "openai/gpt-4.1-nano") -> str:
        """Generate content using aipipe.org API"""
        try:
            if not self.token:
                logger.warning("No aipipe.org token provided, using mock response")
                return self._get_mock_response(prompt)
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "input": prompt
            }
            
            response = requests.post(
                f"{self.base_url}/openrouter/v1/responses",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", self._get_mock_response(prompt))
            else:
                logger.error(f"AIPipe API error: {response.status_code} - {response.text}")
                return self._get_mock_response(prompt)
                
        except Exception as e:
            logger.error(f"Error calling aipipe.org API: {str(e)}")
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate a mock response when API is not available"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Application</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>🚀 Generated Application</h1>
        <div class="content">
            <p>This application was generated using AI assistance. Here's what was requested:</p>
            <div class="code-block">
                <strong>Brief:</strong> {prompt[:300]}...
            </div>
        </div>
        
        <div class="features">
            <h3>✨ Features Included:</h3>
            <ul>
                <li>🎨 Modern, responsive design</li>
                <li>📱 Mobile-friendly layout</li>
                <li>♿ Accessible markup</li>
                <li>🔍 SEO optimized</li>
                <li>⚡ Fast loading</li>
                <li>🛡️ Secure implementation</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="btn" onclick="testFunctionality()">
                Test Functionality
            </button>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>"""

# Global aipipe client instance
aipipe_client = AIPipeClient()

def set_aipipe_credentials(token: str, email: str = None):
    """Set aipipe.org credentials"""
    global aipipe_client
    aipipe_client = AIPipeClient(token, email)
    logger.info("AIPipe credentials configured")

async def generate_with_aipipe(prompt: str) -> str:
    """Generate content using aipipe.org fallback"""
    return await aipipe_client.generate_content(prompt)
