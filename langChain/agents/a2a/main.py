from langchain.agents import create_agent
from langchain_core.tools import tool
from remote_agent_connections import call_a2a_agent

import sys
import os

from langchain_core.tools import tool
from langchain.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oci_openai_helper import OCIOpenAIHelper

@tool
async def sent_task_agent(agent_name:str,full_context:str)->str:
    """ Sends a task to an agent expert in gathering the information requested
    Agents available: weather_agent, clothes_agent, city_agent
    """
    # Method that uses a2a to reach the agent, available in remote_agent_connections.py
    response = await call_a2a_agent(agent_name,full_context)
    return response

class MainAgent:
    #####
    #make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
    #
    #
    #  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
    #  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
    #  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
    #  if you have errors running sample code reach out for help in #igiu-ai-learning
    #####
    SANDBOX_CONFIG_FILE = "sandbox.yaml"

    LLM_MODEL = "xai.grok-4"
    # LLM_MODEL = "openai.gpt-4.1"
    # LLM_MODEL = "openai.gpt-5"
    # xai.grok-4
    # xai.grok-3
    # available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

    def __init__(self):
        self.scfg = self.load_config(self.SANDBOX_CONFIG_FILE)

        self.openai_llm_client = OCIOpenAIHelper.get_client(
            model_name=self.LLM_MODEL,
            config=self.scfg,
            use_responses_api=True
        )

        self.tools = [
            sent_task_agent
        ]

        self.agent = create_agent(
            model=self.openai_llm_client,
            tools=self.tools,
            system_prompt=""" 
        Use the provided tools to gather context when necessary.
        Always provide sufficient context to call the agents.
        Use the correct names as the tools> weather_agent, clothes_agent or city_agent
        Each tool call will only call one agent specified, to call multiple agents, use multiple tool calls with different agent names
        """
        )

    def load_config(self, config_path):
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
                return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            return None

async def main():
    print(f"************************** Agent stream invokation and details for each step **************************")

    main_agent = MainAgent()

    MESSAGE = "What types of clothes should I wear on a trip to Oracle headquarters next week?"

    async for chunk in main_agent.agent.astream(
        input={"messages": [HumanMessage(MESSAGE)]},
        stream_mode="values",
    ):
        # Messages are added to the agent state, that is why we access the last message
        latest_message = chunk["messages"][-1]
        if latest_message.content:
            print(f"Agent: {latest_message.content}")
        elif latest_message.tool_calls:
            # Check any tool calls
            print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())