"""Smoke tests for each agent (mock the SDK so no API calls are made)."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

FAKE_RESPONSE = "Mocked agent response."


async def _fake_query(*args, **kwargs):
    yield FAKE_RESPONSE


@pytest.mark.asyncio
async def test_planner_returns_string():
    from agent_span.agents import PlannerAgent

    with patch("agent_span.base.query", side_effect=_fake_query):
        result = await PlannerAgent().plan("Build a todo app")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_researcher_returns_string():
    from agent_span.agents import ResearcherAgent

    with patch("agent_span.base.query", side_effect=_fake_query):
        result = await ResearcherAgent().research("How does asyncio work?")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_coder_returns_string():
    from agent_span.agents import CoderAgent

    with patch("agent_span.base.query", side_effect=_fake_query):
        result = await CoderAgent().implement("Add a health-check endpoint")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_reviewer_returns_string():
    from agent_span.agents import ReviewerAgent

    with patch("agent_span.base.query", side_effect=_fake_query):
        result = await ReviewerAgent().review("def foo(): pass")
    assert isinstance(result, str)
