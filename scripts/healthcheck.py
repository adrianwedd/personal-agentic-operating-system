"""
Tiny service-level health-checker for docker-compose stack.
Used by onboard.py and CI smoke tests.
"""
import time, json, subprocess as sp
from typing import Tuple

SERVICES = {
    "ollama"  : ("http://localhost:11434/api/tags",       '"models"'),
    "qdrant"  : ("http://localhost:6333/collections",     '"result"'),
    "postgres": ("docker exec postgres pg_isready",       "accepting"),
    "neo4j"   : ("http://localhost:7474",                 "HTTP/1.1 200"),
    "langfuse": ("http://localhost:3000/api/health",      '"status":"ok"'),
}

def _curl(url: str) -> Tuple[int,str]:
    res = sp.run(f"curl -s -m 3 -I {url}", shell=True,
                 capture_output=True, text=True)
    return res.returncode, res.stdout + res.stderr

def wait_for_stack(timeout: int = 120) -> Tuple[bool,str]:
    start = time.time()
    while time.time() - start < timeout:
        failed = []
        for svc,(probe,needle) in SERVICES.items():
            if probe.startswith("http"):
                code, out = _curl(probe)
            else:
                code, out = sp.getstatusoutput(probe)
            if code != 0 or needle not in out:
                failed.append((svc,out.strip()[:120]))
        if not failed:
            return True, "all good"
        time.sleep(3)
    report = "\n".join(f"• {svc}: {msg}" for svc,msg in failed)
    return False, report
