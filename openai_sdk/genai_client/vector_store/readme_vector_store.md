# Vector Store Module (`genai_client/vector_store`)

This module covers **retrieval and knowledge workflows** using files, vector stores, semantic search, batches, connectors, and NL2SQL.

Use this folder when you want to learn how to:

1. Upload and manage files for retrieval.
2. Create and manage vector stores and attached files.
3. Execute search with `file_search` and direct semantic APIs.
4. Run batch ingestion and connector-based ingestion flows.
5. Generate SQL from natural language with semantic store operations.

## Prerequisites

- Valid OCI/OpenAI-compatible setup in `sandbox.yaml`.
- For vector store scripts:
  - Existing `VECTOR_STORE_ID` where required.
  - Existing `file_id` values for attach/batch operations where required.
- For connector workflows:
  - Valid Object Storage namespace/bucket settings.
- For NL2SQL workflow:
  - Semantic store identifiers and connection IDs where required.

Run scripts from repo root:

- `uv run openai_sdk/genai_client/vector_store/file_management.py`
- `uv run openai_sdk/genai_client/vector_store/vector_api.py`
- `uv run openai_sdk/genai_client/vector_store/vector_batch.py`
- `uv run openai_sdk/genai_client/vector_store/file_search.py`
- `uv run openai_sdk/genai_client/vector_store/semantic_store.py`
- `uv run openai_sdk/genai_client/vector_store/vector_store_connector.py`
- `uv run openai_sdk/genai_client/vector_store/nl2sql_tool.py`

## Folder Contents

1. `file_management.py`
   - File API lifecycle for retrieval workflows:
     - Upload, list, retrieve metadata, retrieve content, optional delete.
   - Good starting point before vector store attachment.

2. `vector_api.py`
   - End-to-end vector store lifecycle:
     - Create, retrieve, update, semantic search.
     - Optional file attach/list/retrieve/content.
     - Optional vector store deletion.

3. `vector_batch.py`
   - Vector store file batch operations:
     - Create batch with multiple file IDs.
     - Retrieve batch status.
     - List files in a batch.
     - Optional cancel.

4. `file_search.py`
   - `responses.create(...)` with the built-in `file_search` tool.
   - Shows how to query a vector store during generation.

5. `semantic_store.py`
   - Direct semantic search call via `client.vector_stores.search(...)`.
   - Useful when you want retrieval results directly, outside normal generation flow.

6. `vector_store_connector.py`
   - OCI control-plane connector lifecycle:
     - Create connector from Object Storage.
     - List, retrieve, stats, ingestion logs.
     - Optional delete.

7. `nl2sql_tool.py`
   - Semantic store and NL2SQL workflow:
     - Optional semantic store creation.
     - Validate semantic store.
     - Generate SQL from natural language via inference API.

8. `vector_store.ipynb`
   - Notebook walkthrough for interactive practice across the module topics.

## Suggested Learning Path

1. `file_management.py`
2. `vector_api.py`
3. `vector_batch.py`
4. `file_search.py`
5. `semantic_store.py`
6. `vector_store_connector.py`
7. `nl2sql_tool.py`
8. `vector_store.ipynb`

## Typical Use Cases

1. Enterprise knowledge base retrieval with file grounding.
2. Search and answer flows over internal documents.
3. Scheduled ingestion from Object Storage into vector stores.
4. Analytics assistant patterns that translate natural language into SQL.

## References

- [OpenAI Files API](https://platform.openai.com/docs/api-reference/files)
- [OpenAI Vector Stores API](https://platform.openai.com/docs/api-reference/vector-stores)
- [OpenAI Vector Store Files API](https://platform.openai.com/docs/api-reference/vector-stores-files)
- [OpenAI Vector Store File Batches API](https://platform.openai.com/docs/api-reference/vector-stores-file-batches)
- [OpenAI File Search Guide](https://platform.openai.com/docs/guides/tools-file-search)
