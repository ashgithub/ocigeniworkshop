"""
What this file does:
Demonstrates OCI OpenAI Responses API integration with remote MCP servers. The
model can call remote MCP tools directly through `responses.create()`.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OpenAI Responses API with MCP: https://platform.openai.com/docs/guides/tools-connectors-mcp
- Model Context Protocol overview: https://modelcontextprotocol.io
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Environment setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Loads environment variables if needed.

How to run the file:
1. Start the weather MCP server: `uv run langChain/function_calling/mcp/weather_mcp_server.py`
2. Expose it if needed with ngrok: `ngrok http 8000 --host-header=localhost:8000`
3. Run this client: `uv run langChain/function_calling/mcp/openai_responses_mcp.py`

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code
"""

import sys
import os
from envyaml import EnvYAML
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

# Load configuration
SANDBOX_CONFIG_FILE = "sandbox.yaml"
WEATHER_MCP_DEFAULT_URL = "https://94b180f22830.ngrok-free.app/mcp"

load_dotenv()

# Model configuration
# LLM_MODEL = "xai.grok-4"
LLM_MODEL = "openai.gpt-5"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

def main() -> None:
    """Main function demonstrating MCP integration with OpenAI Responses API."""

    # Load configuration and initialize OCI client
    config = EnvYAML(SANDBOX_CONFIG_FILE)

    print("=" * 70)
    print("🔔  MCP DEMO SETUP REMINDER")
    print("=" * 70)
    print("1. Start the Weather MCP server:")
    print("   uv run langChain/function_calling/mcp/weather_mcp_server.py")
    print("2. Expose it with ngrok (replace 8000 if you changed the port):")
    print("   ngrok http 8000 --host-header=localhost:8000")
    print("3. Paste the active ngrok URL below when prompted.\n")

    if sys.stdin.isatty():
        prompt = (
            "Enter Weather MCP ngrok URL (press Enter to use default\n"
            f"[{WEATHER_MCP_DEFAULT_URL}]): "
        )
        user_weather_url = input(prompt).strip()
    else:
        user_weather_url = ""

    weather_mcp_url = user_weather_url or WEATHER_MCP_DEFAULT_URL
    if not user_weather_url:
        print(f"Using default Weather MCP URL: {weather_mcp_url}\n")

    llm_client = OCIOpenAIHelper.get_sync_openai_client(
        config=config,
    )

    # MCP server configurations
    # Weather MCP URL is provided interactively above
    server_tools = [
        {
            "type": "mcp",
            "server_label": "deepwiki",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "require_approval": "never",
        },
          {
            "type": "mcp",
            "server_label": "tiktoken",
            "require_approval": "never",
            "server_url": "https://gitmcp.io/openai/tiktoken",
            "allowed_tools": ["fetch_tiktoken_documentation"]
        }
       
    ]

    print("Running sample query with MCP tools...\n")

    # Create response with MCP tool calling
    response = llm_client.responses.create(
        model=LLM_MODEL,
        store=False,
        tools=server_tools,
        input = "Whay is BPE in tiktoken specification?"
        #other question to ask 
        #input="What is weather in arlington, va",
        #input="What transport protocols does the 2025-03-26 version of the MCP spec (modelcontextprotocol/modelcontextprotocol) support?"
    )

    print("AI Response:", response.output_text)

if __name__ == "__main__":
    main()
