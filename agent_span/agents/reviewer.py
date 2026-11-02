"""Reviewer agent — reviews code or a plan step and returns structured feedback."""
from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions

from agent_span.base import run_agent

SYSTEM_PROMPT = """\
You are a senior code reviewer and quality engineer.
You review code changes or a completed plan step and provide structured feedback.

Output format:
## Review

**Status:** APPROVED | CHANGES_REQUESTED

### Issues
- (list issues, each with severity: critical / major / minor)

### Suggestions
- (optional improvements, not blockers)

### Summary
One paragraph overall verdict.
"""


class ReviewerAgent:
    """Reviews code or agent output and returns structured feedback."""

    def __init__(self, max_turns: int = 10) -> None:
        self._options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            max_turns=max_turns,
            allowed_tools=["Read", "Glob", "Grep"],
            permission_mode="default",
        )

    async def review(self, artifact: str, context: str = "") -> str:
        """Review *artifact* (code, plan, or output text).

        *context* can include the original plan step or task for reference.
        """
        prompt_parts = [f"Review the following:\n\n{artifact}"]
        if context:
            prompt_parts.append(f"\n\nOriginal task / plan step for reference:\n\n{context}")
        return await run_agent(
            prompt="\n".join(prompt_parts),
            options=self._options,
            label="Reviewer",
        )
