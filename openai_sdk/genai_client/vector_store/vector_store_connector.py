"""Vector store connector sample (OCI control-plane API).

This sample still uses connector APIs from the OCI Python SDK, but it reads
profile/compartment defaults from `OpenAIClientProvider` so auth and keys come
from `sandbox.yaml`.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_store_connector.py

Required environment variables:
- VECTOR_STORE_ID: target vector store id
- VECTOR_OS_NAMESPACE: object storage namespace
- VECTOR_OS_BUCKET: object storage bucket name

Optional environment variables:
- VECTOR_OS_PREFIXES: comma-separated prefixes (empty means full bucket)
- VECTOR_CONNECTOR_DISPLAY_NAME
- VECTOR_CONNECTOR_DESCRIPTION
- VECTOR_CONNECTOR_DELETE_AT_END: true/false
"""

from __future__ import annotations

import os

import oci

try:
    from .vector_genai_client import as_bool, get_env, print_section, require_env
except ImportError:
    from vector_genai_client import as_bool, get_env, print_section, require_env

# Ensure we use sandbox.yaml-backed settings.
from openai_sdk.openai_client_provider import OpenAIClientProvider


def _build_oci_genai_client() -> tuple[oci.generative_ai.GenerativeAiClient, str]:
    provider = OpenAIClientProvider()
    config_path = provider.scfg["oci"].get("configFile", "~/.oci/config")
    profile = provider.oci_openai_profile
    compartment_id = provider.oci_compartment_id

    config = oci.config.from_file(os.path.expanduser(config_path), profile_name=profile)
    token_path = os.path.expanduser(config["security_token_file"])

    with open(token_path, encoding="utf-8") as token_file:
        token = token_file.read()

    private_key = oci.signer.load_private_key_from_file(os.path.expanduser(config["key_file"]))
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key)

    region = config.get("region", "us-chicago-1")
    endpoint = f"https://generativeai.{region}.oci.oraclecloud.com"

    client = oci.generative_ai.GenerativeAiClient(
        config=config,
        signer=signer,
        service_endpoint=endpoint,
    )
    return client, compartment_id


def _parse_prefixes(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def main() -> None:
    client, compartment_id = _build_oci_genai_client()

    vector_store_id = require_env("VECTOR_STORE_ID")
    namespace = require_env("VECTOR_OS_NAMESPACE")
    bucket_name = require_env("VECTOR_OS_BUCKET")
    prefixes = _parse_prefixes(get_env("VECTOR_OS_PREFIXES"))
    display_name = get_env("VECTOR_CONNECTOR_DISPLAY_NAME", "workshop-vector-connector")
    description = get_env(
        "VECTOR_CONNECTOR_DESCRIPTION",
        "Connector sample created by vector_store_connector.py",
    )

    print_section("Create Connector")
    details = oci.generative_ai.models.CreateVectorStoreConnectorDetails(
        compartment_id=compartment_id,
        vector_store_id=vector_store_id,
        display_name=display_name,
        description=description,
        configuration=oci.generative_ai.models.OciObjectStorageConfiguration(
            storage_config_list=[
                oci.generative_ai.models.ObjectStorageConfig(
                    namespace=namespace,
                    bucket_name=bucket_name,
                    prefix_list=prefixes,
                )
            ]
        ),
        schedule_config=oci.generative_ai.models.ScheduleIntervalConfig(
            config_type="INTERVAL",
            frequency="DAILY",
            interval=1,
            state="ENABLED",
        ),
    )
    create_response = client.create_vector_store_connector(details)
    connector = create_response.data
    connector_id = connector.id
    print(f"Connector created: {connector_id} ({connector.lifecycle_state})")

    print_section("List Connectors")
    connectors = client.list_vector_store_connectors(compartment_id=compartment_id).data.items
    print(f"Total connectors: {len(connectors)}")

    print_section("Get Connector")
    fetched = client.get_vector_store_connector(connector_id).data
    print(fetched)

    print_section("Get Connector Stats")
    stats = client.get_vector_store_connector_stats(connector_id).data
    print(stats)

    print_section("List Ingestion Logs")
    logs = client.list_vector_store_connector_ingestion_logs(connector_id, limit=10).data.items
    print(f"Returned log entries: {len(logs)}")

    if as_bool("VECTOR_CONNECTOR_DELETE_AT_END", default=False):
        print_section("Delete Connector")
        client.delete_vector_store_connector(connector_id)
        print(f"Delete request sent for {connector_id}")
    else:
        print("Skipping delete. Set VECTOR_CONNECTOR_DELETE_AT_END=true to delete connector.")


if __name__ == "__main__":
    main()
