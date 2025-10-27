import json
from langchain_oci.chat_models import ChatOCIGenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
# NEW langchain version: https://docs.langchain.com/oss/python/langchain/agents
# Version langchain 1.0.0 not compatible with langchain_oci current version 0.1.5

@tool
def get_weather(city:str) -> str:
    """ Gets the weather for a given city """
    return f"The weather in {city} is 70 Fahrenheit"

@tool
def get_projection_bill(current_bill:int, gas_oven:bool) -> int:
    """ Returns the projected bill for a user depending on the current one and if it has or not oven """
    if gas_oven:
        return current_bill + 45
    return current_bill + 4

tools = [get_weather,get_projection_bill]

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/Test/ocigeniworkshop/sandbox.json"

LLM_MODEL = "cohere.command-r-08-2024"

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
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

# Step 1: Load the config file
scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: create a LLM client using the credentials and optional parameters
llm_client = ChatOCIGenAI(
    model_id= LLM_MODEL,
    service_endpoint= llm_service_endpoint,
    compartment_id= scfg['oci']['compartment'],
    auth_file_location= scfg["oci"]["configFile"],
    auth_profile= scfg["oci"]["profile"],
    model_kwargs={
        "temperature":0.7,
        "max_tokens": 500,
        # "preamble_override": PREAMBLE, # Not supported by openai / grok / meta models
        "is_stream": False,
        "seed": 7555,
        "top_p": 0.7,
        "top_k": 1, # Different from 0 for meta models
        # "frequency_penalty": 0.0 # Not supported by openai / grok models
    }
)

# Step 3: Define a prompt template to use by the agent
REACT_PROMPT = PromptTemplate.from_template(
    """You are a helpful AI assistant. You have access to the following tools:

{tools}

Tool Names: {tool_names}

When you need to use a tool, reply with:
Action: <tool name>
Action Input: <tool input>

If you know the answer, reply with:
Final Answer: <your answer>

Begin!

Question: {input}
{agent_scratchpad}"""
)

# Step 4: Create the agent
# Using react agent which is better managing a single tool call
# For latest lanchain version 1.0.0 use only create_agent: https://docs.langchain.com/oss/python/langchain/agents
agent = create_react_agent(llm_client, tools=tools, prompt=REACT_PROMPT)

# Step 5: create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)  # verbose shows tool usage. Use False for clarity

# Step 6: call the stream function
print(f"************************** Agent single step invokation with streaming steps **************************") 
for step in agent_executor.stream({'input': "How is the weather in San Francisco?"}):
    print("Chain step:\n")
    print(step)