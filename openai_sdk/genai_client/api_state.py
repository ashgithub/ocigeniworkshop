""" What this file does:
Demonstrates manual function-calling state management:
1) let model request a tool call,
2) execute tool locally,
3) continue with `previous_response_id`.

Documentation for reference:
- Function calling guide: https://platform.openai.com/docs/guides/function-calling
- Responses API migration and features: https://developers.openai.com/api/docs/guides/migrate-to-responses
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Set up the credentials for OCI over the `sandbox.yaml file`
- Make sure to set up a project ID from the console, consult the GenAI platform GA docs for guidance
- Set up the right compartment ID and profile name over the config file

How to run the file:
uv run python -m openai_sdk.genai_client.api_state

Safe experiments:
1. Add fields to tool schema (example: temperature units).
2. Change `FINAL_INSTRUCTIONS` and compare response style.
3. Try a prompt that should not call the tool.

Important sections:
1. Step 1: Define tool schema.
2. Step 2: Run initial request and inspect function calls.
3. Step 3: Execute tool locally and send outputs back.
4. Step 4: Continue the same state with `previous_response_id`. """

import json

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.4"
USER_PROMPT = "What's the weather in Paris today?"
FINAL_INSTRUCTIONS = "Answer concisely using the weather information."

# Step 1: Declare callable function schema.
FUNCTION_TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        },
    },
]


def get_weather(city: str) -> str:
    # Replace this stub with a real weather API integration later.
    return f"The weather in {city} is sunny with 24C."


def main() -> None:
    # Step 2: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 3: First call lets the model request tool usage.
    first_response = client.responses.create(
        model=MODEL_ID,
        tools=FUNCTION_TOOLS,
        input=USER_PROMPT,
    )

    print(f"\n<------------- First agent response with tool calls --------->\n\n{first_response.output}\n")

    # Step 4: Execute function calls locally and collect outputs.
    function_outputs = []
    for output_item in first_response.output:
        if output_item.type == "function_call" and output_item.name == "get_weather":
            call_arguments = json.loads(output_item.arguments)
            weather_text = get_weather(**call_arguments)
            function_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": output_item.call_id,
                    "output": json.dumps({"weather": weather_text}),
                }
            )

    # Step 5: Continue same response chain with previous_response_id.
    final_response = client.responses.create(
        model=MODEL_ID,
        instructions=FINAL_INSTRUCTIONS,
        tools=FUNCTION_TOOLS,
        input=function_outputs,
        previous_response_id=first_response.id,
    )
    print(f"<----------- Final agent response --------->\n\n{final_response.output_text}\n")

if __name__ == "__main__":
    main()

