"""
What this file does:
Demonstrates how to build a LangGraph-based agent with tool-calling
capabilities for weather, city, and clothing recommendations.

Documentation to reference:
- LangGraph: https://langchain-ai.github.io/langgraph/
- LangChain Tools: https://docs.langchain.com/oss/python/langchain/tools
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/langgraph_agent.py

Important sections:
- Step 1: Load configuration
- Step 2: Create the OCI-backed LangChain client
- Step 3: Define tools and graph nodes
- Step 4: Compile and run the graph
"""

import os
import sys
from typing import Any

from langchain_core.tools import tool
from dotenv import load_dotenv
from envyaml import EnvYAML
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-fast-reasoning"
#LLM_MODEL = "xai.grok-4-fast-non-reasoning"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

# Step 1: Load configuration
def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: Create the OCI-backed LangChain client
openai_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg,
)


# Step 3: Define tools and graph nodes
@tool
def get_weather(zipcode: int, date: str) -> dict[str, Any]:
    """Return sample weather data for a zipcode and date in yyyy-mm-dd format."""

    return {
        "rain": True,
        "min_temperature": "50 F",
        "max_temperature": "62 F",
    }


@tool
def get_city(criteria: str) -> dict[str, Any]:
    """Recommend a city based on the supplied criteria."""

    return {
        "city_name": "Chicago",
        "zipcode": 60601,
    }


@tool
def get_clothes(gender: str, temp: int, rain: bool) -> dict[str, list[str]]:
    """Suggest clothing and accessories based on the provided conditions."""

    return {
        "clothes": ["rain coat", "jeans", "formal shirt"],
        "accessories": ["watch", "umbrella", "boots"],
    }


tools = [get_weather, get_city, get_clothes]
tools_by_name = {tool.name: tool for tool in tools}

llm_with_tools = openai_llm_client.bind_tools(tools)


def llm_call(state: MessagesState) -> dict[str, list[Any]]:
    """Call the model and let it decide whether a tool is needed."""
    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant. Infer the information missing from the user if needed."
                    )
                ]
                + state["messages"]
            )
        ]
    }


def tool_node(state: MessagesState) -> dict[str, list[ToolMessage]]:
    """Execute each requested tool call and return the resulting tool messages."""

    result = []
    for tool_call in state["messages"][-1].tool_calls:  # type: ignore[attr-defined]
        selected_tool = tools_by_name[tool_call["name"]]
        observation = selected_tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: MessagesState) -> str:
    """Route to the tool node when the model requests tool calls, otherwise end."""

    last_message = state["messages"][-1]
    if last_message.tool_calls:  # type: ignore[attr-defined]
        return "tool_node"
    return END


agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")


# Step 4: Compile and run the graph
agent = agent_builder.compile(checkpointer=InMemorySaver())
print("************************** Agent graph compiled **************************")

MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

print("************************** Agent stream invocation and step details **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]},
    config=config,
    stream_mode="values",
):
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")

print("************************** Agent single-step invoke **************************")
result = agent.invoke(input={"messages": [HumanMessage(MESSAGE)]}, config=config)
print(result["messages"][-1].content)

print("************************** Agent full response state **************************")
for message in result["messages"]:
    print("Agent step message:")
    print(message)
