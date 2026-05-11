"""Shell Tool examples for OCI GenAI Responses API.

The May guide introduces the Shell Tool for terminal-native workflows:
file inspection, script execution, diagnostics, validation, artifact generation,
data transformation, dependency installation, and local-shell execution.

This file is intentionally beginner-friendly:
1. Read the editable values below.
2. Run in preview mode first:

       uv run openai_sdk/genai_client/shell_tool.py

3. Set RUN_LIVE_API=True when Shell Tool access is enabled in your tenancy.
4. Pick EXAMPLE_TO_RUN to try one scenario at a time.

Examples included from the docs:
- hosted shell with `container_auto`
- hosted shell with explicit `container_reference`
- hosted shell with network allowlist
- hosted shell generating a file artifact
- local shell request plus shell_call_output loop
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


# -----------------------------
# Edit these lines before running
# -----------------------------

MODEL_ID = "openai.gpt-5.2"

# Keep False for a request preview that does not call the API.
RUN_LIVE_API = False

# Options:
# - "hosted_auto"
# - "hosted_container_reference"
# - "hosted_network_allowlist"
# - "hosted_artifact"
# - "local_shell"
EXAMPLE_TO_RUN = "hosted_auto"

CONTAINER_NAME = "workshop-shell-container"
CONTAINER_MEMORY_LIMIT = "1g"

# Network access should be minimal. The docs use PyPI as an allowlist example.
ALLOWED_NETWORK_DOMAINS = ["pypi.org", "files.pythonhosted.org"]

# Local shell execution is customer-managed. This demo only allows safe read-only
# commands useful for inspecting the local workshop repository.
LOCAL_SHELL_MAX_ROUNDS = 4
LOCAL_COMMAND_TIMEOUT_SECONDS = 20


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool


class GuardedLocalShell:
    """Small local shell executor for the docs-style shell_call loop."""

    def __init__(self, workspace: Path, timeout_seconds: int) -> None:
        self.workspace = workspace.resolve()
        self.timeout_seconds = timeout_seconds

    def is_allowed(self, command: str) -> bool:
        normalized = f" {command.lower()} "
        blocked = [
            " del ",
            " erase ",
            " move ",
            " remove-item ",
            " ren ",
            " rm ",
            " rmdir ",
            " set-content ",
            " start-process ",
            " wget ",
            " curl ",
        ]
        if any(token in normalized for token in blocked):
            return False

        allowed_prefixes = [
            "dir",
            "get-childitem",
            "get-content",
            "select-string",
            "rg",
            "python --version",
            "python -v",
            "uv --version",
            "git status",
        ]
        return any(normalized.strip().startswith(prefix) for prefix in allowed_prefixes)

    def run(self, command: str, timeout_seconds: int | None = None) -> CommandResult:
        if not self.is_allowed(command):
            return CommandResult(
                stdout="",
                stderr=(
                    "Command was not executed by the local demo guard. "
                    "Use read-only inspection commands such as dir, Get-ChildItem, rg, "
                    "python --version, uv --version, or git status."
                ),
                exit_code=126,
                timed_out=False,
            )

        try:
            completed = subprocess.run(
                command,
                cwd=self.workspace,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout_seconds or self.timeout_seconds,
            )
            return CommandResult(
                stdout=completed.stdout,
                stderr=completed.stderr,
                exit_code=completed.returncode,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                exit_code=None,
                timed_out=True,
            )


def attr_or_key(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def shell_tool(environment: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"type": "shell", "environment": environment}]


def hosted_auto_request() -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "tools": shell_tool({"type": "container_auto"}),
        "input": (
            "Use the shell tool to inspect the workspace. Run non-destructive commands "
            "to show the current directory, list files, print runtime versions for "
            "Python and Node.js if available, and summarize what you found."
        ),
    }


def hosted_network_allowlist_request() -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "tools": shell_tool(
            {
                "type": "container_auto",
                "network_policy": {
                    "type": "allowlist",
                    "allowed_domains": ALLOWED_NETWORK_DOMAINS,
                },
            }
        ),
        "input": (
            "Use the shell tool to install the Python package requests from the "
            "approved package domains, print the installed version, and explain "
            "whether the allowlisted network workflow succeeded."
        ),
    }


def local_shell_request() -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "instructions": (
            "The local shell environment is Windows PowerShell. Request only safe, "
            "read-only inspection commands. Keep the final answer concise."
        ),
        "tools": shell_tool({"type": "local"}),
        "input": (
            "Use the local shell to inspect this repository. Show the current git "
            "status, list the files in openai_sdk/genai_client, and identify the "
            "new Shell Tool example file."
        ),
    }


def print_preview(request_body: dict[str, Any]) -> None:
    print("<------------- Shell Tool request preview ------------>\n")
    print(json.dumps(request_body, indent=2))
    print("\nSet RUN_LIVE_API=True after Shell Tool access is enabled.")


def print_response(title: str, response: Any) -> None:
    print(f"<------------- {title} ------------>\n")
    print(response.output_text)


def run_hosted_auto(client: OpenAI) -> None:
    # Step 1: Ask OCI to provision or reuse a hosted container automatically.
    request_body = hosted_auto_request()
    response = client.responses.create(**request_body)
    print_response("Hosted shell with container_auto", response)


def run_hosted_container_reference(client: OpenAI) -> None:
    # Step 1: Create a named OCI GenAI container.
    container = client.containers.create(
        name=CONTAINER_NAME,
        memory_limit=CONTAINER_MEMORY_LIMIT,
    )
    print(f"Created shell container: {container.id}\n")

    # Step 2: Ask the model to use that exact container.
    response = client.responses.create(
        model=MODEL_ID,
        tools=shell_tool(
            {
                "type": "container_reference",
                "container_id": container.id,
            }
        ),
        input=(
            "Use the shell tool to list files, check disk usage, print runtime "
            "versions, and summarize the container environment."
        ),
    )
    print_response("Hosted shell with container_reference", response)


def run_hosted_network_allowlist(client: OpenAI) -> None:
    # Step 1: Provide a scoped outbound network policy to the hosted shell.
    request_body = hosted_network_allowlist_request()
    response = client.responses.create(**request_body)
    print_response("Hosted shell with network allowlist", response)


def run_hosted_artifact(client: OpenAI) -> None:
    # Step 1: Create a named container so generated files persist for inspection.
    container = client.containers.create(
        name=f"{CONTAINER_NAME}-artifact",
        memory_limit=CONTAINER_MEMORY_LIMIT,
    )
    print(f"Created artifact container: {container.id}\n")

    # Step 2: Ask shell to generate a report in the container workspace.
    response = client.responses.create(
        model=MODEL_ID,
        tools=shell_tool(
            {
                "type": "container_reference",
                "container_id": container.id,
            }
        ),
        input=(
            "Use the shell tool to create /mnt/data/shell_tool_report.md. "
            "The report should include runtime versions, current workspace files, "
            "and a short note explaining what the Shell Tool is useful for. "
            "After writing the file, print its contents."
        ),
    )
    print_response("Hosted shell artifact generation", response)

    # Step 3: List container files so beginners can see where generated artifacts live.
    files_page = client.containers.files.list(container_id=container.id)
    print("\nContainer files:")
    for container_file in files_page.data:
        print(f"- {container_file.id} | {container_file.path} | {container_file.bytes} bytes")


def shell_calls_from(response: Any) -> list[Any]:
    return [item for item in response.output if attr_or_key(item, "type") == "shell_call"]


def command_output_payload(shell_call: Any, executor: GuardedLocalShell) -> dict[str, Any]:
    action = attr_or_key(shell_call, "action", {})
    commands = attr_or_key(action, "commands", [])
    timeout_ms = attr_or_key(action, "timeout_ms")
    timeout_seconds = (
        min(LOCAL_COMMAND_TIMEOUT_SECONDS, max(1, int(timeout_ms / 1000)))
        if timeout_ms
        else None
    )

    output_items = []
    for command in commands:
        result = executor.run(command, timeout_seconds=timeout_seconds)
        outcome: dict[str, Any]
        if result.timed_out:
            outcome = {"type": "timeout"}
        else:
            outcome = {"type": "exit", "exit_code": result.exit_code}

        output_items.append(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "outcome": outcome,
            }
        )

    payload: dict[str, Any] = {
        "type": "shell_call_output",
        "call_id": attr_or_key(shell_call, "call_id"),
        "output": output_items,
    }

    max_output_length = attr_or_key(action, "max_output_length")
    if max_output_length is not None:
        payload["max_output_length"] = max_output_length

    return payload


def run_local_shell(client: OpenAI) -> None:
    # Step 1: Send a request with the local shell environment.
    request_body = local_shell_request()
    response = client.responses.create(**request_body)

    # Step 2: Execute requested shell_call commands locally, then send back
    # shell_call_output with the same call_id.
    workspace = Path(__file__).resolve().parents[2]
    executor = GuardedLocalShell(
        workspace=workspace,
        timeout_seconds=LOCAL_COMMAND_TIMEOUT_SECONDS,
    )

    for _round in range(LOCAL_SHELL_MAX_ROUNDS):
        shell_calls = shell_calls_from(response)
        if not shell_calls:
            print_response("Local shell final response", response)
            return

        follow_up_input = [
            command_output_payload(shell_call=shell_call, executor=executor)
            for shell_call in shell_calls
        ]
        response = client.responses.create(
            model=MODEL_ID,
            previous_response_id=response.id,
            tools=request_body["tools"],
            input=follow_up_input,
        )

    raise RuntimeError("Stopped after LOCAL_SHELL_MAX_ROUNDS to avoid a long-running loop.")


def preview_for_selected_example() -> dict[str, Any]:
    if EXAMPLE_TO_RUN == "hosted_auto":
        return hosted_auto_request()
    if EXAMPLE_TO_RUN == "hosted_network_allowlist":
        return hosted_network_allowlist_request()
    if EXAMPLE_TO_RUN == "local_shell":
        return local_shell_request()
    if EXAMPLE_TO_RUN == "hosted_container_reference":
        return {
            "step_1": {
                "client.containers.create": {
                    "name": CONTAINER_NAME,
                    "memory_limit": CONTAINER_MEMORY_LIMIT,
                }
            },
            "step_2": {
                "model": MODEL_ID,
                "tools": shell_tool(
                    {
                        "type": "container_reference",
                        "container_id": "<container-id-from-step-1>",
                    }
                ),
                "input": "Use the shell tool to list files, check disk usage, and summarize the environment.",
            },
        }
    if EXAMPLE_TO_RUN == "hosted_artifact":
        return {
            "step_1": {
                "client.containers.create": {
                    "name": f"{CONTAINER_NAME}-artifact",
                    "memory_limit": CONTAINER_MEMORY_LIMIT,
                }
            },
            "step_2": {
                "model": MODEL_ID,
                "tools": shell_tool(
                    {
                        "type": "container_reference",
                        "container_id": "<container-id-from-step-1>",
                    }
                ),
                "input": "Use the shell tool to create /mnt/data/shell_tool_report.md and print it.",
            },
            "step_3": "client.containers.files.list(container_id='<container-id-from-step-1>')",
        }
    raise ValueError(
        "EXAMPLE_TO_RUN must be hosted_auto, hosted_container_reference, "
        "hosted_network_allowlist, hosted_artifact, or local_shell."
    )


def main() -> None:
    if not RUN_LIVE_API:
        print_preview(preview_for_selected_example())
        return

    client: OpenAI = OpenAIClientProvider().oci_openai_client

    if EXAMPLE_TO_RUN == "hosted_auto":
        run_hosted_auto(client)
    elif EXAMPLE_TO_RUN == "hosted_container_reference":
        run_hosted_container_reference(client)
    elif EXAMPLE_TO_RUN == "hosted_network_allowlist":
        run_hosted_network_allowlist(client)
    elif EXAMPLE_TO_RUN == "hosted_artifact":
        run_hosted_artifact(client)
    elif EXAMPLE_TO_RUN == "local_shell":
        run_local_shell(client)
    else:
        raise ValueError(f"Unknown EXAMPLE_TO_RUN: {EXAMPLE_TO_RUN}")


if __name__ == "__main__":
    main()
