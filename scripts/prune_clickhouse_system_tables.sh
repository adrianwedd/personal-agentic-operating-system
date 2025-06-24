#!/usr/bin/env bash
set -euo pipefail

# Tune TTL on ClickHouse system tables.
# Options:
#   -d DAYS    retention window in days (default 3)
#   -n         dry-run (just print commands)
#   -l FILE    append output to FILE
#   -c         install daily cron entry

DAYS=3
DRY_RUN=false
LOG_FILE=""
INSTALL_CRON=false

while getopts "d:nlc" opt; do
  case $opt in
    d) DAYS=$OPTARG ;;
    n) DRY_RUN=true ;;
    l) LOG_FILE=$OPTARG ;;
    c) INSTALL_CRON=true ;;
    *) echo "Usage: $0 [-n] [-d DAYS] [-l LOG_FILE] [-c]" >&2; exit 1 ;;
  esac
done

log(){ echo "$1"; [[ -n "$LOG_FILE" ]] && echo "$(date -Is) $1" >> "$LOG_FILE"; }

CH="clickhouse-client --host localhost --user default --password ''"
tables=(
  "system.metric_log"
  "system.trace_log"
  "system.asynchronous_metric_log"
)

for t in "${tables[@]}"; do
  cmd="ALTER TABLE $t MODIFY TTL event_time + INTERVAL ${DAYS} DAY"
  if $DRY_RUN; then
    log "[dry-run] $cmd"
  else
    log "→ Enforcing ${DAYS}-day TTL on $t"
    $CH -q "$cmd"
  fi
done

if $DRY_RUN; then
  for t in "${tables[@]}"; do log "[dry-run] OPTIMIZE TABLE $t FINAL"; done
else
  log "→ Running FINAL OPTIMIZE to reclaim disk"
  for t in "${tables[@]}"; do $CH -q "OPTIMIZE TABLE $t FINAL"; done
fi

if $INSTALL_CRON; then
  crontab -l | grep -q prune_clickhouse_system_tables.sh || (
    (crontab -l 2>/dev/null; echo "0 3 * * * $(pwd)/scripts/prune_clickhouse_system_tables.sh -d ${DAYS} >> ${LOG_FILE:-/var/log/clickhouse_prune.log} 2>&1") | crontab -
  )
  log "Cron entry added for daily run at 03:00"
fi
