from scripts.healthcheck import wait_for_stack

def test_stack_launch_and_health(monkeypatch):
    # Assume docker compose already running in CI
    ok, _ = wait_for_stack(timeout=30)
    assert ok, "services unhealthy"
