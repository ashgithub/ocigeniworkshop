# Vector Store Module (`genai_client/vector_store`)

This module covers retrieval and knowledge workflows using files, vector stores, semantic search, file batches, Object Storage connectors, and NL2SQL.

Use this folder when you want to learn how to:

1. Upload and manage files for retrieval.
2. Create, inspect, update, and search vector stores.
3. Ask a model to answer with the `file_search` tool.
4. Run direct semantic search when you want retrieved chunks instead of a generated answer.
5. Batch-ingest files into a vector store.
6. Connect Object Storage to vector store ingestion.
7. Generate SQL from natural language with an existing structured semantic store.

## Beginner Map

- Files API: stores raw uploaded file objects. These files can later be attached to vector stores or sent directly to model calls.
- Vector store: indexes file content so it can be searched by meaning rather than by exact words.
- Vector store file: the relationship between one uploaded file and one vector store.
- File batch: attaches multiple uploaded files to a vector store in one ingestion job.
- `file_search` tool: lets a Responses API call retrieve relevant vector store chunks while generating an answer.
- Direct semantic search: returns matching chunks and scores directly, without asking a model to write an answer.
- Connector: links an Object Storage bucket or prefix to a vector store for ingestion.
- NL2SQL semantic store: stores database metadata so a natural-language question can be translated into SQL.

## Script Structure

The Python scripts follow the same teaching pattern as `openai_sdk/genai_client/base_client.py`:

1. A top-of-file docstring explains what the file does, reference docs, setup, how to run it, safe experiments, and important sections.
2. Configuration constants live near the top so beginners can change inputs without searching through the whole file.
3. `main()` is split with `# Step N` comments.
4. Step prints are included so terminal output maps back to the source code.
5. Cleanup or destructive operations are guarded by boolean constants where possible.

## Prerequisites

- Valid OCI/OpenAI-compatible setup in `sandbox.yaml`.
- `oci.unstructured_vector_store_id` for unstructured file retrieval examples.
- `oci.structured_vector_store_id` for the NL2SQL example.
- Existing file ids when testing attach operations with `ATTACH_FILE_ID`.
- Object Storage namespace, bucket name, and optional prefix for connector workflows.
- Database connection values in `sandbox.yaml` if you approve SQL execution in the NL2SQL script.

Run scripts from the repo root:

- `uv run openai_sdk/genai_client/vector_store/file_management.py`
- `uv run openai_sdk/genai_client/vector_store/vector_api.py`
- `uv run openai_sdk/genai_client/vector_store/vector_batch.py`
- `uv run openai_sdk/genai_client/vector_store/file_search.py`
- `uv run openai_sdk/genai_client/vector_store/semantic_store.py`
- `uv run openai_sdk/genai_client/vector_store/vector_store_connector.py`
- `uv run openai_sdk/genai_client/vector_store/nl2sql_gen_tool.py`

## Folder Contents

1. `file_management.py`
   - Demonstrates the Files API lifecycle:
   - Upload a file, list files, retrieve metadata, call the model with a file, and optionally delete the file.
   - Good first script before learning vector store attachment.

2. `vector_api.py`
   - Demonstrates vector store metadata and search operations:
   - Retrieve a vector store, update metadata, search it, list attached files, and optionally inspect one attached file.
   - Includes a commented create block for learners who want to create a fresh vector store.

3. `vector_batch.py`
   - Demonstrates batch ingestion:
   - Upload local files, create a vector store file batch, poll status, list files in the batch, and optionally clean up.
   - Good next step after `file_management.py`.

4. `file_search.py`
   - Demonstrates `responses.create(...)` with the built-in `file_search` tool.
   - Use this when you want the model to retrieve context and produce a final answer.

5. `semantic_store.py`
   - Demonstrates direct `client.vector_stores.search(...)`.
   - Use this when you want retrieved chunks, filenames, attributes, and scores without generation.

6. `vector_store_connector.py`
   - Demonstrates OCI control-plane connector APIs with REST calls:
   - Create connector, list connectors, retrieve details, update metadata, inspect stats, inspect ingestion logs, trigger a sync, and optionally delete.
   - Use this when your documents live in Object Storage.

7. `nl2sql_gen_tool.py`
   - Demonstrates NL2SQL generation with an existing structured semantic store.
   - Prints generated SQL, asks for approval, and optionally executes the SQL against the configured database.

8. `vector_store.ipynb`
   - Notebook walkthrough for interactive practice across the module topics.

## Suggested Learning Path

1. `file_management.py`
2. `vector_api.py`
3. `vector_batch.py`
4. `file_search.py`
5. `semantic_store.py`
6. `vector_store_connector.py`
7. `nl2sql_gen_tool.py`
8. `vector_store.ipynb`

## Typical Use Cases

1. Enterprise knowledge base retrieval with file grounding.
2. Search and answer flows over internal documents.
3. Scheduled ingestion from Object Storage into vector stores.
4. Analytics assistant patterns that translate natural language into SQL.

## References

- [OpenAI Files API](https://platform.openai.com/docs/api-reference/files)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [OpenAI Vector Stores API](https://platform.openai.com/docs/api-reference/vector-stores)
- [OpenAI Vector Store Files API](https://platform.openai.com/docs/api-reference/vector-stores-files)
- [OpenAI Vector Store File Batches API](https://platform.openai.com/docs/api-reference/vector-stores-file-batches)
- [OpenAI File Search Guide](https://platform.openai.com/docs/guides/tools-file-search)
