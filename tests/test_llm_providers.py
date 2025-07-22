import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch
import pytest
from langchain_core.messages import HumanMessage, AIMessage

from agent.llm_providers import (
    get_default_client,
    OpenAIClient,
    OllamaClient,
    GeminiClient,
    DeepSeekClient,
)

from tests.mocks import (
    DummyChatModel,
    DummyEmbeddingModel,
    DummyGenerativeModel,
    DummyResponse,
)


def test_factory_selects_backend(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "openai")
    with patch.object(OpenAIClient, "__init__", return_value=None) as init:
        client = get_default_client()
        init.assert_called_once()
        assert isinstance(client, OpenAIClient)


def test_openai_chat_invokes_sdk(monkeypatch):
    fake_model = DummyChatModel()
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    with patch("agent.llm_providers.openai_client.ChatOpenAI", return_value=fake_model), \
         patch("agent.llm_providers.openai_client.OpenAIEmbeddings", DummyEmbeddingModel):
        client = OpenAIClient()
    out = client.chat([HumanMessage(content="hi")])
    assert out.content == "ok"
    assert fake_model.invoked

    # stream and embed
    stream = list(client.stream_chat([HumanMessage(content="hi")]))
    assert [m.content for m in stream] == ["ok1", "ok2"]
    assert client.embed(["a", "b"]) == [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]


def test_ollama_client(monkeypatch):
    fake_model = DummyChatModel()
    fake_embed = DummyEmbeddingModel()
    with patch("agent.llm_providers.ollama_client.ChatOllama", return_value=fake_model), \
         patch("agent.llm_providers.ollama_client.OllamaEmbeddings", return_value=fake_embed):
        client = OllamaClient()
    assert client.chat([HumanMessage(content="hi")]).content == "ok"
    assert [m.content for m in client.stream_chat([HumanMessage(content="hi")])] == ["ok1", "ok2"]
    assert client.embed(["t1"]) == [[1.0, 0.0, 0.0]]


def test_gemini_client(monkeypatch):
    dummy_module = type("M", (), {"GenerativeModel": DummyGenerativeModel, "configure": lambda **_: None})
    with patch("agent.llm_providers.gemini_client.genai", dummy_module):
        client = GeminiClient()
    assert client.chat([HumanMessage(content="hi")]).content == "ok"
    stream = list(client.stream_chat([HumanMessage(content="hi")]))
    assert [m.content for m in stream] == ["ok1", "ok2"]
    with pytest.raises(NotImplementedError):
        client.embed(["x"])


def test_deepseek_client(monkeypatch):
    def fake_post(url, headers=None, json=None, stream=False, timeout=None):
        if stream:
            return DummyResponse(lines=["ok1", "ok2"])
        if "embeddings" in url:
            data = {"data": [{"embedding": [1.0, 0.0, 0.0]}]}
        else:
            data = {"choices": [{"message": {"content": "ok"}}]}
        return DummyResponse(json_data=data)

    with patch(
        "agent.llm_providers.deepseek_client.requests.post", side_effect=fake_post
    ):
        client = DeepSeekClient()
        assert client.chat([HumanMessage(content="hi")]).content == "ok"
        assert [m.content for m in client.stream_chat([HumanMessage(content="hi")])] == [
            "ok1",
            "ok2",
        ]
        assert client.embed(["t1"]) == [[1.0, 0.0, 0.0]]
