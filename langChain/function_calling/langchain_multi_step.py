import sys,os
from langchain.agents import  create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

# How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
# NEW langchain version: https://docs.langchain.com/oss/python/langchain/agents
# Version langchain 1.0.0 not compatible with langchain_oci current version 0.1.5



#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL =  "openai.gpt-5"

# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# openai.gpt-4.1
# openai.gpt-4o
# xai.grok-4
# xai.grok-3

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

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def pretty_print(response):
    for i, m in enumerate(response["messages"], 1):
        role = getattr(m, "type", m.__class__.__name__)
        content = m.content if isinstance(m.content, str) else str(m.content)
        print(f"{i:>2}. [{role.upper()}] {content}")

# Step 1: Load the config file        
scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: create the OpenAI LLM client using credentials and optional parameters

llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg, 
    use_responses_api=True,
    reasoning={"effort": "low", "summary": "auto"}
)


# Step 3: Create the agent
# refer  https://docs.langchain.com/oss/python/langchain/agents
agent = create_agent(llm_client, tools=tools ,system_prompt="use one or more tools to get an response, once you have teh answer use hingish (hindi mixed with english to answer)")



# Step 4: calling the agent
print(f"************************** Agent Multi-Step invoke and details for each step **************************") 
messages =  [HumanMessage(content="Which will be my projected bill? I'm in San Frnacisco, and I have oven. My past bill was $45")]
response = agent.invoke({"messages":messages})
pretty_print(response)
#print(response)

print(f"************************** Agent Multi-Step stream **************************") 
for chunk in agent.invoke({"messages":messages},stream_mode="updates"):
    for step, data in chunk.items():
        print(f"step: {step}", flush=True)
        print(f"content: {data['messages'][-1].content_blocks}",flush=True)