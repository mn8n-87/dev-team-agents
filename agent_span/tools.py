"""Shared tools available to all agents in the Agent Span team.

All paths are resolved inside AGENT_WORKDIR (default: current directory), so the
team can work on any project without touching files outside it.
"""
import os
import subprocess
from conductor.ai.agents import tool

SKIP_DIRS = {"__pycache__", "node_modules", ".venv", "venv", "dist", "build"}


def workdir() -> str:
    """Return the absolute path of the project the team is working on."""
    return os.path.realpath(os.getenv("AGENT_WORKDIR", "."))


def _resolve(path: str) -> str:
    """Resolve *path* inside the workdir, rejecting anything that escapes it."""
    root = workdir()
    full = os.path.realpath(os.path.join(root, path))
    if full != root and not full.startswith(root + os.sep):
        raise PermissionError(f"path is outside the project directory: {path}")
    return full


@tool
def read_file(path: str) -> str:
    """Read the contents of a file from the project directory."""
    try:
        with open(_resolve(path)) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """List files and directories under a given path."""
    try:
        base = _resolve(directory)
        entries = []
        for root, dirs, files in os.walk(base):
            # Skip hidden dirs and common noise
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS)
            level = os.path.relpath(root, base).count(os.sep) + (root != base)
            indent = "  " * level
            entries.append(f"{indent}{os.path.basename(root)}/")
            for f in sorted(files):
                entries.append(f"{indent}  {f}")
        return "\n".join(entries) or "(empty)"
    except Exception as e:
        return f"Error listing files: {e}"


@tool
def search_code(pattern: str, directory: str = ".") -> str:
    """Search for a text pattern across source files using grep."""
    try:
        base = _resolve(directory)
        excludes = [f"--exclude-dir={d}" for d in SKIP_DIRS | {".git"}]
        result = subprocess.run(
            ["grep", "-rnI", *excludes, pattern, base],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stdout.replace(workdir() + os.sep, "")
        return output[:20000] or "(no matches)"
    except Exception as e:
        return f"Error searching code: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed."""
    try:
        full = _resolve(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        return f"Written: {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def run_tests(test_path: str = "tests/") -> str:
    """Run pytest on the given path and return the output."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", _resolve(test_path), "-v", "--tb=short"],
            capture_output=True, text=True, timeout=300, cwd=workdir(),
        )
        return (result.stdout + result.stderr)[-20000:]
    except Exception as e:
        return f"Error running tests: {e}"


# Tools exposed to each agent role
RESEARCHER_TOOLS = [read_file, list_files, search_code]
PLANNER_TOOLS = [read_file, list_files]
CODER_TOOLS = [read_file, list_files, search_code, write_file, run_tests]
REVIEWER_TOOLS = [read_file, list_files, search_code, run_tests]
