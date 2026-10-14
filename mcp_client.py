import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


async def main():
    server_path = Path(__file__).parent / "mcp_server.py"
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],

    )

    async with Client(server) as client:
        result = await client.call_tool(
            "search_policy_library",
            {"search_term": "remote"},
        )

    print(result.structured_content)
    print(f"Tool failed: {result.is_error}")
    print(result.content)


if __name__ == "__main__":
    asyncio.run(main())