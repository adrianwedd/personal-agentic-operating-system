#!/usr/bin/env bash
set -euo pipefail

# Helper: resolve host port for a compose service
# $1 - service name in docker-compose
# $2 - container port spec, e.g. 3000/tcp
# $3 - default port if lookup fails
get_host_port() {
    docker compose port "$1" "$2" 2>/dev/null | \
        awk -F':' 'NF==2 {print $2; exit}' |
        { read -r p && [[ -n "$p" ]] && echo "$p" || echo "$3"; }
}
