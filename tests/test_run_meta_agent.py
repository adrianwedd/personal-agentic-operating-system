import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch
import scripts.run_meta_agent as rma


def test_append_log(tmp_path):
    rma.LOG_FILE = str(tmp_path / "meta.log")
    rma._append_log("hello")
    assert os.path.exists(rma.LOG_FILE)
    with open(rma.LOG_FILE) as fh:
        line = fh.read().strip()
    assert "hello" in line


def test_main_show_last(capsys, tmp_path):
    rma.LOG_FILE = str(tmp_path / "meta.log")
    with open(rma.LOG_FILE, "w") as fh:
        fh.write("2024-01-01 foo\n2024-01-02 bar\n")
    rma.main(show_last=True)
    captured = capsys.readouterr()
    assert "bar" in captured.out


def test_main_runs_and_logs(tmp_path):
    rma.LOG_FILE = str(tmp_path / "meta.log")
    with patch("scripts.run_meta_agent.run_meta_agent", return_value="new rule"):
        rma.main()
    with open(rma.LOG_FILE) as fh:
        data = fh.read()
    assert "new rule" in data

