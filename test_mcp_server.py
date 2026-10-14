import logging
import mcp_server
import pytest

from mcp_server import search_policy_library

def test_search_tool_logs_match_count(caplog, monkeypatch):
    def fake_load_policies(data_path):
        return [
            {
                "policy_id": "TEST-001",
                "title": "Remote Work Policy",
                "content": "Remote access requires multifactor authentication.",
            }
        ]

    monkeypatch.setattr(mcp_server, "load_policies", fake_load_policies)

    with caplog.at_level(logging.INFO, logger="mcp_server"):
        result = search_policy_library("vacation")

    assert result == []
    assert "Policy search completed; matches=0" in caplog.messages


def test_search_tool_rejects_long_input_before_loading(monkeypatch):
    def unexpected_load(data_path):
        raise AssertionError("Loader should not run for oversized input.")

    monkeypatch.setattr(mcp_server, "load_policies", unexpected_load)

    with pytest.raises(ValueError) as exception_info:
        search_policy_library("x" * 201)

    assert str(exception_info.value) == (
        "Search term must be less than or equal to 200 characters."
    )