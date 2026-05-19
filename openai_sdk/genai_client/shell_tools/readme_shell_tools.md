# Shell Tool Examples

This folder contains small runnable scripts that teach the Shell Tool patterns
one file at a time. The files are organized from the simplest hosted container
flow to the more advanced local execution loop.

Run every example from the repository root:

- `uv run openai_sdk/genai_client/shell_tools/hosted_container_auto.py`
- `uv run openai_sdk/genai_client/shell_tools/hosted_container_reference.py`
- `uv run openai_sdk/genai_client/shell_tools/hosted_network_allowlist.py`
- `uv run openai_sdk/genai_client/shell_tools/hosted_artifact_generation.py`
- `uv run openai_sdk/genai_client/shell_tools/local_win_shell.py`

## Suggested Learning Order

1. `hosted_container_auto.py`
   - The shortest hosted Shell Tool example.
   - OCI provisions or reuses a hosted shell container for the request.
2. `hosted_container_reference.py`
   - Your app creates a container first.
   - The shell request uses that exact `container_id`.
3. `hosted_network_allowlist.py`
   - Hosted shell gets scoped outbound network access.
   - Only the approved domains in the allowlist are available.
4. `hosted_artifact_generation.py`
   - Hosted shell creates a file under `/mnt/data`.
   - The app lists and retrieves the file through container files.
5. `local_win_shell.py`
   - The model emits `shell_call`.
   - This app validates and runs approved local Windows PowerShell commands.
   - The app sends `shell_call_output` back so the model can continue.

## Beginner Notes

- Hosted shell examples run commands in hosted containers.
- The local Windows example runs approved commands on this machine, so review
  `GuardedPowerShell.is_allowed` before expanding the allowlist.
- Keep prompts non-destructive while learning.
- Do not place secrets, tokens, or private credentials in these example files.
