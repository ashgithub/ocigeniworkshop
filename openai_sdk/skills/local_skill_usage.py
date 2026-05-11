"""Use local Skills with the Shell tool.

Cloud Skill upload is still on hold, so this file demonstrates the local Skill
shape from the May guide:

    "environment": {
        "type": "local",
        "skills": [
            {"name": "...", "description": "...", "path": "..."}
        ]
    }

In local mode, OCI Generative AI does not run commands for you. The model can
request shell actions, then this application validates and executes them in your
customer-managed runtime and sends shell_call_output back.

Beginner flow:
1. Keep RUN_LIVE_API=False and run this file to inspect the request shape.
2. Review the local skill folders under openai_sdk/skills/samples.
3. Set RUN_LIVE_API=True when local shell is enabled in your environment.
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


MODEL_ID = "openai.gpt-5.2"
RUN_LIVE_API = False
MAX_LOCAL_SHELL_ROUNDS = 4
COMMAND_TIMEOUT_SECONDS = 30

SKILLS_DIR = Path(__file__).resolve().parent / "samples"
TEAM_COMMS_SKILL = SKILLS_DIR / "team-comms-brief"
DEV_HANDOFF_SKILL = SKILLS_DIR / "dev-handoff-kit"

PROMPT = """
Use the team-comms-brief Skill and dev-handoff-kit Skill.

Scenario:
- I added local and inline Skill examples to the OCI GenAI workshop.
- Hosted Skill upload is on hold until Skills access is released in this environment.
- The audience is beginner developers in an innovation workshop.
- I need a short Slack update, an Outlook follow-up email, and a developer handoff note.

Use the bundled scripts if helpful, then return the final communication package.
"""


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool


class GuardedLocalShell:
    """Small local executor for demo use.

    The allowlist keeps the example focused on scripts inside openai_sdk/skills.
    Expand it only after you add your own approval and audit controls.
    """

    def __init__(self, workspace: Path, timeout_seconds: int) -> None:
        self.workspace = workspace.resolve()
        self.timeout_seconds = timeout_seconds

    def is_allowed(self, command: str) -> bool:
        normalized = command.lower().replace("/", "\\")
        blocked_tokens = [" rm ", " del ", " remove-item ", " rmdir ", " curl ", " wget "]
        if any(token in f" {normalized} " for token in blocked_tokens):
            return False
        return "openai_sdk\\skills\\samples" in normalized and ".py" in normalized

    def run(self, command: str, timeout_seconds: int | None = None) -> CommandResult:
        if not self.is_allowed(command):
            return CommandResult(
                stdout="",
                stderr=(
                    "Command was not executed by the local demo guard. "
                    "Only Python scripts under openai_sdk/skills/samples are allowed."
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


def local_skill_specs() -> list[dict[str, str]]:
    return [
        {
            "name": "team-comms-brief",
            "description": (
                "Draft Slack announcements and Outlook follow-up emails for "
                "developer enablement, launches, releases, and workshop updates."
            ),
            "path": str(TEAM_COMMS_SKILL),
        },
        {
            "name": "dev-handoff-kit",
            "description": (
                "Create developer handoff notes, adoption checklists, reviewer notes, "
                "and risk summaries for code or sample-workshop changes."
            ),
            "path": str(DEV_HANDOFF_SKILL),
        },
    ]


def build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "shell",
            "environment": {
                "type": "local",
                "skills": local_skill_specs(),
            },
        }
    ]


def shell_calls_from(response: Any) -> list[Any]:
    return [item for item in response.output if attr_or_key(item, "type") == "shell_call"]


def command_output_payload(shell_call: Any, executor: GuardedLocalShell) -> dict[str, Any]:
    action = attr_or_key(shell_call, "action", {})
    commands = attr_or_key(action, "commands", [])
    timeout_ms = attr_or_key(action, "timeout_ms")
    timeout_seconds = min(COMMAND_TIMEOUT_SECONDS, max(1, int(timeout_ms / 1000))) if timeout_ms else None

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


def main() -> None:
    tools = build_tools()

    if not RUN_LIVE_API:
        print("<------------- Local Skills request preview ------------>\n")
        print(json.dumps({"model": MODEL_ID, "tools": tools, "input": PROMPT.strip()}, indent=2))
        print("\nSet RUN_LIVE_API=True after local shell is enabled and reviewed.")
        return

    client: OpenAI = OpenAIClientProvider().oci_openai_client
    workspace = Path(__file__).resolve().parents[2]
    executor = GuardedLocalShell(workspace=workspace, timeout_seconds=COMMAND_TIMEOUT_SECONDS)

    response = client.responses.create(
        model=MODEL_ID,
        tools=tools,
        input=PROMPT,
    )

    for _round in range(MAX_LOCAL_SHELL_ROUNDS):
        shell_calls = shell_calls_from(response)
        if not shell_calls:
            print("<------------- Local Skills final response ------------>\n")
            print(response.output_text)
            return

        follow_up_input = [
            command_output_payload(shell_call=shell_call, executor=executor)
            for shell_call in shell_calls
        ]
        response = client.responses.create(
            model=MODEL_ID,
            previous_response_id=response.id,
            tools=tools,
            input=follow_up_input,
        )

    raise RuntimeError("Stopped after MAX_LOCAL_SHELL_ROUNDS to avoid an accidental long-running loop.")


if __name__ == "__main__":
    main()
