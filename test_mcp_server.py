import logging
import mcp_server

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
