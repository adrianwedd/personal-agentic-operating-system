import os
import time
from pathlib import Path

import pytest
from clickhouse_driver import Client
from testcontainers.core.container import DockerContainer

CLICKHOUSE_IMAGE = os.getenv("CLICKHOUSE_IMAGE", "clickhouse/clickhouse-server:23.10")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "docker" / "clickhouse" / "config.xml"
PRUNE_SCRIPT = PROJECT_ROOT / "scripts" / "prune_clickhouse_system_tables.sh"


def _wait_for_clickhouse(host: str, port: int, *, timeout: int = 60):
    start = time.time()
    last_exc = None
    while time.time() - start < timeout:
        try:
            client = Client(host=host, port=port)
            client.execute("SELECT 1")
            return
        except Exception as exc:
            last_exc = exc
            time.sleep(0.5)
    raise RuntimeError("ClickHouse did not become ready in time") from last_exc


@pytest.mark.skipif(not CONFIG_FILE.exists(), reason="dev config not found")
@pytest.mark.skipif(not PRUNE_SCRIPT.exists(), reason="prune script not found")
def test_dev_clickhouse_defaults():
    with DockerContainer(CLICKHOUSE_IMAGE) as ch:
        ch.with_volume_mapping(
            str(CONFIG_FILE), "/etc/clickhouse-server/config.d/dev.xml"
        )
        ch.with_volume_mapping(str(PRUNE_SCRIPT), "/prune_clickhouse_system_tables.sh")
        ch.with_command("--config-file=/etc/clickhouse-server/config.xml")
        ch.with_exposed_ports(9000)

        ch.start()
        host = ch.get_container_host_ip()
        port = int(ch.get_exposed_port("9000"))

        _wait_for_clickhouse(host, port)
        client = Client(host=host, port=port)

        bg_pool = int(
            client.execute(
                "SELECT value FROM system.settings WHERE name = 'background_pool_size'"
            )[0][0]
        )
        assert bg_pool == 4, f"background_pool_size expected 4, got {bg_pool}"

        parts_to_delay = int(
            client.execute(
                "SELECT value FROM system.merge_tree_settings WHERE name='parts_to_delay_insert'"
            )[0][0]
        )
        parts_to_throw = int(
            client.execute(
                "SELECT value FROM system.merge_tree_settings WHERE name='parts_to_throw_insert'"
            )[0][0]
        )
        assert parts_to_delay == 300 and parts_to_throw == 600

        ttl_expr_before = client.execute(
            """
            SELECT engine_full
            FROM system.tables
            WHERE database = 'system' AND name = 'metric_log'
            """
        )[0][0]
        assert "TTL event_time + toIntervalDay(3)" in ttl_expr_before

        exit_code, output = ch.exec(["bash", "/prune_clickhouse_system_tables.sh"])
        assert exit_code == 0, f"prune script failed: {output}"

        parts = client.execute(
            """
            SELECT count()
            FROM system.parts
            WHERE database = 'system' AND table = 'metric_log' AND active
            """
        )[0][0]
        assert parts <= 2, f"metric_log still too fragmented: {parts} active parts"
