import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

def main():
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    client = OpenAI()
    response = client.responses.create(
        model="gpt-5.4-mini",
        input="In one sentence, explain what an MCP server does.",
        max_output_tokens=500
    )

    print(response.output_text)


if __name__ == "__main__":
    main()