#!/usr/bin/env python3
"""Standalone helper – prints the recommended Ollama model for this host."""
import psutil, argparse, sys

gibs = psutil.virtual_memory().total / 2**30
if gibs < 4:
    model = "phi3:mini"
elif gibs < 8:
    model = "llama3.2:3b"
else:
    model = "gemma3:4b"

parser = argparse.ArgumentParser()
parser.add_argument("--json", action="store_true")
args = parser.parse_args()
if args.json:
    import json, os
    sys.stdout.write(json.dumps({"model": model, "ram_gib": round(gibs,2)}, indent=2))
else:
    print(model)
