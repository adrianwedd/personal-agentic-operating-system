#!/usr/bin/env bash
set -euo pipefail

# Friendly URL cheat-sheet

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
        xdg-open "http://localhost:${LANGFUSE_PORT:-57660}" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "http://localhost:${LANGFUSE_PORT:-57660}" >/dev/null 2>&1 &
    fi
fi
