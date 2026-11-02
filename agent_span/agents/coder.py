"""Coder agent — writes and edits code based on a plan step."""
from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions

from agent_span.base import run_agent

SYSTEM_PROMPT = """\
You are a senior software engineer.
You implement code changes based on a clear plan step and research findings.

Guidelines:
- Write clean, idiomatic Python (or the language of the target file)
- Follow existing code conventions in the project
- Add docstrings and inline comments where non-obvious
- Output only the files you changed, using the Write/Edit tools
- After writing, briefly summarise what you changed and why
"""


class CoderAgent:
    """Implements a single plan step as working code."""

    def __init__(self, max_turns: int = 20, workdir: str = ".") -> None:
        self._options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            max_turns=max_turns,
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            permission_mode="default",
        )
        self._workdir = workdir

    async def implement(self, step: str, context: str = "") -> str:
        """Implement *step*, optionally informed by *context* (research findings)."""
        prompt_parts = [f"Implement the following plan step:\n\n{step}"]
        if context:
            prompt_parts.append(f"\n\nContext / research findings:\n\n{context}")
        return await run_agent(
            prompt="\n".join(prompt_parts),
            options=self._options,
            label="Coder",
        )
