"""
What this file does:
Builds the main LangGraph host agent for the A2A workshop.

In simple terms:
- this file creates the host model
- this file gives the model access to a tool that can call remote agents
- this file builds the LangGraph loop that alternates between model thinking
  and tool execution
- this file contains a small demo `main()` function

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai
- LangGraph: https://langchain-ai.github.io/langgraph/
- Host agent sample adapted from: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/hosts/multiagent/host_agent.py

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/a2a/langgraph_a2a_agent.py

Important sections:
- Step 1: Load dependencies and environment variables
- Step 2: Build the LangGraph workflow
- Step 3: Initialize the main host agent and model
- Step 4: Create the host agent plus remote connections
- Step 5: Run a demo request through the graph
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


# ============================================================================
# STEP 2: LANGGRAPH WORKFLOW
# ============================================================================
# LangGraph lets us express the host agent as a loop:
# 1. the model reads the conversation
# 2. if needed, it asks to use a tool
# 3. the tool result is added back to the conversation
# 4. the model continues until it can answer

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


# ============================================================================
# STEP 3: MAIN HOST AGENT CLASS
# ============================================================================
# This class wires together the OCI model, the host-side prompt, and the
# LangChain tool that delegates work to remote A2A agents.

class MainAgent:
    """LangGraph host agent that coordinates remote A2A specialists."""

    SANDBOX_CONFIG_FILE = "sandbox.yaml"
    LLM_MODEL = "xai.grok-4-fast-reasoning"

    def __init__(self, host_agent: HostAgent) -> None:
        self.host_agent = host_agent
        self.scfg = self._load_config(self.SANDBOX_CONFIG_FILE)
        print(f"Main host agent is loading model '{self.LLM_MODEL}'.")
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


# ============================================================================
# STEP 4: FACTORY FOR THE FULL HOST AGENT
# ============================================================================
# This helper creates both parts needed by the demo:
# - the remote connection manager
# - the LangGraph host agent that uses it

async def build_main_agent() -> tuple[MainAgent, RemoteAgentConnections]:
    """Create the remote connection manager and the LangGraph host agent."""
    remote_connections = RemoteAgentConnections()
    host_agent = HostAgent(remote_connections)
    await host_agent.initialize()
    main_agent = MainAgent(host_agent)
    return main_agent, remote_connections


# ============================================================================
# STEP 5: DEMO ENTRY POINT
# ============================================================================
# This is a small runnable example that shows the full host flow for learners.

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
