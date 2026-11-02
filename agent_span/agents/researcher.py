"""Researcher agent — gathers information and summarises findings."""
from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions

from agent_span.base import run_agent

SYSTEM_PROMPT = """\
You are a senior technical researcher.
You search documentation, read files, and gather information needed to
complete a software development task.

Guidelines:
- Read existing code before making suggestions
- Cite your sources (file paths, doc URLs)
- Summarise findings concisely in a **Findings** section
- Flag anything ambiguous or missing in a **Questions** section
"""


class ResearcherAgent:
    """Searches and summarises information for a given topic or task step."""

    def __init__(self, max_turns: int = 10, workdir: str = ".") -> None:
        self._options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            max_turns=max_turns,
            allowed_tools=["Read", "Glob", "Grep", "WebSearch", "WebFetch"],
            permission_mode="default",
        )
        self._workdir = workdir

    async def research(self, topic: str) -> str:
        """Research *topic* and return a findings summary."""
        return await run_agent(
            prompt=f"Research the following and produce a findings summary:\n\n{topic}",
            options=self._options,
            label="Researcher",
        )
