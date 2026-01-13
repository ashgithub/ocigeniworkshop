"""
LangChain Agent with MCP (Model Context Protocol) Integration using OpenAI Responses API

This file demonstrates creating a LangChain agent that integrates with MCP servers using the
OpenAI Responses API with MCP calling capability. Uses OCI Generative AI for LLM with direct
MCP server integration via the responses.create() method.

Documentation:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OpenAI Responses API with MCP: https://platform.openai.com/docs/guides/tools-connectors-mcp
- LangChain OpenAI integration: https://docs.langchain.com/oss/python/integrations/chat/openai#remote-mcp
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Environment Setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path
- .env: Load environment variables (API keys if needed)

How to run:
1. Start MCP server: uv run langChain/function_calling/mcp/weather_mcp_server.py
2. Run this client: uv run langChain/function_calling/mcp/langchain_host_responses.py
3. Set up ngrok tunnel: ngrok http 8000 --host-header=localhost:8000

Slack channels:
- #generative-ai-users: OCI Gen AI questions
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Sandbox environment help
"""

import sys
import os
from envyaml import EnvYAML
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

# Load configuration
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Model configuration
LLM_MODEL = "xai.grok-4"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

def main():
    """Main function demonstrating MCP integration with OpenAI Responses API."""

    # Load configuration and initialize OCI client
    config = EnvYAML(SANDBOX_CONFIG_FILE)

    llm_client = OCIOpenAIHelper.get_sync_native_client(
        config=config,
    )

    # MCP server configurations
    # Note: Update ngrok URLs when tunnels change
    server_tools = [
        {
            "type": "mcp",
            "server_label": "deepwiki",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "require_approval": "never",
        },
        {
            "type": "mcp",
            "server_label": "weather",
            "server_url": "https://f2c262f761d7.ngrok-free.app/mcp",  # Update with current ngrok URL
            "require_approval": "never",
        }
    ]

    # Create response with MCP tool calling
    response = llm_client.responses.create(
        model=LLM_MODEL,
        store=False,
        tools=server_tools,
        input="What is the weather in San Francisco, are there any weather alerts?"
    )

    print("AI Response:", response.output_text)

if __name__ == "__main__":
    main()
