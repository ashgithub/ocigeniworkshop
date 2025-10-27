import json
from langchain_oci.chat_models import ChatOCIGenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

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

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/Test/ocigeniworkshop/sandbox.json"

LLM_MODEL = "openai.gpt-4o"

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

# Step 1: load the config file
scfg = load_config(SANDBOX_CONFIG_FILE)

PREAMBLE = """ Use the message context when provided """

# Step 2: build a LLM client
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

# Step 3: Add some messages to the context list
# meta-llama models are eager to have errors when handling multiple or parallel tool calls, try making one request per time
messages = [HumanMessage("Which will be my projected bill? I'm in San Frnacisco, and I have oven. My past bill was $45")]

# Step 4: map the tools for easier invokation over the loop
tool_map = {t.name.lower(): t for t in tools}

# Step 5: bind the tools available to the model
llm_client_with_tools = llm_client.bind_tools(tools)

# Step 6: start the loop
# This will follow the process: ai message -> tool call -> tool response -> ai message
# The model will infer when the process is done or if there is extra tools required.
while True:
    # 1. Get the AI response. Messages is the full context list
    ai_message = llm_client_with_tools.invoke(messages)
    print(f"\nAI Response: {ai_message.content}")
    # print(ai_message) # Try looking at the full ai response data

    # 2. Check if there are tool calls in the last ai response
    if not getattr(ai_message, "tool_calls", None):
        # End the flow if the model is done with tool calls
        print("\nNo tool calls detected — conversation finished.")
        break

    print(f"\n************************ Tool calls detected ************************")
    # Add the latest ai message to context list
    messages.append(ai_message)

    # 3. Execute all the tool calls using invoke method and the tool map
    for tool_call in ai_message.tool_calls:
        # Get first the tool name
        tool_name = tool_call["name"].lower()
        selected_tool = tool_map.get(tool_name)

        # Safety
        if not selected_tool:
            print(f"Unknown tool requested: {tool_name}")
            continue

        # Invoke tool if present in the map and get the content
        print(f"\nExecuting tool: {tool_name}")
        tool_msg = selected_tool.invoke(tool_call)
        print(f"Tool result: {tool_msg.content}")
        # print(tool_msg) # Try looking at the full tool response data

        # 4. Append the tool result to the message context list, so the model has the tool response
        messages.append(tool_msg)

    # 5. Go back to the model with latest messages

# Step 6: chech the last AI message from the conversation
print("\n************************ Conversation Ended ************************")
print(f"\nFinal model message:\n{ai_message.content}")