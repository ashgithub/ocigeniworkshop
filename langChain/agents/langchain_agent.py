import sys
import os

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.messages import HumanMessage
from dotenv import load_dotenv
from envyaml import EnvYAML

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

# Step 4: agent
# Create an agent, tool_calling is the best to manage the auto tool calls and responses
# Also available create_react_agent, which is best for single tool call, not multiple
# Review langchain_step for create_react_agent example
agent = create_agent(
    model=openai_llm_client,
    tools=tools,
    system_prompt="You are a helpful assistant",
    # response_format=<Pydantic class, provide as class to agent response format>
)

# Step 5: build agent executor
# Verbose response for highlight the steps

# Step 6: calling the executor
MESSAGE = "Which will be my projected bill? I'm in San Frnacisco, and I have oven. My past bill was $45"

print(f"************************** Agent stream invokation and details for each step **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]}, 
    stream_mode="values",
):
    # Messages are added to the agent state, that is why we access the last message
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        # Check any tool calls
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")

# Single step agent invokation
result = agent.invoke(
    input={"messages": [HumanMessage(MESSAGE)]}
)

print(f"************************** Agent single step invoke **************************")
print(result['messages'][-1].content)

print(f"************************** Agent full response state **************************")
# Full result
print(result)