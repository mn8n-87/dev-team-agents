#!/usr/bin/env python3
"""Agent Span — CLI entry point.

Usage:
    # Full pipeline (Researcher → Planner → Coder → Reviewer)
    python main.py "Add a /healthz endpoint to the Flask app"

    # Single agent
    python main.py --agent researcher "How is auth implemented?"
    python main.py --agent planner   "Refactor the database layer"
    python main.py --agent coder     "Add input validation to signup"
    python main.py --agent reviewer  "Review the latest changes"

    # Stream output token by token
    python main.py --stream "Add a /healthz endpoint"

Prerequisites:
    1. pip install -e ".[dev]"
    2. cp .env.example .env  →  fill in your API key
    3. agentspan server start   (in a separate terminal)
"""
from __future__ import annotations

import sys
import os
from dotenv import load_dotenv

load_dotenv()

from conductor.ai.agents import AgentRuntime
from agent_span.agents import dev_team, researcher, planner, coder, reviewer

AGENTS = {
    "researcher": researcher,
    "planner": planner,
    "coder": coder,
    "reviewer": reviewer,
    "pipeline": dev_team,
}


def run(task: str, agent_name: str = "pipeline", stream: bool = False) -> None:
    agent = AGENTS[agent_name]
    print(f"\n🚀  Agent Span — running [{agent_name}]\n{'─' * 60}")

    with AgentRuntime() as runtime:
        if stream:
            for event in runtime.stream(agent, task):
                match event.type:
                    case "tool_call":
                        print(f"\n⚙️  [{event.agent_name}] calling {event.tool_name}...")
                    case "thinking":
                        print(f"\n💭  [{event.agent_name}] {event.content}", end="", flush=True)
                    case "done":
                        print(f"\n\n{'─' * 60}\n✅  Done\n\n{event.output}")
                    case "guardrail_fail":
                        print(f"\n⚠️  Guardrail failed: {event.guardrail_name}")
        else:
            result = runtime.run(agent, task)
            result.print_result()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    stream = False
    agent_name = "pipeline"

    if "--stream" in args:
        stream = True
        args.remove("--stream")

    if "--agent" in args:
        idx = args.index("--agent")
        if idx + 1 >= len(args):
            print("Error: --agent requires a name (researcher|planner|coder|reviewer)")
            sys.exit(1)
        agent_name = args[idx + 1]
        if agent_name not in AGENTS:
            print(f"Error: unknown agent '{agent_name}'. Choose from: {', '.join(AGENTS)}")
            sys.exit(1)
        args = args[:idx] + args[idx + 2:]

    task = " ".join(args)
    if not task:
        print("Error: no task provided.")
        sys.exit(1)

    run(task, agent_name=agent_name, stream=stream)


if __name__ == "__main__":
    main()
