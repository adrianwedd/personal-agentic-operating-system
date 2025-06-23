"""Ingestion package."""
from .ingest import ingest
from .loaders import load_gmail, load_files
__all__ = ["ingest", "load_gmail", "load_files"]
