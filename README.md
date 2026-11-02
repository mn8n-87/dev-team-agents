# Agent Span

A durable team of AI agents for software development, powered by [conductor-agent-sdk](https://github.com/agentspan-ai/agentspan) (now part of [Orkes Conductor](https://github.com/conductor-oss/conductor)).

## Pipeline

```
Task ──► Researcher ──► Planner ──► Coder ──► Reviewer
```

| Agent | Role |
|---|---|
| **Researcher** | Explores the codebase, identifies relevant files and patterns |
| **Planner** | Turns research into a numbered, file-level implementation plan |
| **Coder** | Executes the plan, writes files, runs tests, fixes failures |
| **Reviewer** | Reviews the output, returns APPROVED or CHANGES_REQUESTED |

Agents run as durable server-side executions — if your process crashes, the server resumes from the last completed step automatically.

## Setup

### 1. Start the Agentspan server in Docker

The LLM calls run on the server, so it needs your provider key:

```bash
docker run -d --name agentspan --restart unless-stopped -p 6767:6767 \
  -v agentspan_data:/data -e ANTHROPIC_API_KEY=your-key agentspan/server:latest
# Visual UI at http://localhost:6767
```

### 2. Install Python dependencies

`conductor-agent-sdk` needs Python 3.10–3.13 (not 3.14):

```bash
cd dev-team-agents
uv venv --python 3.13 .venv      # or: python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env — set AGENT_MODEL, CONDUCTOR_SERVER_URL and, optionally, AGENT_WORKDIR
```

### 4. Register the team on the server

```bash
python main.py deploy   # agents appear under Definitions → Agent in the UI
python main.py serve    # keep running so runs started from the UI can use the tools
```

### 5. Run the team

```bash
# Full pipeline
python main.py "Add a /healthz endpoint to the Flask app"

# Stream output live
python main.py --stream "Add a /healthz endpoint"

# Single agent
python main.py --agent researcher "How is auth currently implemented?"
python main.py --agent planner    "Refactor the database layer"
python main.py --agent coder      "Add input validation to signup"
python main.py --agent reviewer   "Review the latest changes"

# Work on another project (file tools are confined to this directory)
python main.py --workdir ~/dev/my-app "Add a /healthz endpoint"
```

## Visual UI

Open [http://localhost:6767](http://localhost:6767) after starting the server to see:
- Live execution graph of each agent step
- Full execution history and token usage
- Pause / approve / reject tool calls in the browser

## Tests

```bash
pytest
```

## Project layout

```
dev-team-agents/
├── agent_span/
│   ├── team.py         # Agentspan team: 4 agents + dev_team pipeline (runs on the server)
│   ├── tools.py        # shared tools: read_file, write_file, list_files, search_code, run_tests
│   ├── agents/         # standalone Claude Agent SDK versions of the agents (no server)
│   ├── base.py
│   └── orchestrator.py
├── tests/
│   ├── test_agents.py
│   └── test_tools.py
├── main.py           # CLI entry point
├── pyproject.toml
└── .env.example
```
