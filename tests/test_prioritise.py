def test_prioritise_rules():
    from agent.nodes import prioritise
    state = {
        "current_task": {
            "objective": "Transfer $500 – account alert",
            "sender": "alert@trustedbank.com",
            "priority": None,
            "status": "NEW",
        }
    }
    from unittest.mock import patch

    with patch("agent.nodes.add_task"), patch("agent.nodes.get_default_client"):
        new_state = prioritise(state)
    assert new_state["current_task"]["priority"] == "high"
    assert new_state["current_task"]["status"] == "READY"
