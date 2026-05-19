""" What this file does:
Demonstrates hosted Shell Tool usage with a scoped network allowlist.

Hosted shell containers should start with outbound network disabled unless a
workflow requires it. When network access is needed, use an allowlist so the
container can reach only approved domains.

Beginner mental model:
- Hosted shell network access starts from a deny-by-default posture.
- The allowlist below names the only domains this request may reach.
- The prompt should match the approved domains and avoid broad downloads.

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
- Run this only from a sandbox or approved learning environment.

How to run from repo root:
uv run openai_sdk/genai_client/shell_tools/hosted_network_allowlist.py

Safe experiments:
1. Keep the domain list minimal.
2. Prefer package metadata/version checks over broad downloads.
3. Do not include real secrets in this file.

Important sections:
1. Constants: choose approved domains and the network-aware prompt.
2. Step 1: Build a configured OpenAI client.
3. Step 2: Send the hosted shell request with `network_policy.allowlist`.
"""

import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"

# Only these domains are available to the hosted shell during this request.
ALLOWED_NETWORK_DOMAINS = [
    "pypi.org",
    "files.pythonhosted.org",
]

# The prompt intentionally uses a small package install so beginners can see
# how an allowlisted network workflow behaves without broad internet access.
PROMPT = """
Use the shell tool with the approved outbound domains.
Install the Python package `requests`, print its installed version, and explain
whether the allowlisted network workflow succeeded.
"""

def main() -> None:
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client
    print(
        "Step 1/2: Allowing hosted shell network access to: "
        f"{', '.join(ALLOWED_NETWORK_DOMAINS)}"
    )

    # Step 2: Send the hosted shell request with scoped network access.
    print("Step 2/2: Sending hosted shell request with network allowlist...")
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
