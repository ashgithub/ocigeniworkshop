""" What this file does:
Demonstrates the local Shell Tool `shell_call` / `shell_call_output` loop.

Local shell is different from hosted shell. OCI does not execute commands for
you. The model returns `shell_call` items, this application validates and runs
approved commands in a customer-managed runtime, then sends `shell_call_output`
back with the same `call_id`.

Beginner mental model:
- The first API call asks the model what local commands it wants to run.
- This script checks those commands against a conservative PowerShell guard.
- The script sends stdout, stderr, and exit status back as `shell_call_output`.
- The loop repeats until the model has enough information for a final answer.

Key difference:
- Hosted shell (`container_auto` or `container_reference`): OCI runs commands.
- Local shell (`environment.type = "local"`): your app runs approved commands.
- `shell_call_output`: required so the model can continue after local commands.

Documentation for reference:
- Shell Tool guide: https://developers.openai.com/api/docs/guides/tools-shell
- Responses API reference: https://platform.openai.com/docs/api-reference/responses

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Review the local command guard before enabling live calls.
- This example executes approved commands with Windows PowerShell explicitly.
- Run this only from a sandbox or approved learning environment.

How to run from repo root:
uv run openai_sdk/genai_client/shell_tools/local_win_shell.py

Safe experiments:
1. Start with read-only commands such as `git status` and `Get-ChildItem`.
2. Keep `LOCAL_SHELL_MAX_ROUNDS` low while learning the loop.
3. Expand `GuardedPowerShell.is_allowed` only after adding your own approval
   and audit policy.

Important sections:
1. Constants: set model, safety limits, executable, and prompt.
2. `GuardedPowerShell`: validate and execute approved read-only commands.
3. Helper functions: translate SDK objects into shell output payloads.
4. Step 1: Send a local Shell Tool request.
5. Step 2: Find `shell_call` items in the response.
6. Step 3: Execute approved commands locally with PowerShell.
7. Step 4: Send `shell_call_output` and continue until the final answer.
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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"

# Keep local execution bounded. These limits make the demo easier to reason
# about and reduce the chance of a long-running local command loop.
LOCAL_SHELL_MAX_ROUNDS = 4
LOCAL_COMMAND_TIMEOUT_SECONDS = 20
POWERSHELL_EXECUTABLE = "powershell"

# The prompt asks for read-only repository inspection so the guard can stay
# intentionally small and beginner-friendly.
PROMPT = """
Use the local shell to inspect this repository.
Request only safe, read-only Windows PowerShell commands.

