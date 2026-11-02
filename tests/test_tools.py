"""Unit tests for the shared tools (no LLM / no API calls)."""
import os
import tempfile
import pytest
from unittest.mock import patch


def test_read_file_success(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world")
    # Import here so conductor doesn't need to be running
    from agent_span.tools import read_file
    # tools are decorated — call the underlying function via __wrapped__ if present
    fn = getattr(read_file, "__wrapped__", read_file)
    result = fn(str(f))
    assert "hello world" in result


def test_read_file_missing():
    from agent_span.tools import read_file
    fn = getattr(read_file, "__wrapped__", read_file)
    result = fn("/nonexistent/path/file.txt")
    assert "not found" in result.lower() or "error" in result.lower()


def test_list_files(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("")
    (tmp_path / "README.md").write_text("")
    from agent_span.tools import list_files
    fn = getattr(list_files, "__wrapped__", list_files)
    result = fn(str(tmp_path))
    assert "main.py" in result
    assert "README.md" in result


def test_write_file(tmp_path):
    from agent_span.tools import write_file
    fn = getattr(write_file, "__wrapped__", write_file)
    target = str(tmp_path / "sub" / "new.py")
    result = fn(target, "print('hi')")
    assert "Written" in result
    assert os.path.exists(target)
    assert open(target).read() == "print('hi')"


def test_search_code(tmp_path):
    (tmp_path / "app.py").write_text("def healthz():\n    return 'ok'\n")
    from agent_span.tools import search_code
    fn = getattr(search_code, "__wrapped__", search_code)
    result = fn("healthz", str(tmp_path))
    assert "healthz" in result
