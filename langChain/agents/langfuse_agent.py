""" Sample langfuse integration using the langchain agent """
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

import sys
import os
from typing import Any

from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
from envyaml import EnvYAML
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

# Langfuse reference: https://langfuse.com/integrations/frameworks/langchain

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
# LLM_MODEL = "openai.gpt-4.1"
# LLM_MODEL = "openai.gpt-5"
# xai.grok-4
# xai.grok-3
# available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

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

# Simple model
openai_llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

# Some tool(s)
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

# Simple agent
agent = create_agent(
    model=openai_llm_client,
    tools=tools,
    system_prompt="Use the tools when requested, you are a helpful assistant",
    name="Sample_workshop_agent"                        # Name to identify the agent in tracing
)

config:RunnableConfig = {
    "callbacks": [langfuse_handler],
    "metadata":{
        "langfuse_user_id": "some_user_id",             # To differenciate across users using our applications
        "langfuse_session_id": "session-1234",          # Store all the traces in one single session for multiturn conversations
        "langfuse_tags": ["workshop", "langfuse-test"]  # Add tags to filter in the console
    }}

MESSAGE = "Which will be my projected bill? I'm in San Frnacisco, and I have oven. My past bill was $45"

print(f"************************** Agent stream invokation and details for each step **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]}, 
    stream_mode="values",
    config=config
):
    # Messages are added to the agent state, that is why we access the last message
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        # Check any tool calls
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")