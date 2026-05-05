"""
LangChain/LangGraph-friendly host-agent helpers for A2A orchestration.

This module keeps the useful discovery and delegation ideas from the previous
host-agent refactor, but removes the Google ADK dependency so the orchestration
can stay inside the LangChain/LangGraph stack used by the workshop.
"""

from __future__ import annotations

from typing import Annotated

from a2a.types.a2a_pb2 import AgentCard
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool

from remote_agent_connections import RemoteAgentConnections


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

    def system_prompt(self) -> str:
        """Return the current prompt with discovered remote agents."""
        return build_system_prompt(self.cards)
