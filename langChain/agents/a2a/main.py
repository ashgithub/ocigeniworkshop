from langchain_core.tools import tool
from remote_agent_connections import call_a2a_agent

import sys
import os

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import SystemMessage,ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv
from envyaml import EnvYAML
from typing import Any
load_dotenv()

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
    SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/ocigeniworkshop/sandbox.yaml"

    LLM_MODEL = "xai.grok-4"
    # available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

    def __init__(self):
        self.scfg = self.load_config(self.SANDBOX_CONFIG_FILE)

        self.openai_llm_client = OCIOpenAIHelper.get_client(
            model_name=self.LLM_MODEL,
            config=self.scfg,
            use_responses_api=True
        )

        self.tools = [sent_task_agent]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.model_with_tools = self.openai_llm_client.bind_tools(self.tools)

        self.agent = self.build_langgraph_agent()

    def build_langgraph_agent(self):
        """ This function builds a langgraph agent in order to make async calls with the openai client """
        system_prompt=""" 
        Use the provided tools to gather context when necessary.
        Always provide sufficient context to call the agents.
        Use the correct names as the tools> weather_agent, clothes_agent or city_agent
        Each tool call will only call one agent specified, to call multiple agents, use multiple tool calls with different agent names
        """
        
        def llm_call(state: MessagesState):
            """LLM decides whether to call a tool or not"""
            system_instructions = [SystemMessage(system_prompt)]
            return {"messages": [self.model_with_tools.invoke( system_instructions + state["messages"])]}

        async def tool_node(state:MessagesState) -> dict[Any,Any]:
            """Performs the tool call"""
            result = []
            for tool_call in state["messages"][-1].tool_calls: # type: ignore[attr-defined]
                tool = self.tools_by_name[tool_call["name"]]
                observation = await tool.ainvoke(tool_call["args"])
                result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
            return {"messages": result}

        def should_continue(state: MessagesState) -> str:
            """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.tool_calls: # type: ignore[attr-defined]
                return "tool_node"
            return END

        agent_builder = StateGraph(MessagesState)
        agent_builder.add_node("llm_call", llm_call)
        agent_builder.add_node("tool_node", tool_node)
        agent_builder.add_edge(START, "llm_call")
        agent_builder.add_conditional_edges("llm_call",should_continue,["tool_node", END])
        agent_builder.add_edge("tool_node", "llm_call")
        agent = agent_builder.compile(checkpointer=InMemorySaver())

        return agent

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

    prompt = "What types of clothes should I wear on a trip to Oracle headquarters next week?"
    config: RunnableConfig = {"configurable": {"thread_id": "1"}} # thread for the agent memory

    async for chunk in main_agent.agent.astream(
        input={"messages": [HumanMessage(prompt)]},
        config=config,
        stream_mode="values",
    ):
        # Messages are added to the agent state, that is why we access the last message
        latest_message = chunk["messages"][-1]
        print("Agentic response from graph")
        if latest_message.content:
            try:
                print(latest_message.content[0]['text'])
            except:
                print(latest_message.content)
        elif latest_message.tool_calls:
            # Check any tool calls
            print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())