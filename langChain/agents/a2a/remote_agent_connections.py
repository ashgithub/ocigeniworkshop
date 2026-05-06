"""
What this file does:
Manages direct connections from the host agent to the remote A2A specialist
agents.

In simple terms:
- this file knows where the specialist agents live
- this file can also ask the central registry which agents are available
- this file downloads each agent card from its published A2A route
- this file builds reusable A2A clients
- this file sends messages to remote agents and collects their replies
- this file remembers remote task IDs so multi-step conversations can continue

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai
- Agent connections adapted from: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/hosts/multiagent/remote_agent_connection.py

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
- Step 1: Shared timeout, registry, and URL configuration
- Step 2: Remote task session tracking
- Step 3: Initialize HTTP and A2A client helpers
- Step 4: Discover remote agents from the registry and published agent cards
- Step 5: Send a message to a selected remote agent
- Step 6: Read streamed A2A events and extract text
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
from google.protobuf.json_format import ParseDict


# ============================================================================
# STEP 1: SHARED CONNECTION SETTINGS
# ============================================================================
# These values are shared by every remote agent call made by the host agent.

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
REGISTRY_URL = "http://localhost:9990"
TERMINAL_TASK_STATES = {
    TaskState.TASK_STATE_COMPLETED,
    TaskState.TASK_STATE_FAILED,
    TaskState.TASK_STATE_CANCELED,
    TaskState.TASK_STATE_REJECTED,
    TaskState.TASK_STATE_INPUT_REQUIRED,
    TaskState.TASK_STATE_AUTH_REQUIRED,
}


# ============================================================================
# STEP 2: REMOTE TASK SESSION STATE
# ============================================================================
# A remote A2A conversation may continue over more than one request. These IDs
# let the host continue the same remote task instead of starting from scratch.

@dataclass
class RemoteTaskSession:
    """Tracks the remote task identifiers for a host conversation."""

    task_id: str | None = None
    context_id: str | None = None


# ============================================================================
# STEP 3: REMOTE CONNECTION MANAGER
# ============================================================================
# This is the main utility class used by the LangGraph host agent.

class RemoteAgentConnections:
    """Discover remote agents and send A2A requests to them."""

    def __init__(
        self,
        remote_agent_urls: Iterable[str] | None = None,
        registry_url: str | None = REGISTRY_URL,
    ) -> None:
        self.remote_agent_urls = list(
            remote_agent_urls or DEFAULT_REMOTE_AGENT_URLS
        )
        self.registry_url = registry_url
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

    # =========================================================================
    # STEP 4: AGENT DISCOVERY
    # =========================================================================
    # Discovery means: first ask the registry which agent cards are currently
    # registered, then merge that list with any direct URL fallbacks.
    async def discover_agents(self, force_refresh: bool = False) -> list[AgentCard]:
        """Discover remote agents from the registry and direct URLs."""
        if self._agent_cards and not force_refresh:
            return list(self._agent_cards.values())

        discovered_cards: dict[str, AgentCard] = {}

        for card in await self._discover_from_registry():
            discovered_cards[card.name] = card

        for card in await self._discover_from_urls():
            discovered_cards[card.name] = card

        self._drop_stale_clients(discovered_cards)
        self._agent_cards = discovered_cards
        print(f"Discovered {len(self._agent_cards)} remote A2A agent(s).")
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

    # =========================================================================
    # STEP 5: REMOTE AGENT CALL
    # =========================================================================
    # This method builds an A2A request, sends it to the chosen specialist, and
    # returns the combined text response to the host agent.
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
            await self.discover_agents(force_refresh=True)

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

    async def _discover_from_registry(self) -> list[AgentCard]:
        """Fetch agent cards from the central registry when available."""
        if not self.registry_url:
            return []

        try:
            response = await self._httpx_client.get(
                f"{self.registry_url}/registry/agents"
            )
            response.raise_for_status()
            agent_dicts = response.json()
        except Exception:
            return []

        cards: list[AgentCard] = []
        for agent_dict in agent_dicts:
            try:
                cards.append(ParseDict(agent_dict, AgentCard()))
            except Exception:
                continue
        return cards

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

    def _drop_stale_clients(self, discovered_cards: dict[str, AgentCard]) -> None:
        """Remove cached clients when an agent disappears or changes endpoint."""
        for agent_name in list(self._client_cache):
            previous_card = self._agent_cards.get(agent_name)
            current_card = discovered_cards.get(agent_name)

            if current_card is None:
                self._client_cache.pop(agent_name, None)
                continue

            if previous_card is None:
                continue

            previous_url = self._primary_interface_url(previous_card)
            current_url = self._primary_interface_url(current_card)
            if previous_url != current_url:
                self._client_cache.pop(agent_name, None)

    def _primary_interface_url(self, agent_card: AgentCard) -> str:
        """Return the first published interface URL for a card."""
        if not agent_card.supported_interfaces:
            return ""
        return agent_card.supported_interfaces[0].url

    # =========================================================================
    # STEP 6: STREAM PROCESSING
    # =========================================================================
    # A2A responses can arrive as multiple events. These helpers track the task
    # state and convert the stream into simple text for the host agent.
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
