"""
What this file does:
Demonstrates creating a LangChain agent that integrates with MCP (Model Context Protocol) servers to provide weather and bill projection tools using OCI Generative AI for LLM.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- LangChain: https://docs.langchain.com/oss/python/langchain/agents
- LangChain MCP clients: https://docs.langchain.com/oss/python/langchain/mcp#model-context-protocol-mcp
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/function_calling/mcp/langchain_host.py

Comments to important sections of file:
- Step 1: Load configuration and initialize OCI client
- Step 2: Set up MCP client with multiple servers (weather and bill projection)
- Step 3: Create manual agent execution loop (temporary workaround for async issues)
- Step 4: Execute the agent with tool calling capabilities
"""

import sys
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.messages import HumanMessage

from envyaml import EnvYAML
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

# MCP docs: https://modelcontextprotocol.io/docs/getting-started/intro
# LangChain MCP clients/host: https://docs.langchain.com/oss/python/langchain/mcp#model-context-protocol-mcp

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

# Step 1: Load configuration and initialize OCI client
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Build the OCI client
llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

# Function to bind the tools
async def build_oci_model():
    # MCP client connection using langchain mcp
    client = MultiServerMCPClient(  
            {
                "weather": {
                    "transport": "streamable_http",  # HTTP-based remote server
                    "url": "http://localhost:8000/mcp",
                },
                "bill_server": {
                    "command": "python",
                    # TODO: Make sure to update to the full absolute path to your
                    # local run file
                    # bill_server.py file
                    "args": ["./langChain/function_calling/mcp/bill_mcp_server.py"],
                    "transport": "stdio",
                },
            }
        )

    tools = await client.get_tools()

    """ 
    TODO:
    Important notice: Async calls using langchain are in process for oci_openai library, 
    when solved, from here, you can use the following snippet instead of the call_manual_agent function:

    ```python
        from langchain.agents import create_agent
        agent = create_agent(
            model=llm_client,
            tools=tools
        )

        response = await agent.ainvoke(
            input={'messages':[HumanMessage("Which will be my projected bill? I'm in San Francisco, and I have oven. My past bill was $45")]}
        )

        for message in response:
            print(message)
    ```

    call_manual_agent is a temporary solution given the ainvoke method is yet not supported by oci_openai client
    Error present (11/14/2025)
    `openai.BadRequestError: Error code: 400 - {'code': '400', 'message': 'The given api key not found'}`
    """
    
    tooled_model = llm_client.bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    for name, tool in tools_by_name.items():
        print(f"Tool discovered:{name}")
        print(f"Tool description:{tool.description}")

    return tooled_model, tools_by_name

async def call_manual_agent():
    """ Function to make manual call to agent with tools to substitute agent.ainvoke call"""
    """ This is the same method as langchain_multistep_manual.py file """

    prompt = "Which will be my projected bill? I'm in San Francisco, and I have oven. My past bill was $45"
    messages = [HumanMessage(prompt)]

    # Get the tooled model and the tool names list
    llm_client_with_tools, tools_by_name = await build_oci_model()
    while True:
        # 1. Get the AI response. Messages is the full context list
        ai_message = llm_client_with_tools.invoke(messages)
        print(f"\nAI Response: {ai_message.content}")
        # print(ai_message) # Try looking at the full ai response data

        # 2. Check if there are tool calls in the last ai response
        if not getattr(ai_message, "tool_calls", None):
            # End the flow if the model is done with tool calls
            print("\nNo tool calls detected — conversation finished.")
            break

        print(f"\n************************ Tool calls detected ************************")
        # Add the latest ai message to context list
        messages.append(ai_message)

        # 3. Execute all the tool calls using invoke method and the tool map
        for tool_call in ai_message.tool_calls:
            # Get first the tool name
            tool_name = tool_call["name"].lower()
            selected_tool = tools_by_name.get(tool_name)

            # Safety
            if not selected_tool:
                print(f"Unknown tool requested: {tool_name}")
                continue

            # Invoke tool if present in the map and get the content
            print(f"\nExecuting tool: {tool_name}")
            tool_msg = await selected_tool.ainvoke(tool_call)
            print(f"Tool result: {tool_msg.content}")
            # print(tool_msg) # Try looking at the full tool response data

            # 4. Append the tool result to the message context list, so the model has the tool response
            messages.append(tool_msg)

if __name__ == "__main__":
    import asyncio
    asyncio.run(call_manual_agent())
