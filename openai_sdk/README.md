# OpenAI SDK (OCI Sandbox)

This folder contains OpenAI SDK and Agents SDK examples configured for OCI Generative AI.

## Config Source

`openai_client_provider.py` now loads settings from `sandbox.yaml` (YAML-first), with env fallback for compatibility.

Expected YAML keys:

- `oci.profile`
- `oci.compartment`
- `oci.conversation_store` (optional but recommended)
- `openai.service_endpoint` (optional, defaults to OCI `/openai/v1` endpoint)
- `openai.api_key` (optional, defaults to `OCI`)
- `openai.project` (optional)
- `openai.profile` / `openai.compartment` / `openai.conversation_store` (optional overrides)

Env fallback keys (if YAML values are missing):

- `OPENAI_SERVICE_ENDPOINT`
- `OPENAI_API_KEY` or `OCI_AI_API_KEY`
- `OCI_OPENAI_PROJECT`
- `OCI_PROFILE`
- `OCI_COMPARTMENT_ID` or `OCI_COMPARTMENT_OCID`
- `OCI_CONVERSATION_STORE_ID` or `OCI_CONVERSATION_STORE`

## Run Examples

From repo root:

```bash
uv run python -m openai_sdk.agent_sdk.simple_agent
uv run python -m openai_sdk.genai_client.base_client
```

## Notes

- The provider keeps existing usage unchanged: `OpenAIClientProvider().oci_openai_client`.
- If required keys are missing, it raises `SandBoxConfigKeyNotSetException` with the missing key names.
