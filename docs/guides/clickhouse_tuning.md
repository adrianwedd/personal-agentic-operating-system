# ClickHouse Tuning for Development

ClickHouse's system tables generate frequent background merges which can flood the console when the server runs with a high log level. To keep logs readable on a dev machine, use the custom config below and periodically prune the system tables.

## Configuration

1. Copy `docker/clickhouse/config.xml` into your container at `/etc/clickhouse-server/config.d/dev.xml`.
2. Copy `clickhouse-mutation-pool.xml` into your container at `/etc/clickhouse-server/config.d/10-mutation-pool.xml`.
3. Restart the `clickhouse` service to apply the settings.

These overrides lower the log level, limit background threads and pin mutation pool entries to 8 so ClickHouse 24 starts cleanly.

## Pruning helper

Run `scripts/prune_clickhouse_system_tables.sh` occasionally (or via cron) to enforce the 3‑day TTL and reclaim disk space:

```bash
$ docker exec clickhouse-server /scripts/prune_clickhouse_system_tables.sh
```

This script modifies the TTL on ClickHouse's system logs and performs a `FINAL` optimize.
