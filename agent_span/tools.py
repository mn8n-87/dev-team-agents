"""Shared tools available to all agents in the Agent Span team."""
import os
import subprocess
from conductor.ai.agents import tool, ToolContext


@tool
def read_file(path: str) -> str:
    """Read the contents of a file from the project directory."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """List files and directories under a given path."""
    try:
        entries = []
        for root, dirs, files in os.walk(directory):
            # Skip hidden dirs and common noise
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules", ".venv")]
            level = root.replace(directory, "").count(os.sep)
            indent = "  " * level
            entries.append(f"{indent}{os.path.basename(root)}/")
            for f in files:
                entries.append(f"{indent}  {f}")
        return "\n".join(entries) or "(empty)"
    except Exception as e:
        return f"Error listing files: {e}"


@tool
def search_code(pattern: str, directory: str = ".") -> str:
    """Search for a text pattern across all source files using grep."""
    try:
        result = subprocess.run(
            ["grep", "-rn", "--include=*.py", pattern, directory],
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout or "(no matches)"
    except Exception as e:
        return f"Error searching code: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Written: {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def run_tests(test_path: str = "tests/") -> str:
    """Run pytest on the given path and return the output."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
            capture_output=True, text=True, timeout=60,
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running tests: {e}"


# Tools exposed to each agent role
RESEARCHER_TOOLS = [read_file, list_files, search_code]
PLANNER_TOOLS = [read_file, list_files]
CODER_TOOLS = [read_file, list_files, search_code, write_file, run_tests]
REVIEWER_TOOLS = [read_file, list_files, search_code, run_tests]
