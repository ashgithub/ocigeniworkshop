""" What this file does:
Demonstrates connecting a remote MCP server as a tool in Responses API.
The model can call tools exposed by that MCP endpoint.

Documentation for reference:
- Tools and remote MCP: https://platform.openai.com/docs/guides/tools-remote-mcp
- Responses API: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users
- #igiu-innovation-lab
- #igiu-ai-learning
- #genai-hosted-deployment-users

Environment setup:
- Create `.env` from `.env.example`
- Ensure endpoint/project/profile values are set for OCI

How to run the file:
uv run python genai_client/mcp_client.py

Safe experiments:
1. Change `USER_PROMPT` to another dice expression.
2. Swap MCP server settings when testing another server.
3. Compare output with and without MCP tool enabled.

Important sections:
1. Step 1: Define MCP tool configuration.
2. Step 2: Build configured OpenAI client.
3. Step 3: Run tool-enabled prompt and print output. """

from dotenv import load_dotenv
from openai import OpenAI

from openai_sdk.openai_client_provider import OpenAIClientProvider

load_dotenv()

MODEL_ID = "openai.gpt-5.4"
USER_PROMPT = "Roll 2d4+1"
MCP_TOOL = {
    "type": "mcp",
    "server_label": "dmcp",
    "server_description": "A Dungeons and Dragons MCP server to assist with dice rolling.",
    "server_url": "https://mcp.deepwiki.com/mcp",
    "require_approval": "never",
}


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Run a tool-enabled prompt against the MCP server.
    response = client.responses.create(
        model=MODEL_ID,
        tools=[MCP_TOOL],
        input=USER_PROMPT,
    )

    # Step 3: Print final output.
    print(response.output_text)


if __name__ == "__main__":
    main()
