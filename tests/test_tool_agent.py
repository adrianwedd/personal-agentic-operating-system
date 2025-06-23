import os, sys, importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from unittest.mock import patch, MagicMock

from langchain_core.messages import HumanMessage, AIMessage

tool_agent = importlib.import_module("tool_agent")
build_tools = tool_agent.build_tools
main = tool_agent.main


def test_build_tools():
    fake_gmail = MagicMock()
    fake_gmail.get_tools.return_value = ["g"]
    fake_cal = MagicMock()
    fake_cal.get_tools.return_value = ["c"]
    with patch("tool_agent.GmailToolkit", return_value=fake_gmail), \
         patch("tool_agent.CalendarToolkit", return_value=fake_cal):
        tools = build_tools()
    assert tools == ["g", "c"]


def test_main_print(capsys):
    fake_agent = MagicMock()
    fake_agent.invoke.return_value = {"messages": [HumanMessage(content="hi"), AIMessage(content="pong")]}
    with patch("tool_agent.build_agent", return_value=fake_agent), \
         patch("tool_agent.Langfuse"), \
         patch("tool_agent.CallbackHandler"):
        main("hello")
    captured = capsys.readouterr()
    assert "pong" in captured.out
