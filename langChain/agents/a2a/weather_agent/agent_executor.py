"""
What this file does:
Implements the weather agent executor, including tool-backed weather lookups and
A2A request handling.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
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
This file is not run directly. It is used by `weather_server.py`.

Important sections:
- Step 1: Define the weather tool
- Step 2: Build the weather agent and LLM client
- Step 3: Handle agent invocation
- Step 4: Implement the A2A executor wrapper
"""

import sys
import os
import random

from envyaml import EnvYAML
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.messages import HumanMessage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from oci_openai_helper import OCIOpenAIHelper

load_dotenv()

# Step 1: Define agent tool
@tool
def get_weather(zipcode: int, date: str) -> dict[str, object]:
    """Return sample weather data for a zipcode and date in yyyy-mm-dd format."""

    rain = random.choice([True, False])
    min_temperature = random.randint(40, 60)
    max_temperature = random.randint(min_temperature + 10, min_temperature + 20)
    city_weather = {
        "rain": rain,
        "min_temperature": f"{min_temperature} F",
        "max_temperature": f"{max_temperature} F",
    }
    return city_weather

# Step 2: Implement WeatherAgent class with config and LLM setup
class WeatherAgent:
    """Weather Agent."""
    def __init__(self):
        SANDBOX_CONFIG_FILE = "sandbox.yaml"
        LLM_MODEL = "xai.grok-4-fast-non-reasoning" # try changing to a reasoning model
        # Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

        # Step 2.1: Load configuration
        scfg = self.load_config(SANDBOX_CONFIG_FILE)

        # Step 2.2: Create LLM client
        self.model = OCIOpenAIHelper.get_langchain_openai_client(
            model_name=LLM_MODEL,
            config=scfg
        )

        # Step 2.3: Create agent with tools
        self.agent = create_agent(
            model=self.model,
            tools=[get_weather],
            system_prompt="Answer only details about weather, provide max temperature, min temperature and rain"
        )

    def load_config(self, config_path: str) -> EnvYAML | None:
        """Load configuration from a YAML file."""
        try:
            return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            return None

    # Step 3: Define invoke method for agent execution
    async def invoke(self, context: RequestContext) -> str:
        user_input = context.get_user_input()
        print(user_input)

        response = self.agent.invoke(
            input={"messages": [HumanMessage(str(user_input))]}
        )

        print(response)
        final_response = response['messages'][-1].content
        return str(final_response)

# Step 4: Implement WeatherAgentExecutor with execute and cancel methods
class WeatherAgentExecutor(AgentExecutor):
    """Weather Agent Executor Implementation."""

    def __init__(self):
        self.agent = WeatherAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke(context)
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
