# Memory Module (`genai_client/memory`)

This module demonstrates **conversation memory patterns** with the OpenAI-compatible API on OCI.

Use this folder when you want to learn how to:

1. Associate multiple conversations with one logical user (`memory_subject_id`).
2. Control memory behavior using access policies (`store_only`, `recall_only`).
3. Configure short-term memory optimization metadata.

## Prerequisites

- Valid OCI/OpenAI-compatible setup in `sandbox.yaml`.
- Permission to create conversations and responses.
- Keep your test `memory_subject_id` consistent across related runs.

Run scripts from repo root:

- `uv run openai_sdk/genai_client/memory/memory_subject.py`
- `uv run openai_sdk/genai_client/memory/memory_access.py`
- `uv run openai_sdk/genai_client/memory/memory_optimization.py`

## Folder Contents

1. `memory_subject.py`
   - Demonstrates memory carryover across two conversations sharing one `memory_subject_id`.
   - Flow:
     - Conversation A stores user preferences.
     - Conversation B asks a recall question.
   - Includes a delay (`time.sleep`) to allow memory indexing.

2. `memory_access.py`
   - Demonstrates explicit memory access policy control.
   - Flow:
     - Conversation A uses `memory_access_policy="store_only"`.
     - Conversation B uses `memory_access_policy="recall_only"`.
   - Useful to test policy-driven behavior isolation.

3. `memory_optimization.py`
   - Demonstrates conversation metadata for short-term memory optimization.
   - Shows how to create a conversation with:
     - `short_term_memory_optimization`
     - Initial conversation items.

4. `memory.ipynb`
   - Notebook walkthrough to test memory configurations interactively.

## Suggested Learning Path

1. Start with `memory_subject.py` for baseline memory behavior.
2. Continue with `memory_access.py` to understand policy controls.
3. Finish with `memory_optimization.py` for metadata-based tuning.
4. Use `memory.ipynb` for iterative experiments.

## Typical Use Cases

1. Personalization across independent sessions for the same end user.
2. Restricting memory writes or reads in specific workflow stages.
3. Optimizing conversation handling for short, fast interactions.

## References

- [OpenAI Conversations API](https://platform.openai.com/docs/api-reference/conversations)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
