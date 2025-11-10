"""
What this file does:
Demonstrates reranking using AIA services with Cohere models.

Disclaimer: Reranking requires:
1. AIA client to be installed : aia_common_sdk-1.2b44-py3-none-any.whl or newer
2. Access to AIA services : client code /secret to be requested from AIA team 
3. The access is to dev DAC, thus you need to be on corporate VPN
4 Note: this code stores the secret in OCI vault

Documentation to reference:
- AIA Rerank Service Details: https://gbuconfluence.oraclecorp.com/display/AIAcc/Technical+Design+-+AIA+Services+APIs#:~:text=%7D-,AIA%20Service%20Endpoints%20Details,-Service
- AIA SDK: https://artifactory.oci.oraclecorp.com/igiu-aia-dev-pypi-local/aia-common/
- Cohere Reranking: https://docs.cohere.com/docs/rerank

Relevant slack channels:
 - #igiu-innovation-lab: general discussions on your project 
 - #igiu-ai-learning: help with sandbox environment or help with running this code 
 - #igiu-ai-accelerator-collab:  AIA collaboration channel 

Env setup:
- Requires AIA client installation and VPN for AIA services.

How to run the file:
uv run langChain/rag/aia_rerank.py

Comments to important sections of file:
- Step 1: Load config and set up authentication.
- Step 2: Prepare payload for reranking request.
- Step 3: Send request and display results.
"""

import os
from dotenv import load_dotenv
from envyaml import EnvYAML
from aia_common.authentication.idcs_provider import IDCSTokenProvider
from aia_common.secrets_helper import OCISecretsHelper, OCIAuthConfig

import requests

# Reference: https://docs.cohere.com/docs/rerank

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

# Step 1: Load config and set up authentication
scfg = load_config(SANDBOX_CONFIG_FILE)
auth_config = {"auth_type": "API_KEY", "auth_profile": scfg["oci"]["profile"]}
executor_token_config = scfg["aia"]

# get the secret from vault, 
oci_secrets_helper = OCISecretsHelper(OCIAuthConfig(**auth_config))

idcs_url = executor_token_config["idcs_url"]
client_id = executor_token_config["client_id"]
client_secret = oci_secrets_helper.get_secret(executor_token_config["client_secret"])
auth_scope = executor_token_config["auth_scope"]

token_provider = IDCSTokenProvider(idcs_url, client_id, client_secret, auth_scope)
headers = token_provider.auth_header()

print(headers)

# Step 2: Prepare payload for reranking request
url = " https://puo3dsaj7csiorw4sylcndmjbe.apigateway.us-phoenix-1.oci.customer-oci.com/api/v1/aia/eceu/dac/reranker"
model_id = "cohere.rerank-v3.5"

payload = {
    "pipelineId": "Innovation Lab",
    "appId": "ai-first",
    "modelId": model_id,
    "data": {
        "query": "What is the capital city of the United States of America?",
        "documents": [
            "Washington, D.C. is the capital of the United States. It serves as the seat of the federal government and is located on the Potomac River.",
            "Title: Facts about Carson City\nContent: |\n Carson City is the capital city of the American state of Nevada. At the 2010 United States Census, Carson City had a population of 55,274.\n",
            "Title: The Commonwealth of Northern Mariana Islands\nContent: |\n The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean that are a political division controlled by the United States. Its capital is Saipan.\n",
            "The capital of the US is washington",
            "New York City is often referred to as the economic capital of the world, but it is not the political capital of the United States.",
            "Paris is the capital of France, known for its art, fashion, and culture.",
            "The United States has 50 states, and each state has its own capital city, such as Austin for Texas or Sacramento for California.",
        ],
        "topN": 3,
        "maxChunksPerDocument": 1,
        "isEcho": True,
    },
}

# Step 3: Send request and display results
resp = requests.post(url, json=payload, headers=headers, timeout=120)

print(resp.json()["document_ranks"])
print(resp.json()["document_ranks"][0])
