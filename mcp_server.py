from mcp.server import MCPServer

mcp = MCPServer("Policy Library Assistant")

@mcp.tool()
def get_library_description() -> str:
    """Describe the policy library."""
    return "A synthetic policy library for demonstrating MCP in Python."

if __name__ == "__main__":
    mcp.run(transport="stdio")