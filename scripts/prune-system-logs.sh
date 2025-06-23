#!/usr/bin/env bash
set -euo pipefail

# Minimal helper: set TTLs and optimize system logs
CH="clickhouse-client --host localhost --user default --password ''"

tables=(
  "system.metric_log"
  "system.trace_log"
  "system.asynchronous_metric_log"
)

for t in "${tables[@]}"; do
  echo "→ Enforcing 3-day TTL on $t"
  $CH -q "ALTER TABLE $t MODIFY TTL event_time + INTERVAL 3 DAY"
done

echo "→ Running FINAL OPTIMIZE to reclaim disk now"
for t in "${tables[@]}"; do
  $CH -q "OPTIMIZE TABLE $t FINAL"
done
