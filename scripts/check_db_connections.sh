#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for PostgreSQL and ClickHouse

PSQL_URI=${DATABASE_URL:-""}
CH_USER=${CLICKHOUSE_USER:-"default"}
CH_PASS=${CLICKHOUSE_PASSWORD:-""}
CH_HOST=${CLICKHOUSE_HOST:-"clickhouse"}
CH_PORT=${CLICKHOUSE_PORT:-9000}
CH_DB=${CLICKHOUSE_DB:-"langfuse"}

if [[ -z "$PSQL_URI" ]]; then
  echo "DATABASE_URL not set" >&2
  exit 1
fi

echo "🔍 Testing PostgreSQL connection..."
psql "$PSQL_URI" -c '\dt' >/dev/null

echo "🔍 Testing ClickHouse connection..."
clickhouse-client --host "$CH_HOST" --port "$CH_PORT" \
  --user "$CH_USER" --password "$CH_PASS" \
  -d "$CH_DB" -q 'SELECT 1' >/dev/null

echo "✅ DB connections OK"
