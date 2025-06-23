#!/usr/bin/env python3
"""
Interactive bootstrap wizard for the Personal Agentic Operating System.

✦  Runs on macOS/Linux (ARM & x86_64)
✦  Guides the user through:
    • Docker checks
    • .env creation / patching
    • Selecting LLM providers (Ollama, OpenAI, Gemini, DeepSeek)
    • Auto-choosing a local model based on available RAM
    • First-run health check with intelligent log diagnostics
"""
from __future__ import annotations
import os, sys, re, json, platform, shutil, subprocess as sp
from pathlib import Path
from textwrap import dedent
import psutil         # pulled in by requirements.txt
from rich            import print
from rich.prompt     import Prompt, Confirm
from rich.progress   import Progress, SpinnerColumn, TextColumn

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE  = REPO_ROOT / ".env"
ENV_EX    = REPO_ROOT / ".env.example"

###############################################################################
# Helper utilities
###############################################################################

def sh(cmd: str, **kw) -> tuple[int, str]:
    """Run shell command & capture output."""
    res = sp.run(cmd, shell=True, capture_output=True, text=True, **kw)
    return res.returncode, res.stdout.strip() + res.stderr.strip()

def docker_ok() -> bool:
    return sh("docker info")[0] == 0

def compose_ok() -> bool:
    return sh("docker compose version")[0] == 0

def ensure_env() -> None:
    if ENV_FILE.exists():
        print("[bold green]✓[/] .env already exists – keeping your settings.")
        return
    shutil.copyfile(ENV_EX, ENV_FILE)
    print("[bold yellow]⚠︎[/] No .env found → copied from template.")
    # minimal defaults
    with ENV_FILE.open("a") as f:
        f.write("\nNEXTAUTH_SECRET=changeme\nSALT=changeme\n")

def patch_env(key: str, value: str) -> None:
    txt = ENV_FILE.read_text()
    if re.search(fr"^{key}=", txt, re.M):
        txt = re.sub(fr"^{key}=.*$", f"{key}={value}", txt, flags=re.M)
    else:
        txt += f"\n{key}={value}"
    ENV_FILE.write_text(txt)

def patch_langfuse_image_if_needed() -> None:
    """Downgrade Langfuse image when ClickHouse is unset."""
    txt = ENV_FILE.read_text()
    match = re.search(r"^CLICKHOUSE_URL=(.*)$", txt, re.M)
    if not match or not match.group(1).strip():
        suffix = "2.58.0-arm64" if platform.machine() in {"arm64", "aarch64"} else "2.58.0"
        patch_env("LANGFUSE_IMAGE", f"ghcr.io/langfuse/langfuse:{suffix}")

def suggest_local_model() -> str:
    """Return smallest model usable by Ollama given RAM."""
    gibs = psutil.virtual_memory().total / 2**30
    if gibs < 4:
        return "phi3:mini"
    if gibs < 8:
        return "llama3.2:3b"
    return "gemma3:4b"

###############################################################################
# Interactive steps
###############################################################################

def step_checks() -> None:
    print("\n[bold]🔧  System checks[/bold]")
    if not docker_ok():
        print("[red]✖ Docker daemon not running. Start Docker and re-run.[/]")
        sys.exit(1)
    if not compose_ok():
        print("[red]✖ docker compose not available.[/]")
        sys.exit(1)
    print("[green]✓ Docker + Compose OK[/]")

def step_llm() -> None:
    print("\n[bold]🧠  LLM back-ends[/bold]")
    providers = {
        "1": "Local Ollama only",
        "2": "Ollama + OpenAI",
        "3": "Ollama + Google Gemini",
        "4": "Ollama + DeepSeek",
        "5": "Everything (Ollama, OpenAI, Gemini, DeepSeek)"
    }
    for k, v in providers.items():
        print(f"  {k}. {v}")
    choice = Prompt.ask("Select provider set", choices=list(providers), default="1")
    if choice != "1":
        print("[yellow]→ Remember to insert your API keys in .env later.[/]")

    # Write ENV flags
    patch_env("USE_OPENAI",   "true" if choice in {"2","5"} else "false")
    patch_env("USE_GEMINI",   "true" if choice in {"3","5"} else "false")
    patch_env("USE_DEEPSEEK", "true" if choice in {"4","5"} else "false")

def step_model() -> None:
    print("\n[bold]📦  Local model selection (Ollama)[/bold]")
    default_model = suggest_local_model()
    model = Prompt.ask("Model to pull", default=default_model)
    patch_env("OLLAMA_DEFAULT_MODEL", model)

def step_stack() -> None:
    print("\n[bold]🚀  Launching Docker stack[/bold]")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as prog:
        task = prog.add_task("docker compose up – pulling images…", start=False)
        prog.start_task(task)
        code, out = sh("docker compose up -d --pull always")
        prog.stop()
    if code != 0:
        print(out)
        print("[red]✖ docker compose failed.[/]")
        sys.exit(1)

def step_health() -> None:
    from healthcheck import wait_for_stack   # local import after deps installed
    print("\n[bold]🩺  Health check[/bold]")
    ok, report = wait_for_stack(timeout=120)
    if ok:
        print("[green]✓ All services healthy![/]")
    else:
        print("[red]✖ Some containers unhealthy.[/]")
        print(report)
        sys.exit(1)

###############################################################################
# Main
###############################################################################

def main() -> None:
    print(dedent("""
        [bold cyan]
        🛠  Personal Agentic OS • Interactive Bootstrap Wizard
        -----------------------------------------------
        [/bold cyan]"""))
    step_checks()
    ensure_env()
    patch_langfuse_image_if_needed()
    step_llm()
    step_model()
    step_stack()
    step_health()
    print("\n[bold green]🎉  Setup complete![/]")
    print("Dashboards:")
    print("• Langfuse  : http://localhost:3000")
    print("• Neo4j     : http://localhost:7474")
    print("• Qdrant UI : http://localhost:6333/dashboard")
    print("Next steps → run [italic]make ingest[/] then [italic]make dev[/]")

if __name__ == "__main__":
    sys.exit(main())
