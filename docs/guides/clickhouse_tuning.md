# ClickHouse Tuning for Development

ClickHouse's system tables generate frequent background merges which can flood the console when the server runs with a high log level. To keep logs readable on a dev machine, use the custom config below and periodically prune the system tables.

## Configuration

1. Copy `docker/clickhouse/config.xml` into your container at `/etc/clickhouse-server/config.d/dev.xml`.
2. Restart the `clickhouse` service to apply the settings.

The config lowers the log level to `information`, limits background threads and keeps system logs for only three days.

## Pruning helper

Run `scripts/prune-system-logs.sh` occasionally (or via cron) to enforce the 3‑day TTL and reclaim disk space:

```bash
$ docker exec clickhouse-server /scripts/prune-system-logs.sh
```

This script modifies the TTL on ClickHouse's system logs and performs a `FINAL` optimize.
