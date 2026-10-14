def to_openai_tool(mcp_tool):
    parameters = dict(mcp_tool.input_schema)
    parameters["additionalProperties"] = False

    return {
        "type": "function",
        "name": mcp_tool.name,
        "description": mcp_tool.description,
        "parameters": parameters,
        "strict": True,
    }