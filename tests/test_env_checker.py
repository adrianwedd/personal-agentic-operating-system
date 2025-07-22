from pathlib import Path
from scripts.check_env import missing_vars, main


def test_detects_missing(tmp_path, capsys):
    ex = tmp_path / '.env.example'
    env = tmp_path / '.env'
    ex.write_text('A=1\nB=2\n')
    env.write_text('A=1\n')
    assert missing_vars(ex, env) == ['B']
    main(str(ex), str(env))
    out = capsys.readouterr().out
    assert 'B' in out


def test_all_set(tmp_path, capsys):
    ex = tmp_path / '.env.example'
    env = tmp_path / '.env'
    ex.write_text('A=1\nB=2\n')
    env.write_text('A=1\nB=2\n')
    assert missing_vars(ex, env) == []
    main(str(ex), str(env))
    out = capsys.readouterr().out
    assert 'All required env vars set' in out
