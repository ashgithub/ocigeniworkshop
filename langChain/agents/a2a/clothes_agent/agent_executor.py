""" Agent executor is in charge of receiving the request and call the agent as needed """
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

# Sample remote agent tool
@tool
def get_clothes(gender:str, temp:int, rain:bool) -> dict[str,list[str]]:
    """ Tool to suggest best clothes depending on the city weather, temperature and genders """

    # Hardcoded data, could use any other user details
    clothes = {
        "clothes": ["ran coat", "jeans", "formal chemise"],
        "accessories": ["watch","umbrella", "boots"]
    }

    return clothes

# --8<-- [start:ClothesAgent]
# This is the remote agent, built as any other normal agent
class ClothesAgent:
    """Clothes Agent."""
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
            tools=[get_clothes],
            system_prompt="Answer only details about clothes, provide the clothes and suitable accessories"
        )

    def load_config(self, config_path):
            """Load configuration from a YAML file."""
            try:
                with open(config_path, 'r') as f:
                    return EnvYAML(config_path)
            except FileNotFoundError:
                print(f"Error: Configuration file '{config_path}' not found.")
                return None

    # Helper invokation method to call the agent
    async def invoke(self,context:RequestContext) -> str:
        user_input = context.get_user_input()
        print(user_input)
        
        # Actual agent call using langchain agent
        response = self.agent.invoke(
            input={"messages":[HumanMessage(str(user_input))]}
        )

        print(response)

        final_response = response['messages'][-1].content

        return str(final_response)

# --8<-- [end:ClothesAgent]

# --8<-- [start:ClothesAgentExecutor_init]
# Agent executor to manage requests
class ClothesAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = ClothesAgent()

    # --8<-- [end:ClothesAgentExecutor_init]
    # --8<-- [start:ClothesAgentExecutor_execute]
    # Execution function that uses the agent class to perform the model call
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke(context)
        await event_queue.enqueue_event(new_agent_text_message(result))

    # --8<-- [end:ClothesAgentExecutor_execute]

    # --8<-- [start:ClothesAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:ClothesAgentExecutor_cancel]