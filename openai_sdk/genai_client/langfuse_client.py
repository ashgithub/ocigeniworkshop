""" What this file does:
Demonstrates using the Langfuse OpenAI-compatible client wrapper so the
request can be traced and inspected in Langfuse.

Documentation for reference:
- OpenAI langfuse integration and observability: https://langfuse.com/integrations/model-providers/openai-py
- Langfuse Python SDK reference: https://python.reference.langfuse.com/langfuse
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Responses API: https://platform.openai.com/docs/api-reference/responses
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution
- #genai-hosted-deployment-users: GA deployment and integration updates

Environment setup:
- Create a .env file from the base on .example.env
- Set up credentials on langfuse API keys from the reference to connect to observability host
- Set the `.env` variables LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY. IMPORTANT set keys to have automatic traces
- Set up the credentials for OCI over the `sandbox.yaml file`
    - Make sure to set up a project ID from the console, consult the GenAI platform GA docs for guidance
    - Set up the right profile name over the config file

How to run the file:
uv run openai_sdk/genai_client/langfuse_client.py

Safe experiments:
1. Change `USER_PROMPT` and inspect resulting traces.
2. Remove MCP tool and compare trace structure.
3. Change `MODEL_ID` to compare latency/cost.

Important sections:
1. Step 1: Build Langfuse OpenAI-compatible client.
2. Step 2: Send tool-enabled request.
3. Step 3: Print final text output. """

import httpx

from langfuse.openai import OpenAI
from oci_genai_auth import OciUserPrincipalAuth
from envyaml import EnvYAML
from dotenv import load_dotenv
load_dotenv()

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Summarize the langfuse/langfuse-python repo in 3 sentences"
DEFAULT_SANDBOX_CONFIG = "sandbox.yaml"

def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def main() -> None:
    # Step 1: load the config files
    scfg = load_config(DEFAULT_SANDBOX_CONFIG)

    # Step 1: Build Langfuse OpenAI-compatible client.
    client = OpenAI(
        base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",
        api_key="not-used",
        project=scfg['oci']['project'],
        default_headers={
            "OpenAI-Project": scfg["oci"]["project"],
        },
        http_client=httpx.Client(
            auth=OciUserPrincipalAuth(profile_name=scfg["oci"]["profile"])
        ),
    )

    # Step 2: Send request with MCP tool enabled.
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type": "mcp",
                "server_label": "dmcp",
                "server_url": "https://mcp.deepwiki.com/mcp",
                "require_approval": "never",
            },
        ],
        input=USER_PROMPT,
    )

    # Step 3: Print final text output.
    print("Final traced response:")
    print(response.output_text)

if __name__ == "__main__":
    main()
