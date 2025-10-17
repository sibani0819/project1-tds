import sys
import asyncio
import pytest

# ensure package path
sys.path.append(r'c:\Users\siban\OneDrive\Documents\Desktop\project_tds2\project1-tds')

import main
import aipipe_integration

@pytest.mark.asyncio
async def test_openai_success(monkeypatch):
    # Fake OpenAI response object
    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChoice:
        def __init__(self, content):
            self.message = FakeMessage(content)

    class FakeResponse:
        def __init__(self, content):
            self.choices = [FakeChoice(content)]

    # Fake client with chat.completions.create
    class FakeCompletions:
        @staticmethod
        def create(*args, **kwargs):
            return FakeResponse('<html><body>OPENAI GENERATED</body></html>')

    class FakeChat:
        completions = FakeCompletions()

    fake_client = type('C', (), {'chat': FakeChat()})()

    monkeypatch.setattr(main, 'openai_client', fake_client)

    files = await main.generate_app_code('Brief for openai success', [], [])

    assert 'index.html' in files
    assert 'OPENAI GENERATED' in files['index.html']

@pytest.mark.asyncio
async def test_openai_failure_uses_aipipe(monkeypatch):
    # Make OpenAI client raise error
    class BadCompletions:
        @staticmethod
        def create(*args, **kwargs):
            raise Exception('quota')

    class BadChat:
        completions = BadCompletions()

    bad_client = type('C', (), {'chat': BadChat()})()
    monkeypatch.setattr(main, 'openai_client', bad_client)

    # Patch generate_with_aipipe to return a simple HTML string
    async def fake_aipipe(prompt):
        return '<html><body>AIPIPE GENERATED</body></html>'

    monkeypatch.setattr(aipipe_integration, 'generate_with_aipipe', fake_aipipe)

    files = await main.generate_app_code('Brief for aipipe fallback', [], [])

    assert 'index.html' in files
    assert 'AIPIPE GENERATED' in files['index.html']

@pytest.mark.asyncio
async def test_aipipe_json_triggers_deepseek(monkeypatch):
    # Force no OpenAI client
    monkeypatch.setattr(main, 'openai_client', None)

    # Patch aipipe_client.generate_content to return JSON-like string so generate_with_aipipe will delegate to deepseek
    async def fake_aipipe_gen(prompt):
        return '{"error": "invalid"}'

    async def fake_deepseek_gen(prompt):
        return '<html><body>DEEPSEEK GENERATED</body></html>'

    monkeypatch.setattr(aipipe_integration.aipipe_client, 'generate_content', fake_aipipe_gen)
    monkeypatch.setattr(aipipe_integration, 'deepseek_client', aipipe_integration.deepseek_client)
    monkeypatch.setattr(aipipe_integration.deepseek_client, 'generate_content', fake_deepseek_gen)

    files = await main.generate_app_code('Brief for deepseek fallback', [], [])

    assert 'index.html' in files
    assert 'DEEPSEEK GENERATED' in files['index.html']
