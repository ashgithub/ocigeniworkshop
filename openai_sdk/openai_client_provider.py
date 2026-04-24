"""
OCI OpenAI client provider backed by sandbox.yaml configuration.

This module centralizes client creation for both OpenAI Responses examples and
OpenAI Agents SDK examples in this folder.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from agents import set_default_openai_api, set_default_openai_client
from dotenv import load_dotenv
from envyaml import EnvYAML
from oci_genai_auth import OciUserPrincipalAuth
from openai import AsyncOpenAI, OpenAI

DEFAULT_SANDBOX_CONFIG = "sandbox.yaml"
DEFAULT_OPENAI_ENDPOINT = (
    "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1"
)


class SandBoxConfigKeyNotSetException(Exception):
    """Raised when required config keys are missing."""


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class OpenAIClientProvider:
    def __init__(self, config_path: str = DEFAULT_SANDBOX_CONFIG):
        load_dotenv()
        self.config_path = config_path
        self._config = self._load_config(config_path)

        oci_cfg = self._config.get("oci", {}) if self._config else {}
        openai_cfg = self._config.get("openai", {}) if self._config else {}

        # YAML-first loading, env fallback for backward compatibility.
        self.oci_openai_endpoint = (
            _as_optional_str(openai_cfg.get("service_endpoint"))
            or os.environ.get("OPENAI_SERVICE_ENDPOINT")
            or DEFAULT_OPENAI_ENDPOINT
        )
        self.oci_openai_api_key = (
            _as_optional_str(openai_cfg.get("api_key"))
            or _as_optional_str(oci_cfg.get("api_key"))
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("OCI_AI_API_KEY")
            or "OCI"
        )
        self.oci_openai_project = (
            _as_optional_str(openai_cfg.get("project"))
            or os.environ.get("OCI_OPENAI_PROJECT")
        )
        self.oci_compartment_id = (
            _as_optional_str(openai_cfg.get("compartment"))
            or _as_optional_str(oci_cfg.get("compartment"))
            or os.environ.get("OCI_COMPARTMENT_ID")
            or os.environ.get("OCI_COMPARTMENT_OCID")
        )
        self.oci_openai_profile = (
            _as_optional_str(openai_cfg.get("profile"))
            or _as_optional_str(oci_cfg.get("profile"))
            or os.environ.get("OCI_PROFILE")
        )
        self.oci_openai_conversation_store = (
            _as_optional_str(openai_cfg.get("conversation_store"))
            or _as_optional_str(openai_cfg.get("conversation_store_id"))
            or _as_optional_str(oci_cfg.get("conversation_store"))
            or os.environ.get("OCI_CONVERSATION_STORE_ID")
            or os.environ.get("OCI_CONVERSATION_STORE")
        )

        self._verify_required_config()

        # Build shared clients.
        self.oci_openai_client = self.build_oci_openai_client()
        self.oci_openai_async_client = self.build_oci_openai_async_client()

    def _load_config(self, config_path: str) -> EnvYAML:
        try:
            return EnvYAML(config_path)
        except FileNotFoundError as exc:
            raise SandBoxConfigKeyNotSetException(
                f"Configuration file '{config_path}' was not found."
            ) from exc

    def _verify_required_config(self) -> None:
        missing: list[str] = []
        if not self.oci_openai_endpoint:
            missing.append("openai.service_endpoint")
        if not self.oci_compartment_id:
            missing.append("oci.compartment")
        if not self.oci_openai_profile:
            missing.append("oci.profile")

        if missing:
            raise SandBoxConfigKeyNotSetException(
                f"Missing required config keys in '{self.config_path}': {', '.join(missing)}"
            )

    # Helper for adding the necessary headers to make the sandbox connection.
    def _default_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.oci_compartment_id:
            headers["opc-compartment-id"] = self.oci_compartment_id
            headers["CompartmentId"] = self.oci_compartment_id
        if self.oci_openai_conversation_store:
            headers["opc-conversation-store-id"] = self.oci_openai_conversation_store
        return headers

    # Client for responses.create use cases.
    def build_oci_openai_client(self) -> OpenAI:
        client = OpenAI(
            base_url=self.oci_openai_endpoint,
            api_key=self.oci_openai_api_key,
            # project=self.oci_openai_project,
            default_headers=self._default_headers(),
            http_client=httpx.Client(
                auth=OciUserPrincipalAuth(profile_name=self.oci_openai_profile)
            ),
        )
        return client

    # Async client for Agents SDK setup mode.
    def build_oci_openai_async_client(self) -> AsyncOpenAI:
        async_client = AsyncOpenAI(
            base_url=self.oci_openai_endpoint,
            api_key=self.oci_openai_api_key,
            # project=self.oci_openai_project,
            default_headers=self._default_headers(),
            http_client=httpx.AsyncClient(
                auth=OciUserPrincipalAuth(profile_name=self.oci_openai_profile)
            ),
        )
        return async_client

    # Logger for debug, call as: OpenAIClientProvider().get_logger()
    def get_logger(self):
        self.logger = logging.getLogger("openai")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        return self.logger

    # Call this method in main() for agent files.
    # Allows connections through OCI instead of native OpenAI clients.
    def configure_agents_oci_env(self) -> AsyncOpenAI:
        set_default_openai_client(self.oci_openai_async_client, use_for_tracing=False)
        set_default_openai_api("responses")
        return self.oci_openai_async_client
