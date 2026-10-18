# Policy Library Assistant

A Python case study that demonstrates how an AI assitant can answer policy-related questions retrieved through MCP. The client connects an OpenAI model to a local MCP server, executes policy-related searches, and returns answers with citations. To manage token usage, the workflow permits an initial search and one additional search.

## Components
| File | Purpose |
|---|---|
| ai_client.py | Accepts questions, calls the OpenAI model, runs the required search(es), and displays answers to the user. |
| mcp_server.py | Makes the policy tools available to MCP clients. |
| policy_loader.py | Reads policy data and checks that each record has the required fields and data types. |
| policy_search.py | Searches policy titles and content or finds the appropriate policy by its ID. |
| tool_adapter.py | Converts MCP tool definitions into the format expected by OpenAI. |
| policies.json | Contains policy information. |
| evaluation.md | Documents testing/evaluation of the assistant's performance. | 

## Scope and Limitations
- Search uses case-insensitive substrings, not semantic matching. It does not understand meaning or automatically recognize related terms.
- Differences in wording can cause the search to miss a relevant policy.
- The model is instructed to cite policy IDs, but the assistant does not automatically confirm that each citation supports the answer.
- Each question is handled independently. The assistant does not retain previous questions or answers.
- Automated tests confirm how the assistant behaves using controlled responses. Live evaluations check the answers produced by the OpenAI model.
- The assistant ignored an injected command in the recorded test. More testing would be needed to assess whether other injection attempts might be successful.
- The MCP server runs in Docker using a non-root account. The AI client runs locally.

## Local Setup

Use Python 3.13 and run these commands from the project folder in PowerShell:
- Create virtual environment:
```
py -3.13 -m venv .venv
```

- Install the client and test dependencies:
```
& "./.venv/Scripts/python.exe" -m pip install -r requirements-client.txt -r requirements-dev.txt
```

- Create a local .env file:
```
OPENAI_API_KEY=enter_your_key
```

NOTE: the .env file stores the key in plain text and is excluded from Git and Docker's build context. For production, use a managed key store.

- Run the automated tests:
```
& "./.venv/Scripts/python.exe" -m pytest -q
```

- Start the AI policy assistant:
```
& "./.venv/Scripts/python.exe" ai_client.py
```

The client starts the MCP server automatically. It does not require Docker for the local workflow.

## Run the MCP server in Docker

Docker Desktop must be running with the Linux instance available.

- Build the image from the project folder
```
docker build -t policy-library-assistant:dev .
```

- Confirm that the container runs as a non-root user:
```
docker run --rm policy-library-assistant:dev id
```

The expected user is 'appuser', with UID = 10001.

To connect through MCP Inspector, install Node.js LTS with npm. Once installed, run:
```
npx @modelcontextprotocol/inspector@2.11.0 docker run --rm -i policy-library-assistant:dev
```

Connect to the assistant in Inspector and select a tool to call.

The 'i' option keeps standard input open for MCP messages. Do not add 't' to allocate a terminal.

The image includes the MCP server and policies. It does not include the AI client or the OpenAI API key. The local AI client uses Python directly; it does not use the Docker image.

NOTE: Rebuild the image after changing the server code, dependencies, or policy data.