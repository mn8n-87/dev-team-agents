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

### 1. Install the Agentspan CLI

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/agentspan-ai/agentspan/main/cli/install.sh | sh

# or via npm
npm install -g @agentspan-ai/agentspan
```

### 2. Install Python dependencies

```bash
cd dev-team-agents
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure your API key

```bash
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY (or OPENAI_API_KEY) and AGENT_MODEL
```

### 4. Start the Conductor server

```bash
# In a separate terminal
agentspan server start
# Opens the visual UI at http://localhost:6767
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
│   ├── agents.py     # all 4 agents + pipeline (researcher >> planner >> coder >> reviewer)
│   └── tools.py      # shared tools: read_file, write_file, list_files, search_code, run_tests
├── tests/
│   └── test_tools.py
├── main.py           # CLI entry point
├── pyproject.toml
└── .env.example
```
