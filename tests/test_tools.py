"""Unit tests for the shared tools (no LLM / no API calls)."""
import os
import pytest


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    """Point the tools at a temporary project directory."""
    monkeypatch.setenv("AGENT_WORKDIR", str(tmp_path))
    return tmp_path


def _fn(tool):
    # tools are decorated — call the underlying function via __wrapped__ if present
    return getattr(tool, "__wrapped__", tool)


def test_read_file_success(project):
    (project / "hello.txt").write_text("hello world")
    from agent_span.tools import read_file
    result = _fn(read_file)("hello.txt")
    assert "hello world" in result


def test_read_file_missing():
    from agent_span.tools import read_file
    result = _fn(read_file)("nonexistent/file.txt")
    assert "not found" in result.lower() or "error" in result.lower()


def test_list_files(project):
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("")
    (project / "README.md").write_text("")
    from agent_span.tools import list_files
    result = _fn(list_files)()
    assert "main.py" in result
    assert "README.md" in result


def test_write_file(project):
    from agent_span.tools import write_file
    result = _fn(write_file)("sub/new.py", "print('hi')")
    assert "Written" in result
    target = project / "sub" / "new.py"
    assert os.path.exists(target)
    assert target.read_text() == "print('hi')"


def test_search_code(project):
    (project / "app.py").write_text("def healthz():\n    return 'ok'\n")
    from agent_span.tools import search_code
    result = _fn(search_code)("healthz")
    assert "app.py" in result
    assert "healthz" in result


@pytest.mark.parametrize("path", ["../outside.txt", "/etc/passwd"])
def test_paths_outside_project_are_rejected(path):
    from agent_span.tools import read_file, write_file
    assert "outside the project" in _fn(read_file)(path)
    assert "outside the project" in _fn(write_file)(path, "x")
