import sys
import os

from envyaml import EnvYAML
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

# --8<-- [start:HelloWorldAgent]
class HelloWorldAgent:
    """Hello World Agent."""
    def __init__(self):
        SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/sandbox.yaml"
        load_dotenv()

        LLM_MODEL = "xai.grok-4"
        # LLM_MODEL = "openai.gpt-4.1"
        # LLM_MODEL = "openai.gpt-5"
        # xai.grok-4
        # xai.grok-3
        # available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
        scfg = self.load_config(SANDBOX_CONFIG_FILE)
        self.agent = OCIOpenAIHelper.get_client(
            model_name=LLM_MODEL,
            config=scfg
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
        # message = context.message
        # message_context = context.call_context
        # print(message.parts)
        # print(message_context)
        user_input = context.get_user_input()
        # response = self.agent.invoke(user_input)
        return f"Hello, yout request was: {user_input}"

# --8<-- [end:HelloWorldAgent]

# --8<-- [start:HelloWorldAgentExecutor_init]
class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    # --8<-- [end:HelloWorldAgentExecutor_init]
    # --8<-- [start:HelloWorldAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke(context)
        await event_queue.enqueue_event(new_agent_text_message(result))

    # --8<-- [end:HelloWorldAgentExecutor_execute]

    # --8<-- [start:HelloWorldAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:HelloWorldAgentExecutor_cancel]