"""Shared base utilities for all Agent Span agents."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query
from rich.console import Console

console = Console()


async def run_agent(
    prompt: str,
    options: ClaudeAgentOptions,
    label: str = "agent",
) -> str:
    """Run a single-turn agent and return the accumulated text response."""
    console.rule(f"[bold cyan]{label}[/]")
    console.print(f"[dim]Prompt:[/] {prompt[:120]}{'…' if len(prompt) > 120 else ''}")
    parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        text = _extract_text(message)
        if text:
            parts.append(text)
    result = "\n".join(parts)
    console.print(f"[green]Done.[/]\n")
    return result


def _extract_text(message: Any) -> str:
    """Pull plain text out of whatever shape a message takes."""
    if isinstance(message, str):
        return message
    if hasattr(message, "content"):
        content = message.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return " ".join(
                block.text for block in content if hasattr(block, "text")
            )
    return ""
