#!/usr/bin/env bash
# ————————————————————
# 🧠 Personal Agentic Operating System · interactive bootstrap
# ————————————————————
# Author: Codex generator  |  License: MIT
# Goal : One-command, cross-platform onboarding for devs.
# ————————————————————

set -euo pipefail
IFS=$'\n\t'

bold()   { printf '\033[1m%s\033[0m\n' "$1"; }
green()  { printf '\033[32m%s\033[0m\n' "$1"; }
yellow() { printf '\033[33m%s\033[0m\n' "$1"; }
dim()    { printf '\033[2m%s\033[0m\n' "$1"; }

bold ""
bold "🔧  Welcome to the Personal Agentic Operating System bootstrap wizard!"
dim  "    (This script is safe to re-run; it never overwrites user data.)"

# 1️⃣  Detect platform
OS=$(uname -s)
ARCH=$(uname -m)
green "🧭  Detected  : $OS / $ARCH"

# 2️⃣  Docker check
if ! command -v docker &> /dev/null; then
    yellow "🚫 Docker not found. Please install Docker Desktop:"
    yellow "   https://docs.docker.com/get-docker/"
    exit 1
fi
docker info >/dev/null 2>&1 || { yellow "⚠ Docker daemon not running? Start it and retry."; exit 1; }
green "✅ Docker is running."

# 3️⃣  Docker Compose plugin
if ! docker compose version >/dev/null 2>&1; then
    yellow "🚫 Docker Compose plugin missing."
    exit 1
fi
green "✅ Docker Compose is available."

# 4️⃣  Python (optional but recommended)
if ! command -v python3 &> /dev/null; then
    yellow "⚠️  python3 not on PATH – agent CLI will be unavailable."
else
    PY=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    green "🐍 Python     : $PY"
fi

# 5️⃣  .env generation
if [[ ! -f .env ]]; then
    yellow "📄  Creating fresh .env from template…"
    cp .env.example .env
    # --- generate one-time secrets if not present ---
    {
        grep -q "^NEXTAUTH_SECRET=" .env || \
            echo "NEXTAUTH_SECRET=$(openssl rand -hex 16)" >> .env
        grep -q "^SALT=" .env || \
            echo "SALT=$(openssl rand -hex 16)" >> .env
    }
    sed -i'' "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 8)/" .env 2>/dev/null || \
        sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 8)/" .env
    sed -i'' "s|NEO4J_AUTH=.*|NEO4J_AUTH=neo4j/$(openssl rand -hex 8)|" .env 2>/dev/null || \
        sed -i "s|NEO4J_AUTH=.*|NEO4J_AUTH=neo4j/$(openssl rand -hex 8)|" .env
    sed -i'' "s/CLICKHOUSE_PASSWORD=.*/CLICKHOUSE_PASSWORD=$(openssl rand -hex 8)/" .env 2>/dev/null || \
        sed -i "s/CLICKHOUSE_PASSWORD=.*/CLICKHOUSE_PASSWORD=$(openssl rand -hex 8)/" .env
    green "✅ .env created – customise anytime."
else
    green "📄  Existing .env detected – keeping your settings."
    if grep -q "^NEXTAUTH_SECRET=$" .env || ! grep -q "^NEXTAUTH_SECRET=" .env; then
        echo "NEXTAUTH_SECRET=$(openssl rand -hex 16)" >> .env
    fi
    if grep -q "^SALT=$" .env || ! grep -q "^SALT=" .env; then
        echo "SALT=$(openssl rand -hex 16)" >> .env
    fi
    if grep -q "^NEO4J_AUTH=$" .env || ! grep -q "^NEO4J_AUTH=" .env; then
        echo "NEO4J_AUTH=neo4j/$(openssl rand -hex 8)" >> .env
    fi
    if grep -q "^CLICKHOUSE_PASSWORD=$" .env || ! grep -q "^CLICKHOUSE_PASSWORD=" .env; then
        echo "CLICKHOUSE_PASSWORD=$(openssl rand -hex 8)" >> .env
    fi
fi

# 👷 Copy dev ClickHouse config
echo "\ud83d\udd27  Applying dev-friendly ClickHouse config..."
mkdir -p .clickhouse
cp docker/clickhouse/config.xml .clickhouse/config.xml
cp clickhouse-mutation-pool.xml .clickhouse/mutation-pool.xml
echo "\u26a0\ufe0f  Langfuse v3+ uses ClickHouse and requires manual DB config."
echo "\u2139\ufe0f  ClickHouse config applied: .clickhouse/config.xml"
echo "\u2139\ufe0f  Mutation pool override: .clickhouse/mutation-pool.xml"
echo "   For pruning logs: bash scripts/prune_clickhouse_system_tables.sh"

# 6️⃣  ARM warning for Langfuse < 2.58
if [[ "$ARCH" == "arm64" ]]; then
    dim "ℹ️  ARM Mac detected – using multi-arch Langfuse ≥ 2.58."
fi

# 7️⃣  Pull & launch containers
bold ""
bold "🚀  Launching Docker stack (this may take a few minutes on first run)…"
docker compose pull --quiet
docker compose up -d --wait

# 8️⃣  Post-launch summary
bold ""
green "🎉  All services requested. Quick status:"
docker compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"

# Friendly URL cheat-sheet
scripts/print_service_urls.sh "$@"

bold ""
bold "👟  Next steps"
cat <<EOT
1. Load a model into Ollama, e.g.:  ollama pull llama3:8b
2. Try ingestion:                   python ingestion/ingest.py ~/docs
3. Run the agent:                   python agent/run.py --task "Who emailed me today?"

Docs:   https://adrianwedd.github.io/personal-agentic-operating-system
EOT

green ""
green "✅  Bootstrap complete – happy hacking!"

