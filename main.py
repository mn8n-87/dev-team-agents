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

    # Work on another project (default: AGENT_WORKDIR or the current directory)
    python main.py --workdir ~/dev/my-app "Add a /healthz endpoint"

    # Register all agents on the Agentspan server (shows them in the dashboard)
    python main.py deploy

    # Keep the team's tool workers online so runs started from the dashboard work
    python main.py serve

Prerequisites:
    1. pip install -e ".[dev]"
    2. cp .env.example .env  →  set CONDUCTOR_SERVER_URL and AGENT_MODEL
    3. An Agentspan server with your LLM provider key (e.g. the agentspan Docker container)
"""
from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("CONDUCTOR_SERVER_URL", "http://localhost:6767/api")

from conductor.ai.agents import AgentRuntime
from agent_span.team import AGENTS
from agent_span.tools import workdir


def run(task: str, agent_name: str = "pipeline", stream: bool = False) -> None:
    agent = AGENTS[agent_name]
    print(f"\n🚀  Agent Span — running [{agent_name}] in {workdir()}\n{'─' * 60}")

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


def deploy() -> None:
    with AgentRuntime() as runtime:
        for info in runtime.deploy(*AGENTS.values()):
            print(f"✅  Deployed {info}")


def serve() -> None:
    print(f"🛠️  Serving Agent Span tools for {workdir()} — Ctrl+C to stop")
    with AgentRuntime() as runtime:
        runtime.serve(*AGENTS.values())


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    stream = False
    agent_name = "pipeline"

    if "--workdir" in args:
        idx = args.index("--workdir")
        if idx + 1 >= len(args):
            print("Error: --workdir requires a path")
            sys.exit(1)
        os.environ["AGENT_WORKDIR"] = os.path.expanduser(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if args == ["deploy"]:
        deploy()
        return
    if args == ["serve"]:
        serve()
        return

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
