import os, sys, importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from unittest.mock import patch, MagicMock

from langchain_core.messages import HumanMessage, AIMessage

minimal_agent = importlib.import_module("minimal_agent")
ollama_step = minimal_agent.ollama_step
main = minimal_agent.main


def test_ollama_step():
    state = {"messages": [HumanMessage(content="hi")]}
    fake_llm = MagicMock()
    fake_llm.chat.return_value = AIMessage(content="pong")
    with patch("minimal_agent.get_default_client", return_value=fake_llm):
        new_state = ollama_step(state)
    assert new_state["messages"][-1].content == "pong"


def test_main_print(capsys):
    fake_llm = MagicMock()
    fake_llm.chat.return_value = AIMessage(content="pong")
    with patch("minimal_agent.get_default_client", return_value=fake_llm), \
         patch("minimal_agent.Langfuse"), \
         patch("minimal_agent.CallbackHandler"):
        main("hi")
    captured = capsys.readouterr()
    assert "pong" in captured.out
