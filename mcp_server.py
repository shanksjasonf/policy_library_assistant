import logging
from pathlib import Path

from mcp.server import MCPServer

from policy_loader import load_policies
from policy_search import search_policies

logger = logging.getLogger(__name__)

mcp = MCPServer("Policy Library Assistant")

@mcp.tool()
def get_library_description() -> str:
    """Describe the policy library."""
    return "A synthetic policy library for demonstrating MCP in Python."


@mcp.tool()
def search_policy_library(search_term: str) -> list[dict[str,str]]:
    """Search policy titles and content using a case-insensitive substring."""
    data_path = Path(__file__).parent / "data" / "policies.json"

    policies = load_policies(data_path)

    logger.info("Searching policy library.")

    return search_policies(policies, search_term)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    
    mcp.run(transport="stdio")