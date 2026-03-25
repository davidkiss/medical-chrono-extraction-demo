import os
from agent.llm.provider import get_llm_client, get_structured_llm
from agent.models import MedChronoEvent


def test_get_llm_client_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = get_llm_client()
    assert client is not None


def test_get_llm_client_anthropic(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    client = get_llm_client()
    assert client is not None


def test_get_structured_llm_with_model():
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["LLM_MODEL"] = "gpt-4o"
    os.environ["LLM_TEMPERATURE"] = "0.1"
    llm = get_structured_llm(MedChronoEvent)
    assert llm is not None


def test_default_provider_is_openai(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = get_llm_client()
    assert client is not None


def test_temperature_from_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.5")
    client = get_llm_client()
    assert client is not None


def test_model_from_env_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    client = get_llm_client()
    assert client is not None


def test_model_from_env_anthropic(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "claude-3-opus-20240229")
    client = get_llm_client()
    assert client is not None
