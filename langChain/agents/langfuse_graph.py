"""
What this file does:
Demonstrates Langfuse integration with a LangGraph workflow, including
observability decorators and a secondary summarization step.

Documentation to reference:
- Langfuse: https://langfuse.com/integrations/frameworks/langchain
- Langfuse observe decorator: https://langfuse.com/docs/observability/sdk/python/instrumentation
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and Langfuse settings.
- .env: Loads environment variables if required.
Note: sign up at langfuse to get the langfuse keys. TRAINING ONLY. Use Oracle hosted instance for any official work 

How to run the file:
uv run langChain/agents/langfuse_graph.py

Important sections:
- Step 1: Load configuration and initialize Langfuse
- Step 2: Create model clients and define tools
- Step 3: Build the LangGraph workflow
- Step 4: Run the graph with Langfuse tracing enabled
"""

import datetime
import os
import sys
from typing import Any

from langchain_core.tools import tool
from langfuse import Langfuse, observe
from langfuse.langchain import CallbackHandler
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

LLM_MODEL = "xai.grok-4-1-fast-non-reasoning"
SECONDARY_LLM_MODEL = "openai.gpt-5.4"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

# Step 1: Load configuration and initialize Langfuse
def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

langfuse = Langfuse(
    public_key=scfg["langfuse"]["langfuse_pk"],
    secret_key=scfg["langfuse"]["langfuse_sk"],
    host=scfg["langfuse"]["langfuse_host"],
)
try:
    langfuse_enabled = langfuse.auth_check()
except Exception as exc:
    langfuse_enabled = False
    print(f"Langfuse auth check failed: {exc}")
if not langfuse_enabled:
    print("Langfuse auth check failed. Continuing without Langfuse callback export.")
langfuse_handler = CallbackHandler() if langfuse_enabled else None


def observe_if_enabled():
    """Use Langfuse decorators only when credentials are valid."""

    if langfuse_enabled:
        return observe()

    def decorator(func):
        return func

    return decorator


def update_current_span_metadata(metadata: dict[str, Any]) -> None:
    """Attach metadata when Langfuse tracing is authenticated."""

    if langfuse_enabled:
        langfuse.update_current_span(metadata=metadata)


# Step 2: Create model clients and define tools
openai_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg,
)
secondary_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=SECONDARY_LLM_MODEL,
    config=scfg,
)


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
    """Call the primary model and let it decide whether a tool is needed."""
    return {
        "messages": [
            llm_with_tools.invoke(
                [SystemMessage(content="You are a helpful assistant.")] + state["messages"]
            )
        ]
    }


@observe_if_enabled()
def tool_node(state: MessagesState) -> dict[str, list[ToolMessage]]:
    """Execute each requested tool call and attach trace metadata."""

    result = []
    for tool_call in state["messages"][-1].tool_calls:  # type: ignore[attr-defined]
        selected_tool = tools_by_name[tool_call["name"]]
        update_current_span_metadata(
            {
                "tags": ["using_tools"],
                "tool_name": selected_tool.name,
            }
        )
        observation = selected_tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: MessagesState) -> str:
    """Route to the tool node when tools are requested; otherwise summarize."""

    last_message = state["messages"][-1]
    if last_message.tool_calls:  # type: ignore[attr-defined]
        return "tool_node"
    return "summary_agent"


@observe_if_enabled()
def second_client(state: MessagesState) -> dict[str, list[dict[str, str]]]:
    """Use a secondary model to summarize the workflow output."""

    query = f"Make a summary in less than 100 words of this response: {state['messages']}"
    response = secondary_llm_client.invoke(query)
    update_current_span_metadata(
        {"other_detail": "Included additional summary metadata"}
    )

    return {"messages": [{"role": "assistant", "content": response.content}]}


# Step 3: Build the LangGraph workflow
agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_node("summary_agent", second_client)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", "summary_agent"])
agent_builder.add_edge("tool_node", "llm_call")
agent_builder.add_edge("summary_agent", END)


agent = agent_builder.compile(
    checkpointer=InMemorySaver(),
    name="main_workshop_graph",
)
print("************************** Agent graph compiled **************************")

MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"


# Step 4: Run the graph with Langfuse tracing enabled
config: RunnableConfig = {
    "configurable": {"thread_id": "1"},
    "callbacks": [langfuse_handler] if langfuse_handler else [],
    "metadata": {
        "langfuse_user_id": os.getenv("MY_PREFIX", "default_user"),
        "langfuse_session_id": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"),
        "langfuse_tags": ["workshop", os.getenv("MY_PREFIX", "user-name")],
    },
}

print("************************** Agent stream invocation and step details **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]},
    stream_mode="values",
    config=config,
):
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
