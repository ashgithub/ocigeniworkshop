import sys
import os

from envyaml import EnvYAML
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from dotenv import load_dotenv
load_dotenv()
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.messages import HumanMessage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from oci_openai_helper import OCIOpenAIHelper

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


# --8<-- [start:WeatherAgent]
class WeatherAgent:
    """Weather Agent."""
    def __init__(self):
        SANDBOX_CONFIG_FILE = "sandbox.yaml"

        LLM_MODEL = "xai.grok-4"
        # LLM_MODEL = "openai.gpt-4.1"
        # LLM_MODEL = "openai.gpt-5"
        # xai.grok-4
        # xai.grok-3
        # available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
        
        scfg = self.load_config(SANDBOX_CONFIG_FILE)
        self.model = OCIOpenAIHelper.get_client(
            model_name=LLM_MODEL,
            config=scfg
        )
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

    async def invoke(self,context:RequestContext) -> str:
        user_input = context.get_user_input()


        response = self.agent.invoke(
            input={"messages":[HumanMessage(str(user_input))]}
        )

        final_response = response['messages'][-1].content

        return str(final_response)

# --8<-- [end:WeatherAgent]

# --8<-- [start:WeatherAgentExecutor_init]
class WeatherAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = WeatherAgent()

    # --8<-- [end:WeatherAgentExecutor_init]
    # --8<-- [start:WeatherAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke(context)
        await event_queue.enqueue_event(new_agent_text_message(result))

    # --8<-- [end:WeatherAgentExecutor_execute]

    # --8<-- [start:WeatherAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:WeatherAgentExecutor_cancel]