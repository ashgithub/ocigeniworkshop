""" What this file does:
Demonstrates using the Langfuse OpenAI-compatible client wrapper so the
request can be traced and inspected in Langfuse.

Documentation for reference:
- Langfuse Python SDK: https://langfuse.com/docs/sdk/python/overview
- Responses API: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users
- #igiu-innovation-lab
- #igiu-ai-learning
- #genai-hosted-deployment-users

Environment setup:
- Create `.env` from `.env.example
- Set `OCI_GENAI_API_KEY` and `OCI_GENAI_PROJECT_ID`
- Configure Langfuse environment variables if tracing externally

How to run the file:
uv run python genai_client/langfuse_client.py

Safe experiments:
1. Change `USER_PROMPT` and inspect resulting traces.
2. Remove MCP tool and compare trace structure.
3. Change `MODEL_ID` to compare latency/cost.

Important sections:
1. Step 1: Build Langfuse OpenAI-compatible client.
2. Step 2: Send tool-enabled request.
3. Step 3: Print final text output. """

import httpx

# This import requires higher version of langfuse, for compatibility.
# Current repo uses 3.5.1 for compatibility.
# Try using the snippet on a different environment or upgrade lagfuse dependency
from langfuse.openai import OpenAI
from oci_genai_auth import OciUserPrincipalAuth
from envyaml import EnvYAML

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
        base_url="https://inference.generativeai.us-ashburn-1.oci.oraclecloud.com/openai/v1",
        api_key="not-used",
        project=scfg['oci']['project'],
        default_headers={
            "opc-compartment-id":scfg["oci"]["compartmentid"],
            "CompartmentId":scfg["oci"]["compartmentid"]
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
    print(response.output_text)

if __name__ == "__main__":
    main()
