import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ai_client import execute_policy_tool, answer_policy_question


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

def test_answer_policy_question_returns_answer_without_retry():
    tool_call = SimpleNamespace(
        type="function_call",
        name="search_policy_library",
        arguments='{"search_term": "retention"}',
        call_id="call-test-001",
    )

    first_response = SimpleNamespace(
        id="response-001",
        output=[tool_call],
    )

    answer_response = SimpleNamespace(
        output=[],
        output_text="Retain training records for two years. [POL-001]",
    )

    model_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock(side_effect=[first_response, answer_response]),
        ),
    )

    mcp_client = SimpleNamespace(
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[])),
        call_tool=AsyncMock(return_value=SimpleNamespace(
            is_error=False,
            structured_content={"result": [{"policy_id": "POL-001"}]},
        )),
    )

    result = asyncio.run(answer_policy_question(
        "How long should training records be retained?",
        model_client,
        mcp_client,
    ))

    assert result == "Retain training records for two years. [POL-001]"
    assert model_client.responses.create.await_count == 2
    mcp_client.call_tool.assert_awaited_once_with(
        "search_policy_library",
        {"search_term": "retention"},
    )

def test_answer_policy_question_retries_empty_search_once():
    tool_call = SimpleNamespace(
            type="function_call",
            name="search_policy_library",
            arguments='{"search_term": "retention"}',
            call_id="call-test-001",
        )
    
    first_response = SimpleNamespace(
        id="response-001",
        output=[tool_call],
    )

    retry_response = SimpleNamespace(
        id="response-002",
        output=[SimpleNamespace(
            type="function_call",
            name="search_policy_library",
            arguments='{"search_term": "training"}',
            call_id="call-test-002",
        )],
    )

    answer_response = SimpleNamespace(
        output=[],
        output_text="Retain training records for two years. [POL-001]",
    )

    model_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock(side_effect=[first_response, retry_response, answer_response]),
        ),
    )

    mcp_client = SimpleNamespace(
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[])),
        call_tool=AsyncMock(side_effect=[
            SimpleNamespace(
                is_error=False,
                structured_content={"result": []},
            ),
            SimpleNamespace(
            is_error=False,
            structured_content={"result": [{"policy_id": "POL-001"}]},
        )
        ]),
    )

    result = asyncio.run(answer_policy_question(
        "How long should training records be retained?",
        model_client,
        mcp_client,
    ))

    assert model_client.responses.create.await_count == 3
    assert mcp_client.call_tool.await_count == 2
    mcp_client.call_tool.assert_awaited_with(
        "search_policy_library",
        {"search_term": "training"},
    )

def test_answer_policy_question_stops_after_empty_retry():
    tool_call = SimpleNamespace(
            type="function_call",
            name="search_policy_library",
            arguments='{"search_term": "retention"}',
            call_id="call-test-001",
        )
    
    first_response = SimpleNamespace(
        id="response-001",
        output=[tool_call],
    )

    retry_response = SimpleNamespace(
        id="response-002",
        output=[SimpleNamespace(
            type="function_call",
            name="search_policy_library",
            arguments='{"search_term": "training"}',
            call_id="call-test-002",
        )],
    )

    answer_response = SimpleNamespace(
        output=[],
        output_text="The available policies provide insufficient evidence.",
    )

    model_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock(side_effect=[first_response, retry_response, answer_response]),
        ),
    )

    mcp_client = SimpleNamespace(
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[])),
        call_tool=AsyncMock(side_effect=[
            SimpleNamespace(
                is_error=False,
                structured_content={"result": []},
            ),
            SimpleNamespace(
            is_error=False,
            structured_content={"result": []},
        )
        ]),
    )

    result = asyncio.run(answer_policy_question(
        "How long should training records be retained?",
        model_client,
        mcp_client,
    ))

    assert model_client.responses.create.await_count == 3
    assert mcp_client.call_tool.await_count == 2
    mcp_client.call_tool.assert_awaited_with(
        "search_policy_library",
        {"search_term": "training"},
    )

    final_request = model_client.responses.create.call_args.kwargs
    assert "tools" not in final_request