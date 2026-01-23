"""
What this file does:
Sample Langfuse integration with a complex step graph including advanced observation features for tracing and monitoring agent workflows.

Documentation to reference:
- Langfuse: https://langfuse.com/integrations/frameworks/langchain
- Langfuse observe decorator: https://langfuse.com/docs/observability/sdk/python/instrumentation
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/agents/langfuse_graph.py

Comments to important sections of file:
- Step 1: Load configuration and initialize Langfuse
- Step 2: Create LLM clients and tools
- Step 3: Build LangGraph agent with observation decorators
- Step 4: Configure and run agent with tracing
"""

import sys
import os
import datetime
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

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-fast-non-reasoning"
SECONDARY_LLM_MODEL = "openai.gpt-4.1"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

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

# Step 2: connect to langfuse, using the keys over .env file
langfuse = Langfuse(
    public_key=scfg['langfuse']['langfuse_pk'],
    secret_key=scfg['langfuse']['langfuse_sk'],
    host=scfg['langfuse']['langfuse_host']
)

# Step 3: Calls handler to enable tracing
langfuse_handler = CallbackHandler()

# Simple client
openai_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg
)

# Secondary example client for demonstration
secondary_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg
)

# How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
# Build some tools to give the main agent
@tool
def get_weather(zipcode:int, date:str) -> dict[str,bool | int]:
    """ Gets the weather for a given city zipcode and date in format yyyy-mm-dd """
    
    # This is simple hardcoded data, could use zip code to fetch weather API and get real results
    city_weather = {
        "rain": True,
        "min_temperature": "50 f",
        "max_temperature": "62 f"
    }

    return city_weather

@tool
def get_city(criteria:str) -> dict[str,int|str]:
    """ Based on the criteria given, recommends the user a city and provides the city name and zipcode """

    # This tool could use criteria + LLM + maps API to find the  best city
    city_details = {
        "city_name": "Chicago",
        "zipcode": 60601
    }

    return city_details
    
@tool
def get_clothes(gender:str, temp:int, rain:bool) -> dict[str,list[str]]:
    """ Tool to suggest best clothes depending on the city weather, temperature and genders """

    # Hardcoded data, could use any other user details
    clothes = {
        "clothes": ["ran coat", "jeans", "formal chemise"],
        "accessories": ["watch","umbrella", "boots"]
    }

    return clothes

tools = [get_weather,get_city,get_clothes]
tools_by_name = {tool.name: tool for tool in tools}

# This is the main agent that will perform all the tool calls
llm_with_tools = openai_llm_client.bind_tools(tools)

######### Nodes of the graph #########
# node to call the llm
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    # In this function, you can also use a call to a langchain agent using create_agent
    # This function can call any kind of tooled agent of preference
    # Here, we use binded tools just as simplier demonstration.

    return {
        "messages": [
            # Main agent using tools (model + tools bind)
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

# Node to call each tool
# this node includes teh observe decorator, which indicates langfuse to add this particular state to the trace
# observe decorator works as an extra step to add information to the auto traces generated by default
# could be used with functions that are not common to show up of with some outputs
@observe()
def tool_node(state:MessagesState) -> dict[Any,Any]:
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls: # type: ignore[attr-defined]
        tool = tools_by_name[tool_call["name"]]

        # Some example on how you can update the langfuse trace after using the decorator
        # Useful for manual or specific values updates when required in debug
        # In this case, we are sending as metadata the tool name and adding a filtering tag
        langfuse.update_current_trace(
            tags=['using_tools'],
            metadata={"tools":tool}
        )

        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
# This is a conditional extra steps that guides the graph to keep calling the main model or pass to the secondary node
# When passing to the secondary agent node, means all the tools and details are ready
def should_continue(state: MessagesState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls: # type: ignore[attr-defined]
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return "summary_agent"

# Second agent node using observe decorator
# As an example, after the main agent performs all the tool calls, you can chain other agents to work with the output of the previous ones
# In this case, after performing all the tool calls, this agent is making a summary of the process
# This node will be also displayed in the traces
@observe()
def second_client(state:MessagesState):

    query = f"Make a summary in less than 100 words of the response:{state['messages']}"
    # Calling the second client
    response = secondary_llm_client.invoke(query)

    messages = [{"role":"assistant","content":response.content}]

    # Some example on how you can update the langfuse trace after using the decorator
    # Useful for manual or specific values updates when required in debug
    langfuse.update_current_trace(
        metadata={"other_detail":"Include other details at the metadata trace"}
    )

    return {"messages":messages}


# Build the agent workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
# Secondary demonstration node
agent_builder.add_node("summary_agent",second_client)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
# Conditional edge that uses the function to route tools
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", "summary_agent"]
)
agent_builder.add_edge("tool_node", "llm_call")
agent_builder.add_edge("summary_agent", END)

# Compile the agent
agent = agent_builder.compile(
    checkpointer=InMemorySaver(),        # checkpointer to memory
    name="main_workshop_graph"           # Name to display in the langfuse UI
)
print(f"************************** Agent graph compiled **************************")

# Invoke
MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

# Step 4: Configure runnable with langfuse parameters from environment
config:RunnableConfig = {
    "configurable": {"thread_id": "1"},                 # Add the thread for the checkpointer
    "callbacks": [langfuse_handler],                    # Add the calls back
    "metadata":{                                        # Extra metadata to use (optional, but useful)
        "langfuse_user_id": os.getenv("MY_PREFIX", "default_user"),             # To differenciate across users using our applications
        "langfuse_session_id": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"),          # Store all the traces in one single session for multiturn conversations
        "langfuse_tags": ["workshop", os.getenv("MY_PREFIX", "user-name")]      # Add tags to filter in the console. TODO: Add your own identificator to filter later on on the web interface
    }}

# Step 4: invoke the agent as normal, the traces are auto
print(f"************************** Agent stream invokation and details for each step **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]}, 
    stream_mode="values",
    config=config
):
    # Messages are added to the agent state, that is why we access the last message
    latest_message = chunk[1]["messages"][-1] # type: ignore[attr-defined]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        # Check any tool calls
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
