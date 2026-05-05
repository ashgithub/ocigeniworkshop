"""
LangGraph-based host agent for the workshop A2A flow.

The host agent discovers remote specialist agents, builds a prompt from their
cards, and delegates work to them through LangChain tools backed by the A2A SDK.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from dotenv import load_dotenv
from envyaml import EnvYAML
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from host_agent import HostAgent
from remote_agent_connections import RemoteAgentConnections

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from oci_openai_helper import OCIOpenAIHelper


def build_langgraph_agent_graph(
    model_with_tools,
    system_prompt: str,
    tools_by_name: dict[str, Any],
):
    """Build a small LangGraph loop that supports async tool execution."""

    def llm_call(state: MessagesState):
        system_instructions = [SystemMessage(system_prompt)]
        response = model_with_tools.invoke(system_instructions + state["messages"])
        return {"messages": [response]}

    async def tool_node(state: MessagesState) -> dict[str, list[ToolMessage]]:
        tool_messages: list[ToolMessage] = []
        for tool_call in state["messages"][-1].tool_calls:  # type: ignore[attr-defined]
            tool = tools_by_name[tool_call["name"]]
            observation = await tool.ainvoke(tool_call["args"])
            tool_messages.append(
                ToolMessage(
                    content=str(observation),
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": tool_messages}

    def should_continue(state: MessagesState) -> str:
        last_message = state["messages"][-1]
        if last_message.tool_calls:  # type: ignore[attr-defined]
            return "tool_node"
        return END

    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("llm_call", llm_call)
    graph_builder.add_node("tool_node", tool_node)
    graph_builder.add_edge(START, "llm_call")
    graph_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    graph_builder.add_edge("tool_node", "llm_call")

    return graph_builder.compile(checkpointer=InMemorySaver())


class MainAgent:
    """LangGraph host agent that coordinates remote A2A specialists."""

    SANDBOX_CONFIG_FILE = "sandbox.yaml"
    LLM_MODEL = "xai.grok-4-fast-reasoning"

    def __init__(self, host_agent: HostAgent) -> None:
        self.host_agent = host_agent
        self.scfg = self._load_config(self.SANDBOX_CONFIG_FILE)
        self.openai_llm_client = OCIOpenAIHelper.get_langchain_openai_client(
            model_name=self.LLM_MODEL,
            config=self.scfg,
            use_responses_api=True,
        )

        self.tools = [self.host_agent.create_call_agent_tool()]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.model_with_tools = self.openai_llm_client.bind_tools(self.tools)
        self.agent = build_langgraph_agent_graph(
            self.model_with_tools,
            self.host_agent.system_prompt(),
            self.tools_by_name,
        )

    def _load_config(self, config_path: str) -> EnvYAML | None:
        try:
            return EnvYAML(config_path)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            return None


async def build_main_agent() -> tuple[MainAgent, RemoteAgentConnections]:
    """Create the remote connection manager and the LangGraph host agent."""
    remote_connections = RemoteAgentConnections()
    host_agent = HostAgent(remote_connections)
    await host_agent.initialize()
    main_agent = MainAgent(host_agent)
    return main_agent, remote_connections


async def main() -> None:
    """Demonstrate the LangGraph host agent delegating to remote A2A agents."""
    main_agent, remote_connections = await build_main_agent()
    prompt = "What types of clothes should I wear on a trip to Oracle headquarters next week?"
    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    try:
        async for chunk in main_agent.agent.astream(
            input={"messages": [HumanMessage(prompt)]},
            config=config,
            stream_mode="values",
        ):
            latest_message = chunk["messages"][-1]

            if latest_message.content:
                if isinstance(latest_message.content, list):
                    try:
                        print(latest_message.content[0]["text"])
                    except (KeyError, IndexError, TypeError):
                        print(latest_message.content)
                else:
                    print(latest_message.content)
            elif latest_message.tool_calls:
                print(
                    "Calling tools:",
                    [tool_call["name"] for tool_call in latest_message.tool_calls],
                )
    finally:
        await remote_connections.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
