import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ai_client import execute_policy_tool, answer_policy_question, serialize_tool_result


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

    first_request = model_client.responses.create.call_args_list[0].kwargs
    assert first_request["parallel_tool_calls"] is False
    

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

def test_answer_policy_question_requires_policy_search():
    model_response = SimpleNamespace(
        output=[],
        output_text="An answer without policy evidence.",
    )

    model_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock(return_value=model_response),
        ),
    )

    mcp_client = SimpleNamespace(
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[])),
        call_tool=AsyncMock(),
    )

    result = asyncio.run(answer_policy_question(
        "What does the policy say?",
        model_client,
        mcp_client,
    ))

    assert result == (
        "No policy search was performed, so I cannot provide a grounded answer."
    )
    model_client.responses.create.assert_awaited_once()
    mcp_client.call_tool.assert_not_awaited()

def test_serialize_tool_result_preserves_error_message():
    tool_result = SimpleNamespace(
        is_error=True,
        structured_content=None,
        content=[
            SimpleNamespace(
                type="text",
                text="Search term must be less than or equal to 200 characters.",
            ),
        ],
    )

    serialized = serialize_tool_result(tool_result)
    payload = json.loads(serialized)

    assert payload == {
        "is_error": True,
        "data": None,
        "error": "Search term must be less than or equal to 200 characters.",
    }

def test_answer_policy_question_forwards_tool_error():
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
        output_text="The policy search failed, so I cannot answer from policy evidence.",
    )

    model_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock(side_effect=[first_response, answer_response]),
        ),
    )

    mcp_client = SimpleNamespace(
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[])),
        call_tool=AsyncMock(return_value=SimpleNamespace(
            is_error=True,
            structured_content=None,
            content=[
                SimpleNamespace(type="text", text="Policy search unavailable.")
            ]
        )),
    )

    result = asyncio.run(answer_policy_question(
        "How long should training records be retained?",
        model_client,
        mcp_client,
    ))

    assert model_client.responses.create.await_count == 2
    mcp_client.call_tool.assert_awaited_once_with(
        "search_policy_library",
        {"search_term": "retention"},
    )

    answer_request = model_client.responses.create.call_args.kwargs
    forwarded_result = json.loads(answer_request["input"][0]["output"])

    assert forwarded_result["is_error"] is True
    assert forwarded_result["error"] == "Policy search unavailable."
    assert answer_request["tool_choice"] == "auto"