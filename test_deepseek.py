import asyncio
import pytest

# Ensure the project path is importable
import sys
sys.path.append(r'c:\Users\siban\OneDrive\Documents\Desktop\project_tds2\project1-tds')

import main
import aipipe_integration

pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_openai_success(monkeypatch):
    """When OpenAI client is available and returns content, generate_app_code should use it."""
    class FakeChoice:
        def __init__(self, content):
            self.message = type('M', (), {'content': content})

    class FakeResponse:
        def __init__(self, content):
            self.choices = [type('C', (), {'message': type('M', (), {'content': content})})()]

    async def fake_create(**kwargs):
        return FakeResponse('<html>OpenAI result</html>')

    # Monkeypatch the openai_client to have chat.completions.create
    fake_openai = type('O', (), {})()
    fake_openai.chat = type('Chat', (), {})()
    fake_openai.chat.completions = type('Comp', (), {})()
    fake_openai.chat.completions.create = lambda **kwargs: FakeResponse('<html>OpenAI result</html>')

    monkeypatch.setattr(main, 'openai_client', fake_openai)

    files = await main.generate_app_code('brief', [], [])
    assert 'index.html' in files
    assert 'OpenAI result' in files['index.html']

@pytest.mark.asyncio
async def test_openai_failure_aipipe_success(monkeypatch):
    """If OpenAI errors, AIPipe should be used and successful output returned."""
    # Force OpenAI client to raise
    class BadOpenAI:
        chat = type('Chat', (), {})()
        def __init__(self):
            pass
    def raise_exc(*args, **kwargs):
        raise Exception('quota')
    bad_openai = BadOpenAI()
    bad_openai.chat.completions = type('c', (), {})()
    bad_openai.chat.completions.create = raise_exc

    monkeypatch.setattr(main, 'openai_client', bad_openai)

    # Mock aipipe_integration.generate_with_aipipe to return a known HTML string
    async def fake_aipipe(prompt):
        return '<html>AIPipe result</html>'

    monkeypatch.setattr(aipipe_integration, 'generate_with_aipipe', fake_aipipe)

    files = await main.generate_app_code('brief', [], [])
    assert 'index.html' in files
    assert 'AIPipe result' in files['index.html']

@pytest.mark.asyncio
async def test_aipipe_failure_deepseek_success(monkeypatch):
    """If AIPipe returns a JSON-like object or fails, DeepSeek should be attempted and used."""
    # Ensure openai_client is None so flow goes to aipipe
    monkeypatch.setattr(main, 'openai_client', None)

    # Mock aipipe to return a small JSON-ish string that signals fallback
    async def fake_aipipe(prompt):
        # return something that doesn't look like HTML, to trigger deepseek in our heuristic
        return '{"error": "rate_limited"}'

    monkeypatch.setattr(aipipe_integration, 'generate_with_aipipe', fake_aipipe)

    # Mock deepseek_client.generate_content to return HTML
    class FakeDeep:
        async def generate_content(self, prompt, model=''):
            return '<html>DeepSeek result</html>'

    monkeypatch.setattr(aipipe_integration, 'deepseek_client', FakeDeep())

    files = await main.generate_app_code('brief', [], [])
    assert 'index.html' in files
    assert 'DeepSeek result' in files['index.html']
