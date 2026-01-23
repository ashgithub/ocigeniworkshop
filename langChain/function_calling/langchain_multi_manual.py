"""
What this file does:
Demonstrates manual multi-step function calling with custom tools using OCI Generative AI for LLM.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- LangChain: https://docs.langchain.com/oss/python/langchain/agents
- How to build tools: https://python.langchain.com/docs/how_to/custom_tools/
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai  note: supports OpenAI, XAI & Meta models. Also supports OpenAI Responses API 
- OCI langchain SDK: https://github.com/oracle-devrel/langchain-oci-genai  note: as of Nov 2025 it is not compatible with langchain v1.0. supports all OCI models including Cohere
- OCI GenAI SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI 
 - #igiu-innovation-lab: general discussions on your project 
 - #igiu-ai-learning: help with sandbox environment or help with running this code 

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/function_calling/langchain_multi_manual.py

Comments to important sections of file:
- Step 1: Load the config file 
- Step 2: create the OpenAI LLM client using credentials and optional parameters
- Step 3: Add some messages to the context list
- Step 4: map the tools for easier invokation over the loop
- Step 5: bind the tools available to the model
- Step 6: start the loop
"""

import sys, os
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

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

LLM_MODEL = "openai.gpt-4.1"

# Try experimenting with different models to see how they handle multi-step reasoning. Try different LLM families as well as reasoning and non reasoning models
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# openai.gpt-4.1
# openai.gpt-4o
# xai.grok-4
# xai.grok-3

# define tools
@tool
def get_weather(city: str) -> str:
    """ Gets the weather for a given city """
    return f"The weather in {city} is 70 Fahrenheit"

@tool
def get_projection_bill(current_weather: int, gas_oven: bool) -> int:
    """ Returns the projected bill for a user depending on the current one and if it has or not oven """
    if gas_oven:
        return (current_weather*2) + 45
    return (current_weather*2) + 4

tools = [get_weather, get_projection_bill]

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
llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg, use_responses_api=True
)

# Step 3: Add some messages to the context list
# meta-llama models are eager to have errors when handling multiple or parallel tool calls, try making one request per time
messages = [HumanMessage("Which will be my projected bill? I'm in San Francisco, and I have oven. My past bill was $45")]

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

# Step 6: check the last AI message from the conversation
print("\n************************ Conversation Ended ************************")
print(f"\nFinal model message:\n{ai_message.content}")
