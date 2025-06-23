#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/util_docker_port.sh"

langfuse_port=$(get_host_port langfuse 3000/tcp    "${LANGFUSE_PORT:-57660}")
ch_http_port=$(get_host_port clickhouse 8123/tcp   "${CLICKHOUSE_HTTP_PORT:-57659}")
neo4j_http=$(get_host_port neo4j 7474/tcp          "${NEO4J_HTTP_PORT:-7474}")
ollama_port=$(get_host_port ollama 11434/tcp       "${OLLAMA_PORT:-11434}")
qdrant_port=$(get_host_port qdrant 6333/tcp        "${QDRANT_PORT:-52873}")

echo ""
echo "🌐  Open your browser:"
printf "%-16s →  %s\n"  "Langfuse UI"          "http://localhost:${LANGFUSE_PORT:-57660}"
printf "%-16s →  %s/play\n"  "ClickHouse UI"   "http://localhost:${CLICKHOUSE_HTTP_PORT:-57659}"
printf "%-16s →  %s\n"  "Neo4j Browser"       "http://localhost:${NEO4J_HTTP_PORT:-7474}"
printf "%-16s →  %s\n"  "Ollama REST"         "http://localhost:${OLLAMA_PORT:-11434}"
printf "%-16s →  %s\n"  "Qdrant REST"         "http://localhost:${QDRANT_PORT:-52873}"
printf "%-16s →  %s\n"  "Trace API"          "http://localhost:8000"
printf "%-16s →  %s\n"  "Graph UI"           "http://localhost:5173"

echo ""
echo "Tip: add '--ui' to auto-open Langfuse in your default browser."

if [[ "${1:-}" == "--ui" ]]; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${langfuse_port}" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "http://localhost:${langfuse_port}" >/dev/null 2>&1 &
    fi
fi
