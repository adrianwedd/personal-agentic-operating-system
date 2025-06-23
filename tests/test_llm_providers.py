import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage

from agent.llm_providers import get_default_client, OpenAIClient


def test_factory_selects_backend(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "openai")
    with patch.object(OpenAIClient, "__init__", return_value=None) as init:
        client = get_default_client()
        init.assert_called_once()
        assert isinstance(client, OpenAIClient)


def test_openai_chat_invokes_sdk(monkeypatch):
    fake_model = MagicMock()
    fake_model.invoke.return_value = AIMessage(content="hi")
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    with patch("agent.llm_providers.openai_client.ChatOpenAI", return_value=fake_model), \
         patch("agent.llm_providers.openai_client.OpenAIEmbeddings"):
        client = OpenAIClient()
    out = client.chat([HumanMessage(content="hi")])
    assert out.content == "hi"
    assert fake_model.invoke.called
