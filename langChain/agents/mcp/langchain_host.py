import sys
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import SystemMessage,ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

from typing import Any
from envyaml import EnvYAML
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/ocigeniworkshop/sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

# Step 1: Load config and initialize client
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

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
                "cinema":{
                    "transport": "streamable_http",  # HTTP-based remote server
                    "url": "http://localhost:8001/mcp",
                }
            }
        )

    tools = await client.get_tools()
    tooled_model = llm_client.bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    return tooled_model, tools_by_name

async def build_langgraph_agent():
    """ This function builds a langgraph agent in order to make async calls with the openai client """
    llm_with_tools, tools_by_name = await build_oci_model()
    
    def llm_call(state: MessagesState):
        """LLM decides whether to call a tool or not"""
        system_instructions = [SystemMessage("You are a helpful assistant, Infer information if missing")]
        return {"messages": [llm_with_tools.invoke( system_instructions + state["messages"])]}

    async def tool_node(state:MessagesState) -> dict[Any,Any]:
        """Performs the tool call"""
        result = []
        for tool_call in state["messages"][-1].tool_calls: # type: ignore[attr-defined]
            tool = tools_by_name[tool_call["name"]]
            observation = await tool.ainvoke(tool_call["args"])
            result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
        return {"messages": result}

    def should_continue(state: MessagesState) -> str:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls: # type: ignore[attr-defined]
            return "tool_node"
        return END

    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call",should_continue,["tool_node", END])
    agent_builder.add_edge("tool_node", "llm_call")
    agent = agent_builder.compile(checkpointer=InMemorySaver())

    return agent

async def call_agent():
    agent = await build_langgraph_agent()

    # Invoke
    prompt = "What is the weather in NYC?"
    # prompt = "Which are the movies available for today at CA?"
    config: RunnableConfig = {"configurable": {"thread_id": "1"}} # thread for the agent memory

    print(f"************************** Agent stream invokation and details for each step **************************")
    async for chunk in agent.astream(
        input={"messages": [HumanMessage(prompt)]},
        config=config,
        stream_mode="values",
    ):
        # Messages are added to the agent state, that is why we access the last message
        latest_message = chunk["messages"][-1]
        if latest_message.content:
            print(f"Agent: {latest_message.content}")
        elif latest_message.tool_calls:
            # Check any tool calls
            print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(call_agent())