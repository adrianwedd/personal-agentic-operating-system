# ClickHouse Tuning for Development

ClickHouse's system tables generate frequent background merges which can flood the console when the server runs with a high log level. To keep logs readable on a dev machine, use the custom config below and periodically prune the system tables.

## Configuration

1. Copy `.clickhouse/config.xml` into your container at `/etc/clickhouse-server/config.d/dev-overrides.xml`.
2. Copy `.clickhouse/mutation-pool.xml` into your container at `/etc/clickhouse-server/config.d/10-mutation-pool.xml`.
3. Restart the `clickhouse` service to apply the settings.

These overrides lower the log level, limit background threads and pin mutation pool entries to 8 so ClickHouse 24 starts cleanly.

## Pruning helper

Run `scripts/prune_clickhouse_system_tables.sh` occasionally (or via cron) to enforce the TTL and reclaim disk space. The script now accepts a custom number of days and a dry-run flag:

```bash
$ docker exec clickhouse-server /scripts/prune_clickhouse_system_tables.sh
```

```
./scripts/prune_clickhouse_system_tables.sh -d 7 --dry-run
```
This command would show what changes would be applied with a 7‑day retention. Remove `--dry-run` to execute. The script modifies the TTL on ClickHouse's system logs and performs a `FINAL` optimize.
