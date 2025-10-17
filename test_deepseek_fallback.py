import os
import asyncio

# Ensure our module path
import sys
sys.path.append(r'c:\Users\siban\OneDrive\Documents\Desktop\project_tds2\project1-tds')

from main import generate_app_code, openai_client
from aipipe_integration import deepseek_client

async def run_test():
    # Force OpenAI client to None to exercise fallback path
    # Note: this modifies in-memory openai_client only for the test
    import main as m
    m.openai_client = None

    # If no DeepSeek key is present, warn but continue to call (will return mock)
    if not deepseek_client.key:
        print('No DeepSeek_Key configured; DeepSeek client will return mock response')

    files = await generate_app_code('A minimal app that says hello', [], [])
    print('Generated files:', list(files.keys()))
    print('index.html preview:\n', files['index.html'][:400])

async def test_round1_fallback():
    """Simulate round 1 codegen with DeepSeek fallback."""
    import main as m
    m.openai_client = None
    # Monkeypatch aipipe to return JSON-like error to trigger DeepSeek
    import aipipe_integration as ai
    async def fake_aipipe(prompt):
        return '{"error": "rate_limited"}'
    ai.generate_with_aipipe = fake_aipipe
    class FakeDeep:
        async def generate_content(self, prompt, model=''):
            return '<html>DeepSeek round1 result</html>'
    ai.deepseek_client = FakeDeep()
    files = await m.generate_app_code('Round 1 brief', [], [])
    print('Round 1 files:', list(files.keys()))
    print('Round 1 index.html preview:\n', files['index.html'][:400])

async def test_round2_fallback():
    """Simulate round 2 revision with DeepSeek fallback."""
    import main as m
    m.openai_client = None
    import aipipe_integration as ai
    async def fake_aipipe(prompt):
        return '{"error": "rate_limited"}'
    ai.generate_with_aipipe = fake_aipipe
    class FakeDeep:
        async def generate_content(self, prompt, model=''):
            return '<html>DeepSeek round2 result</html>'
    ai.deepseek_client = FakeDeep()
    files = await m.generate_app_code('Round 2 brief', [], [])
    print('Round 2 files:', list(files.keys()))
    print('Round 2 index.html preview:\n', files['index.html'][:400])

if __name__ == '__main__':
    print('--- ROUND 1 TEST ---')
    asyncio.run(test_round1_fallback())
    print('\n--- ROUND 2 TEST ---')
    asyncio.run(test_round2_fallback())
