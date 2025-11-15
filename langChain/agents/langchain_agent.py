""" This file is showcasing a simple agent constitution using langchain new method `create_agent` """

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

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-fast-non-reasoning"
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
# Step 3: Build some tools to give the agent
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

# Step 4: create the agent
agent = create_agent(
    model=openai_llm_client,
    tools=tools,
    system_prompt="You are a helpful assistant, infer the details missing from the user",
    # response_format=<Pydantic class, provide as class to agent response format>
)
print(f"************************** Agent ready **************************")

MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

# Calling the agent with stream mode to see the different tools and responses
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


print(f"************************** Agent single step invoke **************************")
# Single step agent invokation
result = agent.invoke(
    input={"messages": [HumanMessage(MESSAGE)]}
)
# Final result from agent
print(result['messages'][-1].content)

print(f"************************** Agent full response state **************************")
# Full result
for message in result['messages']:
    print("Agent step message:")
    print(message)