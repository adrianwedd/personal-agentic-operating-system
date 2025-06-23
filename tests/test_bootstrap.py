def test_human_approval(tmp_path):
    from agent import graph

    graph.HITL_DIR = tmp_path
    state = {"current_task": {"task_id": "t1"}}
    graph.human_approval(state)
    assert (tmp_path / "t1.json").exists()
