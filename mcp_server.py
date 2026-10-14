import logging
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from policy_loader import load_policies
from policy_search import search_policies, get_policy_by_id

logger = logging.getLogger(__name__)

mcp = MCPServer("Policy Library Assistant")

@mcp.tool()
def get_library_description() -> str:
    """Describe the policy library."""
    return "A synthetic policy library for demonstrating MCP in Python."


@mcp.tool()
def search_policy_library(search_term: str) -> list[dict[str, str]]:
    """Search policy titles and content using a case-insensitive substring."""
    if len(search_term) > 200:
        raise ToolError("Search term must be less than or equal to 200 characters.")
    
    data_path = Path(__file__).parent / "data" / "policies.json"

    policies = load_policies(data_path)

    matches = search_policies(policies, search_term)
    logger.info("Policy search completed; matches=%d", len(matches))

    return matches

@mcp.tool()
def get_policy(policy_id: str) -> dict[str, str] | None:
    """Retrieve policy by exact ID or return None if not found."""
    data_path = Path(__file__).parent / "data" / "policies.json"
    policies = load_policies(data_path)
    return get_policy_by_id(policies, policy_id)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    mcp.run(transport="stdio")