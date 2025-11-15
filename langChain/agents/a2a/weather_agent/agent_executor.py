"""
What this file does:
Implements the agent executor for the weather agent, handling A2A requests and executing weather information logic.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai  note: supports OpenAI, XAI & Meta models. Also supports OpenAI Responses API

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
This file is not run directly, but used by weather_server.py

Comments to important sections of file:
- Step 1: Define agent tool
- Step 2: Implement WeatherAgent class with config and LLM setup
- Step 3: Define invoke method for agent execution
- Step 4: Implement WeatherAgentExecutor with execute and cancel methods
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
def get_weather(zipcode: int, date: str) -> dict[str, bool | int]:
    """ Gets the weather for a given city zipcode and date in format yyyy-mm-dd """
    # This is simple hardcoded data, could use zip code to fetch weather API and get real results
    
    print(f"tool invoked with {zipcode} {date} ")
    rain = random.choice([True, False])
    min_temperature = random.randint(40, 60)
    max_temperature = random.randint(min_temperature + 10, min_temperature + 20)
    city_weather = {
        "rain": rain,
        "min_temperature": f"{min_temperature} f",
        "max_temperature": f"{max_temperature} f"
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
        self.model = OCIOpenAIHelper.get_client(
            model_name=LLM_MODEL,
            config=scfg
        )

        # Step 2.3: Create agent with tools
        self.agent = create_agent(
            model=self.model,
            tools=[get_weather],
            system_prompt="Answer only details about weather, provide max temperature, min temperature and rain"
        )

    def load_config(self, config_path):
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
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
