import os, sys, importlib, json
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

agent_tools = importlib.import_module("agent.tools")


def test_build_action_tools_list():
    class T:
        def model_dump(self, *a, **k):
            return {}
    fake_gmail = MagicMock()
    fake_gmail.get_tools.return_value = [T()]
    fake_cal = MagicMock()
    fake_cal.get_tools.return_value = [T()]
    with patch("agent.tools.build_gmail_service", return_value=MagicMock()), \
         patch("agent.tools.build_calendar_service", return_value=MagicMock()), \
         patch("agent.tools.GmailToolkit", return_value=fake_gmail), \
         patch("agent.tools.CalendarToolkit", return_value=fake_cal):
        tools = agent_tools.build_action_tools()
    assert len(tools) == 2


def test_tools_sanitizes_tokens():
    class FakeTool:
        def __init__(self):
            self.api_resource = {"credentials": {"token": "secret"}}
        def model_dump(self, *a, exclude=None, **k):
            if exclude and "api_resource" in exclude:
                return {}
            return {"api_resource": self.api_resource}
    fake_gmail = MagicMock()
    fake_gmail.get_tools.return_value = [FakeTool()]
    with patch("agent.tools.build_gmail_service", return_value=MagicMock()), \
         patch("agent.tools.GmailToolkit", return_value=fake_gmail):
        tools = agent_tools.build_gmail_tools()
    dumped = tools[0].model_dump()
    assert "token" not in json.dumps(dumped)
    assert "api_resource" not in dumped
