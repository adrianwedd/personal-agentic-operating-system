"""Utility functions for Gmail and Calendar tools."""
from __future__ import annotations

from typing import List, Iterable

from langchain_core.tools import BaseTool
from langchain_google_community.gmail.toolkit import GmailToolkit, SCOPES as GMAIL_SCOPES
from langchain_google_community.gmail.utils import build_resource_service as build_gmail_service
from langchain_google_community.calendar.toolkit import CalendarToolkit, SCOPES as CAL_SCOPES
from langchain_google_community.calendar.utils import build_resource_service as build_calendar_service


def _sanitize_tool(tool: BaseTool) -> BaseTool:
    """Hide API credentials when serializing tool objects."""
    original_dump = tool.model_dump

    def safe_dump(*args, **kwargs):
        exclude = set(kwargs.pop("exclude", set()))
        exclude.add("api_resource")
        return original_dump(*args, exclude=exclude, **kwargs)

    tool.model_dump = safe_dump  # type: ignore[assignment]
    return tool


def build_gmail_toolkit(scopes: Iterable[str] | None = None) -> GmailToolkit:
    """Return a GmailToolkit with read/write scopes."""
    return GmailToolkit(api_resource=build_gmail_service(scopes=list(scopes or GMAIL_SCOPES)))


def build_calendar_toolkit(scopes: Iterable[str] | None = None) -> CalendarToolkit:
    """Return a Google CalendarToolkit with read/write scopes."""
    return CalendarToolkit(api_resource=build_calendar_service(scopes=list(scopes or CAL_SCOPES)))


def build_gmail_tools() -> List[BaseTool]:
    """Return sanitized Gmail tools."""
    try:
        toolkit = build_gmail_toolkit()
        tools = toolkit.get_tools()
    except Exception:
        tools = []
    return [_sanitize_tool(t) for t in tools]


def build_calendar_tools() -> List[BaseTool]:
    """Return sanitized Google Calendar tools."""
    try:
        toolkit = build_calendar_toolkit()
        tools = toolkit.get_tools()
    except Exception:
        tools = []
    return [_sanitize_tool(t) for t in tools]


def build_action_tools() -> List[BaseTool]:
    """Return all available Gmail and Calendar tools."""
    return build_gmail_tools() + build_calendar_tools()

