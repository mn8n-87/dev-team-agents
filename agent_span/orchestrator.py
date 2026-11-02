"""Orchestrator — wires the four agents together into a pipeline."""
from __future__ import annotations

from rich.console import Console

from agent_span.agents import CoderAgent, PlannerAgent, ResearcherAgent, ReviewerAgent

console = Console()


class Orchestrator:
    """Runs the full Plan → Research → Code → Review pipeline for a task."""

    def __init__(self, workdir: str = ".") -> None:
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent(workdir=workdir)
        self.coder = CoderAgent(workdir=workdir)
        self.reviewer = ReviewerAgent()

    async def run(self, task: str) -> dict[str, str]:
        """
        Execute the full pipeline for *task*.

        Returns a dict with keys: plan, research, implementation, review.
        """
        console.rule("[bold magenta]Agent Span[/]")
        console.print(f"[bold]Task:[/] {task}\n")

        # 1. Plan
        plan = await self.planner.plan(task)

        # 2. Research
        research = await self.researcher.research(
            f"Task: {task}\n\nPlan:\n{plan}"
        )

        # 3. Code
        implementation = await self.coder.implement(
            step=plan,
            context=research,
        )

        # 4. Review
        review = await self.reviewer.review(
            artifact=implementation,
            context=f"Task: {task}\n\nPlan:\n{plan}",
        )

        console.rule("[bold magenta]Pipeline complete[/]")
        return {
            "plan": plan,
            "research": research,
            "implementation": implementation,
            "review": review,
        }
