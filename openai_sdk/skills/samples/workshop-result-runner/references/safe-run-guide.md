# Safe Run Guide

The runner script is intentionally local-only. It reads repo files, counts examples, and prints suggested commands. It does not call OCI, databases, hosted containers, or external APIs.

## Safe by Default

- Safe: scanning READMEs, Python scripts, notebooks, and sample skill folders.
- Safe: printing `uv run ...` commands for the user to try.
- Needs care: running AI, database, object storage, or hosted skill examples.
- Needs setup: `sandbox.yaml`, `.env`, OCI config, database wallets, and project/compartment values.

## Before Live Runs

1. Check `README.md` and the module README.
2. Run `uv run AISandboxEnvCheck.py`.
3. Confirm the command writes only expected local files or sandbox resources.
4. Tell the user when a command may use cloud quota, shared buckets, database schemas, or hosted resources.

## Good First Results

Use the report to answer:

- Which module has the best docs for this topic?
- Which scripts and notebooks exist?
- Which commands are likely safe to try first?
- Which setup items block deeper execution?
