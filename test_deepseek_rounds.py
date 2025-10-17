import asyncio
import pytest
import sys
sys.path.append(r'c:\Users\siban\OneDrive\Documents\Desktop\project_tds2\project1-tds')

import main
import aipipe_integration

pytest_plugins = ('pytest_asyncio',)

class DummyTaskRequest:
    def __init__(self, brief, round_num):
        self.email = 'test@example.com'
        self.secret = main.VERIFICATION_SECRET
        self.task = 'testtask'
        self.round = round_num
        self.nonce = '12345678'
        self.brief = brief
        self.checks = []
        self.evaluation_url = 'http://localhost/eval'
        self.attachments = []

@pytest.mark.asyncio
async def test_round1_fallback(monkeypatch):
    """Test round 1 (initial codegen) with fallback to DeepSeek."""
    monkeypatch.setattr(main, 'openai_client', None)
    async def fake_aipipe(prompt):
        return '{"error": "rate_limited"}'
    monkeypatch.setattr(aipipe_integration, 'generate_with_aipipe', fake_aipipe)
    class FakeDeep:
        async def generate_content(self, prompt, model=''):
            return '<html>DeepSeek round1 result</html>'
    monkeypatch.setattr(aipipe_integration, 'deepseek_client', FakeDeep())
    files = await main.generate_app_code('Round 1 brief', [], [])
    assert 'index.html' in files
    assert 'DeepSeek round1 result' in files['index.html']

@pytest.mark.asyncio
async def test_round2_revision_fallback(monkeypatch):
    """Test round 2 (revision) with fallback to DeepSeek."""
    monkeypatch.setattr(main, 'openai_client', None)
    async def fake_aipipe(prompt):
        return '{"error": "rate_limited"}'
    monkeypatch.setattr(aipipe_integration, 'generate_with_aipipe', fake_aipipe)
    class FakeDeep:
        async def generate_content(self, prompt, model=''):
            return '<html>DeepSeek round2 result</html>'
    monkeypatch.setattr(aipipe_integration, 'deepseek_client', FakeDeep())
    # Simulate revision background process
    task_request = DummyTaskRequest('Round 2 brief', round_num=2)
    # Directly call generate_app_code for revision logic
    files = await main.generate_app_code(task_request.brief, task_request.checks, task_request.attachments)
    assert 'index.html' in files
    assert 'DeepSeek round2 result' in files['index.html']
