import logging

from mcp_server import search_policy_library

def test_search_tool_logs_match_count(caplog):
    with caplog.at_level(logging.INFO, logger="mcp_server"):
        result = search_policy_library("vacation")

    assert result == []
    assert "Policy search completed; matches=0" in caplog.messages