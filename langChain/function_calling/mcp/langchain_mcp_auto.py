"""
What this file does:
Demonstrates creating a LangChain agent that integrates with MCP (Model Context
Protocol) servers to provide weather and bill projection tools using OCI
Generative AI for LLM inference.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- LangChain: https://docs.langchain.com/oss/python/langchain/agents
- LangChain MCP clients: https://docs.langchain.com/oss/python/langchain/mcp#model-context-protocol-mcp
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or running this code

Env setup:
- sandbox.yaml: Contains OCI tenancy, compartment, and wallet details.
- .env: Load environment variables (e.g., API keys) consumed by load_dotenv.

How to run the file:
uv run langChain/function_calling/mcp/langchain_mcp_auto.py

Comments to important sections of file:
- Step 1: Load configuration and initialize OCI client
- Step 2: Set up MCP client with weather and bill projection servers
- Step 3: Create the async agent workflow (uses ainvoke now that it is supported)
- Step 4: Execute the agent and print the response messages
"""

import asyncio
import os
import sys

from envyaml import EnvYAML
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from oci_openai_helper import OCIOpenAIHelper

load_dotenv()

SANDBOX_CONFIG_FILE = "sandbox.yaml"
LLM_MODEL = "openai.gpt-5.2"

MCP_SERVER_CONFIG = {
    "weather": {
        "transport": "streamable_http",
        "url": "http://localhost:8000/mcp",
    },
    "bill_server": {
        "command": "python",
        "args": ["./langChain/function_calling/mcp/bill_mcp_server.py"],
        "transport": "stdio",
    },
}


def load_config(config_path: str) -> EnvYAML:
    """Load sandbox configuration from YAML or raise if unavailable."""

    try:
        with open(config_path, "r", encoding="utf-8"):
            return EnvYAML(config_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Configuration file '{config_path}' not found."
        ) from exc


def create_llm_client(config: EnvYAML):
    """Instantiate the OCI-backed LangChain client."""

    return OCIOpenAIHelper.get_langchain_openai_client(
        model_name=LLM_MODEL,
        config=config,
    )


async def run_mcp_agent(prompt: str, llm_client, server_config):
    """Create an MCP-enabled agent and stream responses for the given prompt."""

    client = MultiServerMCPClient(server_config)
    tools = await client.get_tools()

    agent = create_agent(model=llm_client, tools=tools)
    response = await agent.ainvoke(
        input={"messages": [HumanMessage(prompt)]}
    )

    return response.get("messages", [])


async def main() -> None:
    """Entrypoint for running the demo agent."""

    #prompt = "what is the weather in San Francisco, are there any alerts"
    prompt = "Which will be my projected bill? I'm in San Francisco, and I have oven. My past bill was $45"

    config = load_config(SANDBOX_CONFIG_FILE)
    llm_client = create_llm_client(config)

    messages = await run_mcp_agent(prompt, llm_client, MCP_SERVER_CONFIG)
    for message in messages:
        print(getattr(message, "content", message))


if __name__ == "__main__":
    asyncio.run(main())