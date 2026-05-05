"""
What this file does:
Provides A2A discovery and connection management for the LangGraph host agent.
It supports direct agent-card resolution from agent URLs, cached clients, and
remote task continuation across calls.

How to use this file:
- Import `RemoteAgentConnections` from `langgraph_a2a_agent.py` or
  `host_agent.py`.
- By default it discovers the workshop agents from their known local URLs.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable

import httpx
from a2a.client import A2ACardResolver, Client, ClientConfig, ClientFactory
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types.a2a_pb2 import (
    AgentCard,
    Role,
    SendMessageRequest,
    StreamResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from a2a.utils.constants import TransportProtocol


GLOBAL_TIMEOUT = httpx.Timeout(
    timeout=30.0,
    connect=5.0,
    read=25.0,
    write=5.0,
)

DEFAULT_REMOTE_AGENT_URLS = (
    "http://localhost:9997",
    "http://localhost:9998",
    "http://localhost:9999",
)
TERMINAL_TASK_STATES = {
    TaskState.TASK_STATE_COMPLETED,
    TaskState.TASK_STATE_FAILED,
    TaskState.TASK_STATE_CANCELED,
    TaskState.TASK_STATE_REJECTED,
    TaskState.TASK_STATE_INPUT_REQUIRED,
    TaskState.TASK_STATE_AUTH_REQUIRED,
}


@dataclass
class RemoteTaskSession:
    """Tracks the remote task identifiers for a host conversation."""

    task_id: str | None = None
    context_id: str | None = None


class RemoteAgentConnections:
    """Discover remote agents and send A2A requests to them."""

    def __init__(
        self,
        remote_agent_urls: Iterable[str] | None = None,
    ) -> None:
        self.remote_agent_urls = list(
            remote_agent_urls or DEFAULT_REMOTE_AGENT_URLS
        )
        self._httpx_client = httpx.AsyncClient(timeout=GLOBAL_TIMEOUT)
        self._client_factory = ClientFactory(
            ClientConfig(
                httpx_client=self._httpx_client,
                supported_protocol_bindings=[
                    TransportProtocol.JSONRPC,
                    TransportProtocol.HTTP_JSON,
                ],
            )
        )
        self._agent_cards: dict[str, AgentCard] = {}
        self._client_cache: dict[str, Client] = {}
        self._task_sessions: dict[tuple[str, str], RemoteTaskSession] = {}

    async def discover_agents(self, force_refresh: bool = False) -> list[AgentCard]:
        """Discover remote agents from direct URLs."""
        if self._agent_cards and not force_refresh:
            return list(self._agent_cards.values())

        discovered_cards: dict[str, AgentCard] = {}

        for card in await self._discover_from_urls():
            discovered_cards[card.name] = card

        self._agent_cards = discovered_cards
        return list(self._agent_cards.values())

    async def list_agent_summaries(self) -> list[dict[str, str]]:
        """Return lightweight agent metadata for prompting and diagnostics."""
        cards = await self.discover_agents()
        return [
            {
                "name": card.name,
                "description": card.description,
            }
            for card in cards
        ]

    async def call_agent(
        self,
        agent_name: str,
        message: str,
        *,
        thread_id: str = "default",
    ) -> str:
        """Send a text request to a remote agent and return consolidated text."""
        await self.discover_agents()

        if agent_name not in self._agent_cards:
            available = ", ".join(sorted(self._agent_cards))
            return (
                f"Agent '{agent_name}' is not available. "
                f"Available agents: {available or 'none'}"
            )

        client = self._client_cache.get(agent_name)
        if client is None:
            client = self._client_factory.create(self._agent_cards[agent_name])
            self._client_cache[agent_name] = client

        session_key = (thread_id, agent_name)
        session = self._task_sessions.setdefault(session_key, RemoteTaskSession())
        request = SendMessageRequest(
            message=new_text_message(
                text=message,
                task_id=session.task_id,
                context_id=session.context_id,
                role=Role.ROLE_USER,
            )
        )

        try:
            response_text = await self._consume_response_stream(
                client,
                request,
                session,
            )
        except Exception as exc:
            self._client_cache.pop(agent_name, None)
            return f"Error calling {agent_name}: {exc}"

        return response_text or "No response received"

    async def close(self) -> None:
        """Release network resources owned by the connection manager."""
        for client in self._client_cache.values():
            await client.close()
        self._client_cache.clear()
        await self._httpx_client.aclose()

    async def _discover_from_urls(self) -> list[AgentCard]:
        """Resolve agent cards directly from known agent base URLs."""
        cards: list[AgentCard] = []
        for url in self.remote_agent_urls:
            try:
                resolver = A2ACardResolver(self._httpx_client, url)
                card = await resolver.get_agent_card()
            except Exception:
                continue
            cards.append(card)
        return cards

    async def _consume_response_stream(
        self,
        client: Client,
        request: SendMessageRequest,
        session: RemoteTaskSession,
    ) -> str:
        """Aggregate text from A2A stream responses and track task IDs."""
        text_chunks: OrderedDict[str, None] = OrderedDict()

        async for response in client.send_message(request):
            self._update_session_from_response(response, session)

            chunk = self._extract_text(response)
            if chunk:
                text_chunks[chunk] = None

        return "\n".join(text_chunks.keys())

    def _update_session_from_response(
        self,
        response: StreamResponse,
        session: RemoteTaskSession,
    ) -> None:
        """Persist remote task identifiers so a later call can continue it."""
        task: Task | None = None

        if response.HasField("task"):
            task = response.task
        elif response.HasField("status_update"):
            status_update: TaskStatusUpdateEvent = response.status_update
            session.task_id = status_update.task_id or session.task_id
            session.context_id = status_update.context_id or session.context_id
        elif response.HasField("artifact_update"):
            artifact_update: TaskArtifactUpdateEvent = response.artifact_update
            session.task_id = artifact_update.task_id or session.task_id
            session.context_id = artifact_update.context_id or session.context_id

        if task is None:
            return

        session.task_id = task.id or session.task_id
        session.context_id = task.context_id or session.context_id

        if task.status.state in TERMINAL_TASK_STATES:
            # Keep identifiers for input/auth-required states so a future turn can resume.
            if task.status.state in {
                TaskState.TASK_STATE_COMPLETED,
                TaskState.TASK_STATE_FAILED,
                TaskState.TASK_STATE_CANCELED,
                TaskState.TASK_STATE_REJECTED,
            }:
                session.task_id = None
                session.context_id = None

    def _extract_text(self, response: StreamResponse) -> str:
        """Extract human-readable text from a stream response without duplicates."""
        if response.HasField("message"):
            return get_message_text(response.message).strip()

        if response.HasField("task"):
            task = response.task
            artifact_text = "\n".join(
                get_artifact_text(artifact).strip()
                for artifact in task.artifacts
                if get_artifact_text(artifact).strip()
            )
            if artifact_text:
                return artifact_text
            if task.status.HasField("message"):
                return get_message_text(task.status.message).strip()
            return ""

        if response.HasField("status_update"):
            status_update = response.status_update
            if (
                status_update.status.state in TERMINAL_TASK_STATES
                and status_update.status.HasField("message")
            ):
                return get_message_text(status_update.status.message).strip()
            return ""

        if response.HasField("artifact_update"):
            return get_artifact_text(response.artifact_update.artifact).strip()

        return ""
