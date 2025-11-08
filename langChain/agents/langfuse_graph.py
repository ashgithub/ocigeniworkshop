""" Sample langfuse example with a complex step graph """
import sys
import os
from typing import Any

from langchain_core.tools import tool
from langfuse import Langfuse, observe
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv
from envyaml import EnvYAML
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#
#
#  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
#  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
#  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
#  if you have errors running sample code reach out for help in #igiu-ai-learning
#####

SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4"
SECONDARY_LLM_MODEL = "openai.gpt-4.1"
# LLM_MODEL = "openai.gpt-5"
# xai.grok-4
# xai.grok-3
# available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

# Step 1: load config 

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Langfuse API connection
langfuse = Langfuse(
    public_key=scfg['langfuse']['langfuse_pk'],
    secret_key=scfg['langfuse']['langfuse_sk'],
    host=scfg['langfuse']['langfuse_host']
)

# Calls handler to enable tracing
langfuse_handler = CallbackHandler()

# Step 2: create the OpenAI LLM client using credentials and optional parameters

openai_llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

secondary_llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

@tool
def get_weather(city:str) -> str:
    """ Gets the weather for a given city """
    return f"The weather in {city} is 70 Fahrenheit"

# This tool depends on weather, which is information that the model initially doesn't have
# Requires the model to reason and call first the get_weather tool to complete the arguments in the bill projection
@tool
def get_projection_bill(current_bill:int, gas_oven:bool, weather:int) -> int:
    """ Returns the projected bill for a user depending on the current one and if it has or not oven, also the weather of the city"""
    if gas_oven:
        return current_bill + 45 + weather
    return current_bill + 4 + weather

tools = [get_weather,get_projection_bill]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = openai_llm_client.bind_tools(tools)

# Nodes
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    # In this function, you can also use a call to a langchain agent using create_agent
    # This function can call any kind of tooled agent of preference
    # Here, we use binded tools just as simplier demonstration.

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant."
                    )
                ]
                + state["messages"]
            )
        ]
    }

@observe()
def tool_node(state:MessagesState) -> dict[Any,Any]:
    """Performs the tool call"""

    langfuse.update_current_trace(
        tags=['using_tools']
    )

    result = []
    for tool_call in state["messages"][-1].tool_calls: # type: ignore[attr-defined]
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls: # type: ignore[attr-defined]
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return "summary_agent"

@observe()
def second_client(state:MessagesState):

    query = f"Make a summary in less than 100 words of the response:{state['messages']}"
    response = secondary_llm_client.invoke(query)

    messages = [{"role":"assistant","content":response.content}]

    langfuse.update_current_trace(
        metadata={"other_detail":"Include other details at the metadata trace"}
    )

    return {"messages":messages}


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_node("summary_agent",second_client)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", "summary_agent"]
)
agent_builder.add_edge("tool_node", "llm_call")
agent_builder.add_edge("summary_agent", END)

# Compile the agent
agent = agent_builder.compile(
    checkpointer=InMemorySaver(),
    name="main_graph"
)

# Invoke
MESSAGE = "Which will be my projected bill? I'm in San Frnacisco, and I have oven. My past bill was $45"

config:RunnableConfig = {
    "configurable": {"thread_id": "1"},
    "callbacks": [langfuse_handler],
    "metadata":{
        "langfuse_user_id": "some_user_id",             # To differenciate across users using our applications
        "langfuse_session_id": "session-1234",          # Store all the traces in one single session for multiturn conversations
        "langfuse_tags": ["workshop", "langfuse-test"]  # Add tags to filter in the console
    }}

for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]}, 
    stream_mode="values",
    subgraphs=True,
    config=config
):
    # Messages are added to the agent state, that is why we access the last message
    latest_message = chunk[1]["messages"][-1] # type: ignore[attr-defined]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        # Check any tool calls
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")