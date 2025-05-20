from src.utils.openai_client import get_llm_client, OpenAILLMClient
from src.utils.llm_client import NoopLLMClient


def test_llm_factory_without_key(monkeypatch):
    # Mock settings to have no API key
    class MockSettings:
        class LLM:
            api_key = None
        llm = LLM()
    
    monkeypatch.setattr("src.utils.openai_client.get_settings", lambda: MockSettings())
    
    client = get_llm_client()
    assert isinstance(client, NoopLLMClient)


def test_llm_factory_with_key(monkeypatch):
    # Mock settings to have an API key
    class MockSettings:
        class LLM:
            api_key = "test-key"
            model = "gpt-3.5-turbo"
        llm = LLM()
    
    monkeypatch.setattr("src.utils.openai_client.get_settings", lambda: MockSettings())
    
    client = get_llm_client()
    assert isinstance(client, OpenAILLMClient)
    assert client.api_key == "test-key"


def test_openai_client_fallback():
    # Test that OpenAI client returns fallback on error
    client = OpenAILLMClient(api_key="invalid-key")
    result = client.complete("test prompt")
    # Should return fallback string since API call will fail
    assert isinstance(result, str)
    assert len(result) > 0
