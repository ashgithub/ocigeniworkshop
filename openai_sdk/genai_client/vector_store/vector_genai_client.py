"""Shared helpers for vector-store samples.

These helpers keep all sample scripts consistent and ensure authentication comes
from `OpenAIClientProvider`, which reads credentials from `sandbox.yaml`.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from openai import OpenAI

# Make imports work even when executing a file directly from the repo root.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from openai_sdk.openai_client_provider import OpenAIClientProvider


def get_client() -> OpenAI:
    """Return an authenticated OpenAI client configured for OCI GenAI."""
    return OpenAIClientProvider().oci_openai_client


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read an environment variable with an optional default value."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def require_env(name: str) -> str:
    """Read a required environment variable, raising a readable error if missing."""
    value = get_env(name)
    if not value:
        raise ValueError(
            f"Missing required environment variable '{name}'. "
            f"Set it before running this sample."
        )
    return value


def as_bool(name: str, default: bool = False) -> bool:
    """Parse common boolean-like env values."""
    value = get_env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


def print_section(title: str) -> None:
    """Print a readable section divider for CLI output."""
    print(f"\n=== {title} ===")
