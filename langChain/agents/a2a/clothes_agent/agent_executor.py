"""
What this file does:
Implements the clothes agent executor, including tool-backed clothing
recommendations and A2A request handling.

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
This file is not run directly. It is used by `clothes_server.py`.

Important sections:
- Step 1: Define the clothing recommendation tool
- Step 2: Build the clothes agent and LLM client
- Step 3: Handle agent invocation
- Step 4: Implement the A2A executor wrapper
"""

import sys
import os

from envyaml import EnvYAML
from a2a.helpers import (
    new_task_from_user_message,
    new_text_artifact,
    new_text_message,
)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types.a2a_pb2 import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from dotenv import load_dotenv
load_dotenv()
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.messages import HumanMessage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from oci_openai_helper import OCIOpenAIHelper

# Step 1: Define agent tool
@tool
def get_clothes(gender: str, temp: int, rain: bool) -> dict[str, list[str]]:
    """Suggest clothing and accessories based on temperature, rain, and user preference."""
    # Hardcoded data, could use any other user details
    clothes = []
    accessories = []

    # Base recommendations on temperature
    if temp < 50:
        clothes.extend(["heavy coat", "sweater", "jeans", "boots"])
        accessories.extend(["scarf", "gloves"])
    elif temp < 70:
        clothes.extend(["jacket", "long-sleeve shirt", "pants"])
        accessories.extend(["watch"])
    else:
        clothes.extend(["t-shirt", "shorts", "sneakers"])
        accessories.extend(["sunglasses"])

    # Adjust for rain
    if rain:
        clothes.append("rain coat")
        accessories.extend(["umbrella", "rain boots"])

    # Adjust for user preference (simplified demo logic)
    if gender.lower() == "male":
        clothes.extend(["polo shirt"])
    elif gender.lower() == "female":
        clothes.extend(["dress", "blouse"])
    else:
        clothes.extend(["casual shirt"])

    return {
        "clothes": clothes,
        "accessories": accessories
    }

# Step 2: Implement ClothesAgent class with config and LLM setup
class ClothesAgent:
    """Clothes Agent."""
    def __init__(self):
        SANDBOX_CONFIG_FILE = "sandbox.yaml"
        LLM_MODEL = "xai.grok-4-fast-non-reasoning"
        # Alternative models: openai.gpt-4.1, openai.gpt-4o, xai.grok-3
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
            tools=[get_clothes],
            system_prompt="Answer only details about clothes, provide the clothes and suitable accessories"
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

# Step 4: Implement ClothesAgentExecutor with execute and cancel methods
class ClothesAgentExecutor(AgentExecutor):
    """Clothes Agent Executor Implementation."""

    def __init__(self):
        self.agent = ClothesAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        message = context.message
        if context.current_task is not None:
            task = context.current_task
        elif message is not None:
            task = new_task_from_user_message(message)
        else:
            raise ValueError('RequestContext.message is required to create a new task')

        await event_queue.enqueue_event(task)

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                status=TaskStatus(
                    state=TaskState.TASK_STATE_WORKING,
                    message=new_text_message('Processing request...'),
                ),
            )
        )

        result = await self.agent.invoke(context)

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                artifact=new_text_artifact(name='result', text=result),
            )
        )
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
