import sys
import os
from typing import Any

from langchain_core.tools import tool
from dotenv import load_dotenv
from envyaml import EnvYAML
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

# LangGraph agent reference: https://docs.langchain.com/oss/python/langgraph/workflows-agents#agents

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#
#
#  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
#  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
#  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
#  if you have errors running sample code reach out for help in #igiu-ai-learning
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4"
# LLM_MODEL = "openai.gpt-4.1"
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

# Step 2: create the OpenAI LLM client using credentials and optional parameters

openai_llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

# How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
# Build some tools for the agent
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


# This tool depends on weather, which is information that the model initially doesn't have
# Requires the model to reason and call first the get_weather tool to complete the arguments in the bill projection
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
# Bind the tools to the client
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

# node to process all the tool calls and give the response to the model
def tool_node(state:MessagesState) -> dict[Any,Any]:
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls: # type: ignore[attr-defined]
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
# This function is in charge of deciding if the graph should finish or go back to the model for response
def should_continue(state: MessagesState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls: # type: ignore[attr-defined]
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
# Conditional edge that decides if the flow is done
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile(checkpointer=InMemorySaver())
print(f"************************** Agent graph compiled **************************")

# Invoke
MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

config: RunnableConfig = {"configurable": {"thread_id": "1"}} # thread for the agent memory

print(f"************************** Agent stream invokation and details for each step **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]},
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

print(f"************************** Agent single step invoke **************************")
# Single step agent invokation
result = agent.invoke(
    input={"messages": [HumanMessage(MESSAGE)]},
    config=config
)
print(result['messages'][-1].content)

print(f"************************** Agent full response state **************************")
# Full result
for message in result['messages']:
    print("Agent step message:")
    print(message)