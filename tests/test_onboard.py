import subprocess
import pytest

from scripts.healthcheck import wait_for_stack


def docker_running() -> bool:
    """Return True if Docker daemon is reachable."""
    return subprocess.run("docker info", shell=True, capture_output=True).returncode == 0

@pytest.mark.skipif(not docker_running(), reason="Docker not available")
def test_stack_launch_and_health(monkeypatch):
    """Ensure all core services report healthy when Docker stack is running."""
    ok, _ = wait_for_stack(timeout=30)
    assert ok, "services unhealthy"
