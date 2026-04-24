import httpx
from oci_genai_auth import OciUserPrincipalAuth
from openai import OpenAI

# Learning goal:
# Explore Vector Store API operations with an OCI-authenticated OpenAI client.
#
# How to run:
# uv run python genai_client/vector_store/vector_store.py
#
# Safe experiments for students:
# 1. Uncomment create/update/delete sections in a test project only.
# 2. Lower list limits and inspect pagination behavior.
# 3. Move secrets/OCIDs into environment variables before sharing.
#
# Note:
# This file contains hard-coded IDs/profile values for local learning.
# Replace them with environment variables before releasing publicly.

PROFILE_NAME = "API-USER"
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga"
PROJECT_ID = "ocid1.generativeaiproject.oc1.us-chicago-1.amaaaaaaghwivzaaweu6y7r5yms24upipxxrhyfw6hqllhqpzc5756f5bmtq"
BASE_URL = "https://generativeai.us-chicago-1.oci.oraclecloud.com/20231130/openai/v1"


def build_vector_store_client() -> OpenAI:
    return OpenAI(
        base_url=BASE_URL,
        api_key="not-used",
        project=PROJECT_ID,
        http_client=httpx.Client(auth=OciUserPrincipalAuth(profile_name=PROFILE_NAME)),
        default_headers={"opc-compartment-id": COMPARTMENT_ID},
    )


def main() -> None:
    # Step 1: Build OCI-authenticated client.
    vector_client = build_vector_store_client()

    # Step 2: List existing vector stores.
    list_result = vector_client.vector_stores.list(limit=20, order="desc")
    print(list_result)

    # Step 3: Optional sections below for create/retrieve/update/delete/search.
    # Keep them commented unless you are testing in a safe environment.


if __name__ == "__main__":
    main()
