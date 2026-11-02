"""Planner agent — breaks down a task and produces a step-by-step plan."""
from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions

from agent_span.base import run_agent

SYSTEM_PROMPT = """\
You are a senior software architect and project planner.
Given a high-level task or feature request, produce a clear, numbered
implementation plan that a team of specialised agents can execute.

Each step must:
- Be atomic (one clear action)
- Specify which agent role should handle it (Researcher, Coder, Reviewer)
- Include acceptance criteria

Output format:
## Plan: <task title>

1. [<Role>] <Step description>
   - Acceptance: <what done looks like>

2. ...

End with a brief **Risk & Notes** section.
"""


class PlannerAgent:
    """Decomposes tasks into actionable plans."""

    def __init__(self, max_turns: int = 5) -> None:
        self._options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            max_turns=max_turns,
            allowed_tools=[],          # pure reasoning, no file tools needed
            permission_mode="default",
        )

    async def plan(self, task: str) -> str:
        """Return a structured plan for *task*."""
        return await run_agent(
            prompt=f"Task:\n\n{task}",
            options=self._options,
            label="Planner",
        )
