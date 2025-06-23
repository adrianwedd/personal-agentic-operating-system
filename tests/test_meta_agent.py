import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch, MagicMock
import agent.meta_agent as meta
from langchain_core.messages import AIMessage


def test_meta_agent_updates_guidelines(tmp_path):
    refl_dir = tmp_path / "reflections"
    refl_dir.mkdir()
    f = refl_dir / "log.jsonl"
    f.write_text("{\"task_id\": \"1\", \"result\": \"approved\"}\n")

    patch1 = patch.object(meta, "REFLECT_DIR", str(refl_dir))
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="Be nice")
    with patch1, patch("agent.meta_agent.ChatOllama", return_value=fake_llm):
        meta.run_meta_agent()

    with open("guidelines.txt") as gh:
        assert "Be nice" in gh.read()
