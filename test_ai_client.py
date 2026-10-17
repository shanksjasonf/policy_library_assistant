import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ai_client import execute_policy_tool


def test_execute_policy_tool_rejects_unsupported_tool():
    tool_call = SimpleNamespace(
        name="delete_policy",
        arguments={},
    )

    mcp_client = SimpleNamespace(call_tool=AsyncMock())

    with pytest.raises(ValueError) as exception_info:
        asyncio.run(execute_policy_tool(tool_call, mcp_client))

    assert str(exception_info.value) == "Model requested an unsupported tool."
    mcp_client.call_tool.assert_not_awaited()

def test_execute_policy_tool_calls_search():
    tool_call = SimpleNamespace(
        name="search_policy_library",
        arguments='{"search_term": "retention"}',
    )

    expected_result = SimpleNamespace(
        is_error=False,
        structured_content={"result": []},
    )

    mcp_client = SimpleNamespace(
        call_tool=AsyncMock(return_value=expected_result),
    )

    result = asyncio.run(execute_policy_tool(tool_call, mcp_client))

    mcp_client.call_tool.assert_awaited_once_with(
        "search_policy_library",
        {"search_term": "retention"},
    )

    assert result is expected_result

def test_execute_policy_tool_rejects_invalid_json():
    tool_call = SimpleNamespace(
        name="search_policy_library",
        arguments="('search_term': 'retention')",
    )

    mcp_client = SimpleNamespace(call_tool=AsyncMock())

    with pytest.raises(json.JSONDecodeError):
        asyncio.run(execute_policy_tool(tool_call, mcp_client))

    mcp_client.call_tool.assert_not_awaited()