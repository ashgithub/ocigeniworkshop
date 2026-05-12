# Shell Tool Examples

This folder splits Shell Tool usage into small runnable scripts. Start with:

- `uv run openai_sdk/genai_client/shell_tool.py`

Then run the focused file for the capability you want to inspect:

1. `hosted_container_auto.py`
   - OCI provisions or reuses a hosted shell container.
2. `hosted_container_reference.py`
   - Your app creates or chooses a container, then the shell request uses that exact `container_id`.
3. `hosted_network_allowlist.py`
   - Hosted shell gets scoped outbound network access for approved domains.
4. `hosted_artifact_generation.py`
   - Hosted shell creates a file under `/mnt/data`; the app lists and retrieves it through container files.
5. `local_shell_loop.py`
   - The model emits `shell_call`; the app validates and runs approved local commands, then sends `shell_call_output`.

All scripts default to preview mode with `RUN_LIVE_API=False`.
