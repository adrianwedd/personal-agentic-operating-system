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
printf "%-16s →  http://localhost:%s\n" "Langfuse UI"     "$langfuse_port"
printf "%-16s →  http://localhost:%s/play\n" "ClickHouse UI" "$ch_http_port"
printf "%-16s →  http://localhost:%s\n" "Neo4j Browser"  "$neo4j_http"
printf "%-16s →  http://localhost:%s\n" "Ollama REST"    "$ollama_port"
printf "%-16s →  http://localhost:%s\n" "Qdrant REST"    "$qdrant_port"
echo ""
echo "Tip: add '--ui' to auto-open Langfuse in your default browser."

if [[ "${1:-}" == "--ui" ]]; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${langfuse_port}" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "http://localhost:${langfuse_port}" >/dev/null 2>&1 &
    fi
fi
