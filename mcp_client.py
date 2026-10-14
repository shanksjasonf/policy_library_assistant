import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from tool_adapter import to_openai_tool

async def main():
    server_path = Path(__file__).parent / "mcp_server.py"
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],

    )

    async with Client(server) as client:
        result = await client.list_tools()

        for tool in result.tools:
            if tool.name == "search_policy_library":
                print(to_openai_tool(tool))


if __name__ == "__main__":
    asyncio.run(main())