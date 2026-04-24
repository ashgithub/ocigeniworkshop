""" What this file does:
Demonstrates `code_interpreter` usage with:
1) automatic container, 2) automatic container with memory config,
3) explicit named container.

Documentation for reference:
- Code interpreter guide: https://platform.openai.com/docs/guides/tools-code-interpreter
- Containers guide: https://platform.openai.com/docs/guides/tools-code-interpreter#containers
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users
- #igiu-innovation-lab
- #igiu-ai-learning
- #genai-hosted-deployment-users

Environment setup:
- Create `.env` from `.env.example`
- Ensure endpoint/project/profile values are set for OCI

How to run the file:
uv run python genai_client/code_interpreter.py

Safe experiments:
1. Change prompts to other math/data tasks.
2. Adjust `memory_limit` and compare behavior.
3. Reuse a named container for related tasks.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Run auto-container example.
3. Step 3: Run auto-container with memory limit.
4. Step 4: Run named-container example. """

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-4.1"
PROMPT_LINEAR = "I need to solve the equation 3x + 11 = 14. Can you help me?"
PROMPT_NESTED_ROOT = "Use the python tool to find the square root of the square root of (4 * 3.82)."
PROMPT_REQUIRED_TOOL = "Use the python tool to calculate what is 4 * 3.82, then find its square root, then find the square root of that result."


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Auto container example.
    first_response = client.responses.create(
        model=MODEL_ID,
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
        instructions="Write and run code using python tool to answer the question.",
        input=PROMPT_LINEAR,
    )
    print(first_response.output_text)

    # Step 3: Auto container with custom memory limit.
    second_response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type": "code_interpreter",
                "container": {"type": "auto", "memory_limit": "1g"},
            }
        ],
        input=PROMPT_NESTED_ROOT,
    )
    print(second_response.output_text)

    # Step 4: Explicit named container example.
    named_container = client.containers.create(name="test-container", memory_limit="4g")
    third_response = client.responses.create(
        model=MODEL_ID,
        tools=[{"type": "code_interpreter", "container": named_container.id}],
        tool_choice="required",
        input=PROMPT_REQUIRED_TOOL,
    )
    print(third_response.output_text)


if __name__ == "__main__":
    main()

