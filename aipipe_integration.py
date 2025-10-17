"""
AIPipe.org integration for LLM Code Deployment API
This module provides fallback LLM generation using aipipe.org service
"""

import os
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
                # OpenRouter style response may include 'response' or 'output'
                return result.get("response") or result.get("output") or self._get_mock_response(prompt)
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


class DeepSeekClient:
    """Simple client to call OpenRouter / OpenRouter-compatible endpoints (DeepSeek via openrouter.ai)."""

    def __init__(self, key: str = None):
        self.key = key or os.getenv("DeepSeek_Key")
        self.base_url = "https://openrouter.ai/api"

    async def generate_content(self, prompt: str, model: str = "tngtech/deepseek-r1t2-chimera:free") -> str:
        """Generate content using OpenRouter / DeepSeek.

        Returns a string of the model output similar to the other fallbacks.
        """
        try:
            if not self.key:
                logger.warning("No DeepSeek_Key provided, DeepSeekClient will return mock response")
                return self._get_mock_response(prompt)

            headers = {
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }

            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if resp.status_code == 200:
                result = resp.json()
                # Try to extract assistant content (openai/chat style)
                try:
                    choices = result.get("choices") or []
                    if choices:
                        message = choices[0].get("message") or choices[0]
                        # Support different shapes
                        if isinstance(message, dict):
                            return message.get("content") or message.get("text") or json.dumps(result)
                        return str(message)
                except Exception:
                    return json.dumps(result)

                # Fallback to common keys
                return result.get("response") or result.get("output") or json.dumps(result)
            else:
                logger.error(f"DeepSeek API error: {resp.status_code} - {resp.text}")
                return self._get_mock_response(prompt)

        except Exception as e:
            logger.error(f"Error calling DeepSeek/OpenRouter API: {str(e)}")
            return self._get_mock_response(prompt)

    def _get_mock_response(self, prompt: str) -> str:
        return aipipe_client._get_mock_response(prompt)


# Global deepseek client instance
deepseek_client = DeepSeekClient()

def set_aipipe_credentials(token: str, email: str = None):
    """Set aipipe.org credentials"""
    global aipipe_client
    aipipe_client = AIPipeClient(token, email)
    logger.info("AIPipe credentials configured")

async def generate_with_aipipe(prompt: str) -> str:
    """Generate content using aipipe.org fallback"""
    # Try AIPipe first, then DeepSeek as a secondary fallback
    result = await aipipe_client.generate_content(prompt)
    if result and not result.startswith("{") and "Generated Application" not in result[:200]:
        # Best-effort heuristic — if response looks valid, return it
        return result

    # Otherwise try DeepSeek/OpenRouter fallback
    logger.info("Falling back to DeepSeek/OpenRouter for generation")
    return await deepseek_client.generate_content(prompt)
