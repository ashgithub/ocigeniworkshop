"""
What this file does:
Demonstrates how to create a LangChain agent with custom tools for city,
weather, and clothing recommendations.

Documentation to reference:
- LangChain Agents: https://docs.langchain.com/oss/python/langchain/agents
- LangChain Tools: https://docs.langchain.com/oss/python/langchain/tools
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/langchain_agent.py

Important sections:
- Step 1: Load configuration
- Step 2: Create the OCI-backed LangChain chat client
- Step 3: Define the tools exposed to the agent
- Step 4: Create and run the agent
"""

import os
import sys
from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.messages import HumanMessage
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-fast-non-reasoning"
# LLM_MODEL = "openai.gpt-4.1"
# LLM_MODEL = "openai.gpt-5"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm


# Step 1: Load configuration
def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


scfg = load_config(SANDBOX_CONFIG_FILE)


# Step 2: Create the OCI-backed LangChain client
openai_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg,
)


# Step 3: Define tools for the agent
# How to build tools: https://docs.langchain.com/oss/python/langchain/tools
@tool
def get_weather(zipcode: int, date: str) -> dict[str, Any]:
    """Return sample weather data for a zipcode and date in yyyy-mm-dd format."""

    city_weather = {
        "rain": True,
        "min_temperature": "50 F",
        "max_temperature": "62 F",
    }
    return city_weather


@tool
def get_city(criteria: str) -> dict[str, Any]:
    """Recommend a city based on the supplied criteria."""

    city_details = {
        "city_name": "Chicago",
        "zipcode": 60601,
    }
    return city_details


@tool
def get_clothes(gender: str, temp: int, rain: bool) -> dict[str, list[str]]:
    """Suggest clothing and accessories based on conditions supplied by the agent."""

    clothes = {
        "clothes": ["rain coat", "jeans", "formal shirt"],
        "accessories": ["watch", "umbrella", "boots"],
    }
    return clothes


tools = [get_weather, get_city, get_clothes]


# Step 4: Create and run the agent
agent = create_agent(
    model=openai_llm_client,
    tools=tools,
    system_prompt="Answer questions by using the provided tools. Some queries may require multiple tool calls. DO not assume any thing. only use the tools. I am a 50 yr old guy",
)
print("************************** Agent ready **************************")

MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

print("************************** Agent stream invocation and step details **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]},
    stream_mode="values",
):
    # last message as the final answer
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")


print("************************** Agent single-step invoke **************************")
result = agent.invoke(input={"messages": [HumanMessage(MESSAGE)]})
print(result["messages"][-1].content)

print("************************** Agent full response state **************************")
for message in result["messages"]:
    print("Agent step message:")
    print(message)
