import json
from langchain_oci.chat_models import ChatOCIGenAI
from langchain_core.tools import tool
from openai_oci_client import OciOpenAILangGraphClient
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
# NEW langchain version: https://docs.langchain.com/oss/python/langchain/agents
# Version langchain 1.0.0 not compatible with langchain_oci current version 0.1.5

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

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = " sandbox.json"

LLM_MODEL = "xai.grok-3" # meta-llama models are eager to have trouble in multistep invokations

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024

# Models should be used with extra library since langchain-oci is still behind on latest langchain create_agent methods
# openai.gpt-4.1
# openai.gpt-4o
# xai.grok-4
# xai.grok-3


llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{config_path}': {e}")
        return None

# Step 1: load the config file
scfg = load_config(SANDBOX_CONFIG_FILE)

# Step2 : Build an OCI LLM client (cohere models)
# Only supports cohere models, openai and grok models get toolId error due to unsupported type from langchain-oci calls
llm_client = ChatOCIGenAI(
    model_id= LLM_MODEL,
    service_endpoint= llm_service_endpoint,
    compartment_id= scfg['oci']['compartment'],
    auth_file_location= scfg["oci"]["configFile"],
    auth_profile= scfg["oci"]["profile"],
    model_kwargs={
        "temperature":0.7,
        "max_tokens": 500
    }
)

# Use the openai client to enable grok and openai models with toolId for multiple steps
openai_llm_client = OciOpenAILangGraphClient(
    model_name=LLM_MODEL,
    profile=scfg['oci']['profile'],
    compartment_id=scfg['oci']['compartment'],
    service_endpoint= llm_service_endpoint
)

# Step 3: build a simple prompt template for the agent.
prompt = ChatPromptTemplate.from_messages(
     [
        ("system", "You are a helpful assistant"),
        ("human", "{input}"),
        # Placeholders fill up a **list** of messages
        MessagesPlaceholder(variable_name="agent_scratchpad"),
     ]
)

# Step 4: agent
# Create an agent, tool_calling is the best to manage the auto tool calls and responses
# Also available create_react_agent, which is best for single tool call, not multiple
# Review langchain_step for create_react_agent example
agent = create_tool_calling_agent(
    llm=llm_client, # Use with cohere models
    # llm=openai_llm_client, # Uncomment to use the openai models
    tools=tools,
    prompt=prompt
)

# Step 5: build agent executor
# Verbose response for highlight the steps, verbose = False for better clarity in streaming
agent_executor = AgentExecutor(agent=agent,tools=tools, verbose=True)

# Step 6: streaming the function steps
print(f"************************** Agent Step invoke and details for each step **************************") 
for step in agent_executor.stream({'input': "Which will be my projected bill? I'm in San Frnacisco, and I have oven. My past bill was $45"}):
    print("\nChain step:")
    print(step)