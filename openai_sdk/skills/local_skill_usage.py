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
1. Review the local skill folders under openai_sdk/skills/samples.
2. Run this file after your OCI OpenAI-compatible environment is configured.
"""

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
MAX_LOCAL_SHELL_ROUNDS = 10
COMMAND_TIMEOUT_SECONDS = 30

SKILLS_DIR = Path(__file__).resolve().parent / "samples"
REPO_TOUR_SKILL = SKILLS_DIR / "repo-tour-guide"
MODULE_DOCS_SKILL = SKILLS_DIR / "module-docs-explainer"
WORKSHOP_RUNNER_SKILL = SKILLS_DIR / "workshop-result-runner"

PROMPT = """
Use the repo-tour-guide skill.

Scenario:
- I am onboarding beginner developers in an innovation lab.
- They need to understand this OCI AI Developer Learning Path repo.
- Focus on where to start, which modules matter, and what local checks are safe.
- Include a short result summary if you use the bundled script.

Use the bundled script if helpful, then return a compact learning path.

uv run openai_sdk/skills/local_skill_usage.py
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
                stdout=exc.stdout or "", #type:ignore
                stderr=exc.stderr or "", #type:ignore
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
            "name": "repo-tour-guide",
            "description": (
                "Give a beginner-friendly map of this OCI AI workshop repo, "
                "including where to start and which files to open next."
            ),
            "path": str(REPO_TOUR_SKILL),
        },
        {
            "name": "module-docs-explainer",
            "description": (
                "Explain repo modules using bundled references and current README files "
                "for OpenAI SDK, LangChain, OCI-native, database, RAG, agents, and skills."
            ),
            "path": str(MODULE_DOCS_SKILL),
        },
        {
            "name": "workshop-result-runner",
            "description": (
                "Run a safe local repo scan and summarize runnable learning paths "
                "without calling cloud services."
            ),
            "path": str(WORKSHOP_RUNNER_SKILL),
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

    client: OpenAI = OpenAIClientProvider().oci_openai_client
    workspace = Path(__file__).resolve().parents[2]
    executor = GuardedLocalShell(workspace=workspace, timeout_seconds=COMMAND_TIMEOUT_SECONDS)

    response = client.responses.create(
        model=MODEL_ID,
        tools=tools, #type:ignore
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
            tools=tools, #type:ignore
            input=follow_up_input,
        )

    raise RuntimeError("Stopped after MAX_LOCAL_SHELL_ROUNDS to avoid an accidental long-running loop.")


if __name__ == "__main__":
    main()
