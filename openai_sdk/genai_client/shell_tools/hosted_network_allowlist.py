"""What this file does:
Demonstrates hosted Shell Tool usage with a scoped network allowlist.

Hosted shell containers should start with outbound network disabled unless a
workflow requires it. When network access is needed, use an allowlist so the
container can reach only approved domains.

Key difference:
- Disabled network: safest default for local file inspection and reports.
- Allowlist network: lets hosted shell access approved package/API domains.
- Domain secrets: add separately when approved domains need scoped credentials.

Documentation for reference:
- Shell Tool guide: https://developers.openai.com/api/docs/guides/tools-shell
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- Containers API reference: https://platform.openai.com/docs/api-reference/containers

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm hosted Shell Tool and network policy support are enabled.
- Keep `RUN_LIVE_API=False` until you are ready to allow outbound network use.

How to run from repo root:
uv run openai_sdk/genai_client/shell_tools/hosted_network_allowlist.py

Safe experiments:
1. Keep the domain list minimal.
2. Prefer package metadata/version checks over broad downloads.
3. Do not include real secrets in this file.

Important sections:
1. Step 1: Build a shell tool with `network_policy.allowlist`.
2. Step 2: Preview or run the hosted shell request.
"""

import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"

ALLOWED_NETWORK_DOMAINS = [
    "pypi.org",
    "files.pythonhosted.org",
]

PROMPT = """
Use the shell tool with the approved outbound domains.
Install the Python package `requests`, print its installed version, and explain
whether the allowlisted network workflow succeeded.
"""

def main() -> None:
    # Step 2: Send the hosted shell request with scoped network access.
    client: OpenAI = OpenAIClientProvider().oci_openai_skills_client
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {
                        "type": "allowlist",
                        "allowed_domains": ALLOWED_NETWORK_DOMAINS,
                    },
                },
            }
        ],
        input=PROMPT
    )
    print("<------------- Hosted network allowlist response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()
