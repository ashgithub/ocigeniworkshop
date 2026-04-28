""" What this file does:
Demonstrates connecting a remote MCP server as a tool in Responses API.
The model can call tools exposed by that MCP endpoint.

Documentation for reference:
- Tools and remote MCP connector: https://developers.openai.com/api/docs/guides/tools-connectors-mcp
- Responses API: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution
- #genai-hosted-deployment-users: GA deployment and integration updates

Environment setup:
- Set up the credentials for OCI over the `sandbox.yaml file`
- Make sure to set up a project ID from the console, consult the GenAI platform GA docs for guidance
- Set up the right compartment ID and profile name over the config file

How to run the file:
uv run openai_sdk/genai_client/mcp_client.py

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

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

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
    print("Final response after MCP tool usage:")
    print(response.output_text)

if __name__ == "__main__":
    main()
