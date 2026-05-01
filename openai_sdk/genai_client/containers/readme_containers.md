# Containers Module (`genai_client/containers`)

This module introduces **container resources** and **container file operations** using the OpenAI-compatible client configured through OCI.

Use this folder when you want to learn how to:

1. Create, list, retrieve, and delete containers.
2. Upload files into a container and inspect their metadata/content.
3. Build confidence with the container lifecycle before using advanced tools that depend on containers.

## Prerequisites

- Valid OCI/OpenAI-compatible setup in `sandbox.yaml`.
- Access to a project/compartment with permissions for container operations.
- If you run `container_files.py`, provide:
  - A valid `container_id`.
  - A local sample file (`data.csv` in the sample, or your own path).
  - A valid `file_id` for retrieve/content/delete calls.

Run scripts from repo root:

- `uv run openai_sdk/genai_client/containers/base_example.py`
- `uv run openai_sdk/genai_client/containers/container_files.py`

## Folder Contents

1. `base_example.py`
   - Demonstrates the base container lifecycle:
     - `client.containers.create(...)`
     - `client.containers.list()`
     - `client.containers.retrieve(...)`
     - `client.containers.delete(...)`
   - Best first file for understanding container resources.

2. `container_files.py`
   - Demonstrates file lifecycle inside a container:
     - Upload file to a container.
     - List container files.
     - Retrieve file metadata.
     - Retrieve file content stream.
     - Delete a file from the container.
   - Good follow-up once `base_example.py` is clear.

3. `containers.ipynb`
   - Notebook version of container examples for interactive learning and step-by-step experiments.

## Suggested Learning Path

1. Start with `base_example.py` and run each operation one by one.
2. Move to `container_files.py` to practice file upload and retrieval.
3. Use `containers.ipynb` to iterate with your own IDs and sample files.

## Typical Use Cases

1. Preparing a reusable workspace for code-interpreter style workflows.
2. Managing data files that should be attached to an execution environment.
3. Testing API behavior for create/retrieve/delete operations before production integration.

## References

- [OpenAI Containers API](https://platform.openai.com/docs/api-reference/containers)
- [OpenAI Container Files API](https://platform.openai.com/docs/api-reference/container-files)
