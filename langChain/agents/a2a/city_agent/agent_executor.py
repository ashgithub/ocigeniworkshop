"""
What this file does:
Implements the city agent executor, including structured output generation and
A2A request handling.

In simple terms:
- this file defines the shape of a city recommendation
- this file creates a model that returns structured city data instead of free text
- this file receives A2A requests and sends the structured result back to the caller

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- Agent executor adapted from: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/agent_executor.py
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai
- Structured Output: https://python.langchain.com/docs/how_to/structured_output/

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
This file is not run directly. It is used by `city_server.py`.

Important sections:
- Step 1: Define the structured output schema
- Step 2: Build the city agent and LLM client
- Step 3: Handle agent invocation
- Step 4: Implement the A2A executor wrapper
"""

import os
import sys
from typing import Optional

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
from envyaml import EnvYAML
from pydantic import BaseModel, Field

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from oci_openai_helper import OCIOpenAIHelper


# ============================================================================
# STEP 1: STRUCTURED OUTPUT SCHEMA
# ============================================================================
# Pydantic gives the model a strict schema. This helps beginners see how we can
# ask an LLM for a predictable JSON-like response instead of plain prose.

class CityRecommendation(BaseModel):
    """City recommendation with details."""
    city_name: str = Field(description="Name of the recommended city")
    zipcode: str = Field(description="ZIP code of the recommended city")
    reason: str = Field(description="Reason why this city is recommended")
    population: Optional[int] = Field(default=None, description="Approximate population of the city")
    state: Optional[str] = Field(default=None, description="State or region where the city is located")


# ============================================================================
# STEP 2: STRUCTURED CITY AGENT
# ============================================================================
# This class loads the OCI-compatible model client and wraps it with
# `with_structured_output(...)` so the result follows `CityRecommendation`.

class CityAgent:
    """City Agent using structured output."""

    def __init__(self):
        SANDBOX_CONFIG_FILE = "sandbox.yaml"
        LLM_MODEL = "xai.grok-4-fast-non-reasoning"
        # Alternative models: openai.gpt-4.1, openai.gpt-4o, xai.grok-3
        # Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
        # Note: Structured output is supported by OpenAI and Grok models

        # Step 2.1: Load configuration
        scfg = self.load_config(SANDBOX_CONFIG_FILE)

        # Step 2.2: Create LLM client
        llm_client = OCIOpenAIHelper.get_langchain_openai_client(
            model_name=LLM_MODEL,
            config=scfg
        )

        # Step 2.3: Create structured output model
        self.structured_model = llm_client.with_structured_output(CityRecommendation)

    def load_config(self, config_path: str) -> EnvYAML | None:
        """Load configuration from a YAML file."""
        try:
            return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            return None

    # =========================================================================
    # STEP 3: REQUEST -> STRUCTURED RESPONSE
    # =========================================================================
    # This is the main learning point in this file: we turn a user request into
    # a prompt, ask the model for structured output, and serialize the result.
    async def invoke(self, context: RequestContext) -> str:
        user_input = context.get_user_input()
        print(f"City agent received request: {user_input}")

        # Create prompt for structured output
        prompt = f"""Based on the user's request: "{user_input}"

                    Please provide a thoughtful city recommendation that matches the user's needs.
                """

        try:
            # Get structured output from the model
            response = self.structured_model.invoke(prompt)

            # Ensure response is a CityRecommendation instance
            if isinstance(response, CityRecommendation):
                return response.model_dump_json()
            else:
                # Handle case where response is a dict
                return str(response)

        except Exception as e:
            print(f"Error generating structured output: {e}")
            # Fallback response
            return "I'm sorry, I couldn't generate a city recommendation at this time."


# ============================================================================
# STEP 4: A2A EXECUTOR WRAPPER
# ============================================================================
# The executor is the A2A-facing layer. It creates tasks, emits progress
# updates, and returns the final city recommendation as an A2A artifact.

class CityAgentExecutor(AgentExecutor):
    """City Agent Executor Implementation."""

    def __init__(self):
        self.agent = CityAgent()

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
