"""
What this file does:
Demonstrates Langfuse integration with a LangChain agent for tracing and
monitoring tool-calling workflows.

Documentation to reference:
- Langfuse: https://langfuse.com/integrations/frameworks/langchain
- LangChain Agents: https://docs.langchain.com/oss/python/langchain/agents
- LangChain Tools: https://docs.langchain.com/oss/python/langchain/tools
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and Langfuse settings.
- .env: Loads environment variables if required.

Note: sign up at langfuse to get the langfuse keys. TRAINING ONLY. Use Oracle hosted instance for any official work 

How to run the file:
uv run langChain/agents/langfuse_agent.py

Important sections:
- Step 1: Load configuration and initialize Langfuse
- Step 2: Define tools and create the agent
- Step 3: Add Langfuse callback configuration
- Step 4: Run the agent with tracing enabled
"""

import datetime
import os
import sys
from typing import Any

from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
from envyaml import EnvYAML
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-fast-non-reasoning"
# LLM_MODEL = "openai.gpt-4.1"
# LLM_MODEL = "openai.gpt-5"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm


def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 1: Initialize Langfuse from the loaded configuration
langfuse = Langfuse(
    public_key=scfg["langfuse"]["langfuse_pk"],
    secret_key=scfg["langfuse"]["langfuse_sk"],
    host=scfg["langfuse"]["langfuse_host"],
)
langfuse_handler = CallbackHandler()


# Step 2: Create the model client and define tools
openai_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg,
)


@tool
def get_weather(zipcode: int, date: str) -> dict[str, Any]:
    """Return sample weather data for a zipcode and date in yyyy-mm-dd format."""

    return {
        "rain": True,
        "min_temperature": "50 F",
        "max_temperature": "62 F",
    }


@tool
def get_city(criteria: str) -> dict[str, Any]:
    """Recommend a city based on the supplied criteria."""

    return {
        "city_name": "Chicago",
        "zipcode": 60601,
    }


@tool
def get_clothes(gender: str, temp: int, rain: bool) -> dict[str, list[str]]:
    """Suggest clothing and accessories based on the provided conditions."""

    return {
        "clothes": ["rain coat", "jeans", "formal shirt"],
        "accessories": ["watch", "umbrella", "boots"],
    }


tools = [get_weather, get_city, get_clothes]


agent = create_agent(
    model=openai_llm_client,
    tools=tools,
    system_prompt="Use the tools when helpful and answer as a helpful assistant.",
    name="sample_workshop_agent",
)
print("************************** Agent ready **************************")


# Step 3: Add Langfuse callback and metadata configuration
config: RunnableConfig = {
    "callbacks": [langfuse_handler],
    "metadata": {
        "langfuse_user_id": os.getenv("MY_PREFIX", "default_user"),
        "langfuse_session_id": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"),
        "langfuse_tags": ["workshop", os.getenv("MY_PREFIX", "user-name")],
    },
}

MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"


# Step 4: Stream the agent response with tracing enabled
print("************************** Agent stream invocation and step details **************************")
for chunk in agent.stream(
    input={"messages": [HumanMessage(MESSAGE)]},
    stream_mode="values",
    config=config,
):
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
