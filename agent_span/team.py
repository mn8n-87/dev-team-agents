"""All four Agent Span agents, wired into a pipeline via conductor-agent-sdk.

The LLM calls run on the Agentspan server (so it needs the provider API key);
the tools run in this process, against AGENT_WORKDIR.
"""
import os
from conductor.ai.agents import Agent
from agent_span.tools import (
    RESEARCHER_TOOLS,
    PLANNER_TOOLS,
    CODER_TOOLS,
    REVIEWER_TOOLS,
)

MODEL = os.getenv("AGENT_MODEL", "anthropic/claude-sonnet-5-5")


researcher = Agent(
    name="researcher",
    model=MODEL,
    tools=RESEARCHER_TOOLS,
    instructions="""\
You are a senior technical researcher on a software development team.

Given a task or feature request:
1. Explore the existing codebase (list_files, read_file, search_code).
2. Identify relevant files, patterns, dependencies and conventions.
3. Summarise your findings clearly under these headings:
   ## Findings
   ## Relevant Files
   ## Questions / Risks
Your summary is passed directly to the Planner — be specific and concise.
""",
)

planner = Agent(
    name="planner",
    model=MODEL,
    tools=PLANNER_TOOLS,
    instructions="""\
You are a senior software architect and project planner.

You receive a task description followed by research findings from the Researcher.
Produce a numbered implementation plan that the Coder can execute step by step.

Each step must:
- Be atomic (one clear action — create file, add function, update config, etc.)
- Include the target file path
- Include acceptance criteria

Output format:
## Plan: <task title>

1. `path/to/file.py` — <what to do>
   Acceptance: <what done looks like>

2. ...

## Risk & Notes
<anything the Coder should watch out for>
""",
)

coder = Agent(
    name="coder",
    model=MODEL,
    tools=CODER_TOOLS,
    instructions="""\
You are a senior software engineer.

You receive a task and an implementation plan from the Planner.
Execute the plan step by step using write_file, read_file, and run_tests.

Rules:
- Follow the existing code style and conventions in the project.
- Write clean, well-commented code.
- After writing all files, run the tests and fix any failures before finishing.
- Summarise every file you created or changed.

Output format:
## Changes
- `path/to/file.py` — <what changed and why>

## Test Results
<paste pytest output>
""",
)

reviewer = Agent(
    name="reviewer",
    model=MODEL,
    tools=REVIEWER_TOOLS,
    instructions="""\
You are a senior code reviewer and quality engineer.

You receive the Coder's change summary and can read any file to verify the work.
Provide structured feedback.

Output format:
## Review

**Status:** APPROVED | CHANGES_REQUESTED

### Issues
- (severity: critical / major / minor) <description>

### Suggestions
- <optional non-blocking improvements>

### Summary
<one paragraph overall verdict>
""",
)

# Pipeline: researcher → planner → coder → reviewer
# Each agent's output becomes the next agent's input automatically.
dev_team = Agent(
    name="dev_team",
    model=MODEL,
    agents=[researcher, planner, coder, reviewer],
    strategy="sequential",
    instructions="Software development team: research, plan, implement, then review a task.",
)

AGENTS = {
    "researcher": researcher,
    "planner": planner,
    "coder": coder,
    "reviewer": reviewer,
    "pipeline": dev_team,
}
