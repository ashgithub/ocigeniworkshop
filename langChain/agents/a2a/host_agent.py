"""
What this file does:
Helps the main LangGraph host agent understand which remote A2A agents exist
and how to call them.

In simple terms:
- this file turns discovered agent cards into readable text for the host prompt
- this file creates the `call_agent` tool used by the host agent
- this file connects LangGraph thread state to remote A2A task state

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/
- Host tutorial: https://a2a-protocol.org/latest/tutorials/#python
- Tutorial code: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/hosts/multiagent/host_agent.py
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
This file is not run directly. It is imported by `langgraph_a2a_agent.py`.

Important sections:
- Step 1: Build short descriptions for discovered remote agents
- Step 2: Build the system prompt used by the host agent
- Step 3: Initialize the host-side helper class
- Step 4: Create the LangChain tool that sends work to remote agents
- Step 5: Return the final prompt shown to the model
"""

from __future__ import annotations

from typing import Annotated

from a2a.types.a2a_pb2 import AgentCard
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool

from remote_agent_connections import RemoteAgentConnections


# ============================================================================
# STEP 1: AGENT CARD -> PROMPT TEXT
# ============================================================================
# These helpers convert low-level A2A agent metadata into text that a beginner
# can read and that the host model can use when deciding which specialist to call.

def build_agent_description(card: AgentCard) -> str:
    """Render one remote agent card into concise prompt text."""
    lines = [f"- {card.name}: {card.description or 'No description available'}"]

    if card.skills:
        for skill in card.skills:
            lines.append(
                f"  Skill {skill.name}: {skill.description or 'No description'}"
            )
            if skill.tags:
                lines.append(f"  Tags: {', '.join(skill.tags)}")
            if skill.examples:
                lines.append(f"  Examples: {', '.join(skill.examples[:3])}")

    return "\n".join(lines)


# ============================================================================
# STEP 2: SYSTEM PROMPT BUILDER
# ============================================================================
# The host agent needs a single prompt that lists the available specialists and
# explains when it should delegate work.

def build_system_prompt(cards: list[AgentCard]) -> str:
    """Create the orchestrator prompt from discovered agent cards."""
    if not cards:
        agent_block = "No remote agents are currently available."
    else:
        agent_block = "\n".join(build_agent_description(card) for card in cards)

    return f"""You are a helpful host agent with access to specialized A2A agents.

Available agents:
{agent_block}

Instructions:
- Use the `call_agent` tool when a remote specialist can answer or perform part of the task.
- Choose the agent whose description, skills, tags, or examples best match the request.
- You may call more than one agent when the user needs a combined answer.
- Provide each remote agent enough context to do its part well.
- Use the exact remote agent name shown above.
- If no remote agent is appropriate, answer directly.
"""


# ============================================================================
# STEP 3: HOST-SIDE ORCHESTRATION HELPER
# ============================================================================
# This class is intentionally small. It stores discovered cards, prepares the
# host prompt, and exposes one tool that LangGraph can call.

class HostAgent:
    """Thin orchestration wrapper used by the LangGraph host agent."""

    def __init__(self, remote_connections: RemoteAgentConnections) -> None:
        self.remote_connections = remote_connections
        self.cards: list[AgentCard] = []

    async def initialize(self, force_refresh: bool = False) -> None:
        """Load remote agent cards before building tools and prompts."""
        self.cards = await self.remote_connections.discover_agents(
            force_refresh=force_refresh
        )
        print(f"Host agent loaded {len(self.cards)} remote agent card(s).")

    # =========================================================================
    # STEP 4: TOOL CREATION
    # =========================================================================
    # The LangGraph host does not call remote agents directly. Instead, the
    # model chooses this tool, and the tool forwards the work through the
    # shared A2A connection manager.
    def create_call_agent_tool(self):
        """Expose remote A2A calls as a LangChain tool."""

        @tool
        async def call_agent(
            agent_name: str,
            query: str,
            config: Annotated[RunnableConfig, InjectedToolArg],
        ) -> str:
            """Call a remote A2A agent with the provided query."""
            thread_id = str(config.get("configurable", {}).get("thread_id", "default"))
            return await self.remote_connections.call_agent(
                agent_name,
                query,
                thread_id=thread_id,
            )

        return call_agent

    # =========================================================================
    # STEP 5: FINAL HOST PROMPT
    # =========================================================================
    # This returns the text that the model sees before the conversation starts.
    def system_prompt(self) -> str:
        """Return the current prompt with discovered remote agents."""
        return build_system_prompt(self.cards)
