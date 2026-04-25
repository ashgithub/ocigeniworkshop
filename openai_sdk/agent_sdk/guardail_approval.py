""" What this file does:
Demonstrates a human-in-the-loop approval flow for sensitive tool calls.
The agent requests approval before executing `cancel_order`.

Documentation for reference:
- OpenAI Agents SDK guardails: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- OpenAI Agents guide: https://developers.openai.com/api/docs/guides/agents/quickstart
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code
- #genai-hosted-deployment-users: Information on GA deployment and integrations

Environment setup:
- Ensure `sandbox.yaml` contains valid OCI profile, project, and compartment values
- `.env` is optional for this script
- Ensure you have access to OCI Generative AI services

How to run the file:
uv run python -m openai_sdk.agent_sdk.guardail_approval

Safe experiments:
1. Change `USER_PROMPT` to other support actions.
2. Adjust `rejection_message` to study final response behavior.
3. Add a second approval-required tool and compare outputs.

Important sections:
1. Step 1: Define a tool with `needs_approval=True`.
2. Step 2: Build an agent that can call that tool.
3. Step 3: Run, handle interruptions, and approve/reject.
"""

import asyncio
import json

from agents import Agent, Runner, function_tool
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Cancel order 123."

# Step 1: Create the function tool to be called with approval request
@function_tool(needs_approval=True)
async def cancel_order(order_id: int) -> str:
    return f"Cancelled order {order_id}"

# Step 2: Instantiate the agent.
agent = Agent(
    name="Support agent",
    instructions="Handle support requests and ask for approval when needed.",
    tools=[cancel_order],
    model=MODEL_ID,
)

# Helper: Pretty-print tool arguments when approval is requested.
def _pretty_arguments(arguments: str | None) -> str:
    if not arguments:
        return "{}"
    try:
        parsed = json.loads(arguments)
    except json.JSONDecodeError:
        return arguments
    return json.dumps(parsed, indent=2)

# Helper: Ask the user whether to approve/reject an interrupted tool call.
def _ask_for_approval(interruption) -> bool:
    tool_name = interruption.qualified_name or interruption.name or "unknown_tool"
    call_id = interruption.call_id or "unknown_call_id"
    args_preview = _pretty_arguments(interruption.arguments)

    print("\nApproval required:")
    print(f"Tool: {tool_name}")
    print(f"Call ID: {call_id}")
    print("Arguments:")
    print(args_preview)

    while True:
        answer = input("Approve this action? [y/n]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer with 'y' or 'n'.")

async def main() -> None:
    # Step 3: Configure environment for using OCI auth and not native OpenAI.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 4: Run the agent. Sensitive tool calls may return interruptions.
    result = await Runner.run(agent, USER_PROMPT)

    # Step 5: Resolve each interruption by user approval/rejection.
    if result.interruptions:
        print(f"Found {len(result.interruptions)} interruption(s).")
        state = result.to_state()
        for interruption in result.interruptions:
            if _ask_for_approval(interruption):
                state.approve(interruption)
            else:
                state.reject(
                    interruption,
                    rejection_message="User denied the cancellation request.",
                )
        result = await Runner.run(agent, state)

    # Step 6: Print final response after approvals are processed.
    print("Final response:")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