Please:
1. Show the short git status.
2. List the files in `openai_sdk/genai_client/shell_tools`.
3. Identify the Shell Tool example that demonstrates local command execution.
"""

@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool


class GuardedPowerShell:
    """Small read-only PowerShell executor for the local shell demo.

    The guard is intentionally conservative: it blocks common write, network,
    shell-chaining, traversal, and secret-reading patterns before allowing a
    command to run in the shared workshop workspace.
    """

    def __init__(self, workspace: Path, timeout_seconds: int) -> None:
        self.workspace = workspace.resolve()
        self.timeout_seconds = timeout_seconds

    def is_allowed(self, command: str) -> bool:
        """Return True only when a command passes the deny-list and allow-list."""
        normalized = " ".join(command.lower().split())

        # Block secrets, parent traversal, shell chaining, network calls, writes,
        # deletes, process control, and other operations outside this read-only demo.
        blocked_fragments = [
            ".env",
            "sandbox.yaml",
            ".oci",
            "api_key",
            "password",
            "secret",
            "token",
            "..",
            "~",
            ":",
            "|",
            ";",
            "&&",
            "||",
            ">",
            ">>",
            "add-content",
            "clear-content",
            "curl",
            "del ",
            "erase ",
            "invoke-restmethod",
            "invoke-webrequest",
            "iwr ",
            "mkdir",
            "move-item",
            "new-item",
            "out-file",
            "remove-item",
            "rename-item",
            "rm ",
            "rmdir",
            "set-content",
            "start-process",
            "stop-process",
            "wget",
        ]
        if any(fragment in normalized for fragment in blocked_fragments):
            return False

        # Allow only simple discovery commands that are useful for this workshop.
        allowed_prefixes = [
            "dir",
            "get-childitem",
            "get-content",
            "get-location",
            "git status",
            "ls",
            "pwd",
            "python --version",
            "python -v",
            "rg ",
            "select-string",
            "uv --version",
        ]
        return any(normalized.startswith(prefix) for prefix in allowed_prefixes)

    def run(self, command: str, timeout_seconds: int | None = None) -> CommandResult:
        """Execute an allowed PowerShell command and capture stdout, stderr, and exit."""
        if not self.is_allowed(command):
            return CommandResult(
                stdout="",
                stderr=(
                    "Command was not executed by the local demo guard. "
                    "Use safe read-only commands such as git status, Get-ChildItem, "
                    "Get-Content, rg, python --version, or uv --version."
                ),
                exit_code=126,
                timed_out=False,
            )

        try:
            completed = subprocess.run(
                [
                    POWERSHELL_EXECUTABLE,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                cwd=self.workspace,
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
                stdout=exc.stdout or "", #type:ignore
                stderr=exc.stderr or "", #type:ignore
                exit_code=None,
                timed_out=True,
            )


def attr_or_key(item: Any, name: str, default: Any = None) -> Any:
    """Read a field from either an SDK object or a dictionary."""
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)

def shell_calls_from(response: Any) -> list[Any]:
    """Return only the `shell_call` output items from a Responses API result."""
    output = attr_or_key(response, "output", [])
    return [item for item in output if attr_or_key(item, "type") == "shell_call"]


def commands_from_shell_call(shell_call: Any) -> list[str]:
    """Normalize a shell call into a list of command strings."""
    action = attr_or_key(shell_call, "action", {})
    commands = attr_or_key(action, "commands", [])
    if isinstance(commands, str):
        return [commands]
    return list(commands)


def command_output_payload(shell_call: Any, executor: GuardedPowerShell) -> dict[str, Any]:
    """Execute requested commands and package the `shell_call_output` payload."""
    action = attr_or_key(shell_call, "action", {})
    timeout_ms = attr_or_key(action, "timeout_ms")
    timeout_seconds = (
        min(LOCAL_COMMAND_TIMEOUT_SECONDS, max(1, int(timeout_ms) // 1000))
        if timeout_ms
        else None
    )

    output_items = []
    for command in commands_from_shell_call(shell_call):
        print(f"Step 3/4: Evaluating local command request: {command}")
        result = executor.run(command, timeout_seconds=timeout_seconds)
        if result.timed_out:
            outcome: dict[str, Any] = {"type": "timeout"}
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

def main() -> None:
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 1: Send a request where the model can ask for local shell commands.
    print("Step 1/4: Asking the model for local shell_call instructions...")
    response = client.responses.create(
        model=MODEL_ID,
        instructions=(
            "The local shell environment is Windows PowerShell. "
            "Request only safe, read-only inspection commands. "
            "Keep the final answer concise."
        ),
        tools=[
            {
                "type": "shell",
                "environment": {
                    "type": "local",
                },
            }
        ],
        input=PROMPT
    )

    workspace = Path(__file__).resolve().parents[3]
    executor = GuardedPowerShell(
        workspace=workspace,
        timeout_seconds=LOCAL_COMMAND_TIMEOUT_SECONDS,
    )

    # Step 2-4: Execute shell_call requests and continue with shell_call_output.
    for round_number in range(1, LOCAL_SHELL_MAX_ROUNDS + 1):
        shell_calls = shell_calls_from(response)
        if not shell_calls:
            print("<------------- Local shell final response ------------>\n")
            print(response.output_text)
            return

        print(
            f"Step 2/4: Received {len(shell_calls)} shell_call item(s) "
            f"in round {round_number}."
        )
        follow_up_input = [
            command_output_payload(shell_call=shell_call, executor=executor)
            for shell_call in shell_calls
        ]
        print("Step 4/4: Sending shell_call_output back to the model...")
        response = client.responses.create(
            model=MODEL_ID,
            previous_response_id=response.id,
            tools=[
                {
                    "type": "shell",
                    "environment": {
                        "type": "local",
                    },
                }
            ],
            input=follow_up_input,
        )

    raise RuntimeError("Stopped after LOCAL_SHELL_MAX_ROUNDS to avoid a long-running loop.")


if __name__ == "__main__":
    main()
