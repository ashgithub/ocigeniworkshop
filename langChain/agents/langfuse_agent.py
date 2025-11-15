"""
What this file does:
Demonstrates Langfuse integration with LangChain agents for tracing and monitoring tool-calling workflows with weather, city, and clothing recommendation tools.

Documentation to reference:
- Langfuse: https://langfuse.com/integrations/frameworks/langchain
- LangChain Agents: https://python.langchain.com/docs/concepts/agents/
- LangChain Tools: https://python.langchain.com/docs/how_to/custom_tools/
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
uv run langChain/agents/langfuse_agent.py

Comments to important sections of file:
- Step 1: Load configuration and initialize Langfuse
- Step 2: Define agent tools
- Step 3: Create agent with tracing configuration
- Step 4: Run agent with streaming execution
"""
import sys
import os
import datetime

from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
from envyaml import EnvYAML
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-fast-non-reasoning"
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

# Step 1: First build the client with the langfuse keys on .env file
langfuse = Langfuse(
    public_key=scfg['langfuse']['langfuse_pk'],
    secret_key=scfg['langfuse']['langfuse_sk'],
    host=scfg['langfuse']['langfuse_host']
)

# Step 2: build the call back. Calls handler to enable tracing
langfuse_handler = CallbackHandler()

# Simple model to do the tracing
openai_llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

# How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
# Some tools to give the model
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

# Simple agent to perform tracing
agent = create_agent(
    model=openai_llm_client,
    tools=tools,
    system_prompt="Use the tools when requested, you are a helpful assistant",
    name="Sample_workshop_agent"    # Name to identify the agent in tracing
)
print(f"************************** Agent ready **************************")

# Step 3: on the runnable config of the call, add the langfuse parameters

config:RunnableConfig = {
    "callbacks": [langfuse_handler],                    # Add the calls back
    "metadata":{                                        # Extra metadata to use (optional, but useful)
        "langfuse_user_id": os.getenv("MY_PREFIX", "default_user"),             # To differenciate across users using our applications
        "langfuse_session_id": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"),          # Store all the traces in one single session for multiturn conversations
        "langfuse_tags": ["workshop", os.getenv("MY_PREFIX", "user-name")]      # Add tags to filter in the console. TODO: Add your own identificator to filter later on on the web interface
    }}

MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

# Step 4: invoke the agent as normal, the traces are auto
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
