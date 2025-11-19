## Welcome to the Database Module

In this module, we will explore how Oracle Autonomous Database (23ai) and **Select AI** enable Large Language Model (LLM) workflows directly inside the database and how to combine them with Retrieval-Augmented Generation (RAG).

## What you will learn

In this module, we will explore the following capabilities:

1. **Natural-Language-to-SQL (NL2SQL)** – Ask questions in plain English and let the database generate and execute the SQL for you.
2. **Select AI** – Compare "inline LLM" SQL (`SELECT AI …`) with external LLM calls.
3. **Database-centric RAG** – Use SQL and Embeddings stored in the database to build a full RAG pipeline that returns citations.
4. **Semantic Caching** – Cache answers and retrieve them based on similar questions using vector embeddings.

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment, DB details, and wallet path.
- `.env`: Load environment variables (e.g., API keys if needed).
- Download the **ADB / 23ai wallet** and unzip it locally.
- Populate the `db` section in `sandbox.yaml` (wallet directory, user, password, service name, prefix).
- Verify `oci` section is complete (needed for embedding generation).
- Ensure you have access to Oracle Autonomous Database 23ai.

## Suggested Study Order and File Descriptions

The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **nl2sql_demo.py**: Demonstrates Natural-Language-to-SQL (NL2SQL) conversion using OCI Generative AI. It translates plain English questions into SQL queries that execute against the SH (Sales History) schema in Oracle Database, displaying results in a formatted table.
   - Key features: Uses few-shot prompting with schema description; handles database connections and error handling.
   - How to run: `uv run database/nl2sql_demo.py`.

2. **llm_semantic_cache.py**: Demonstrates semantic caching using OCI Generative AI embeddings and Oracle Database vector search. It stores Q&A pairs as embeddings and retrieves semantically similar answers for user queries, reducing the need for repeated LLM calls.
   - Key features: Embeds Q&A pairs, stores in DB, performs semantic search with cosine similarity.
   - How to run: `uv run database/llm_semantic_cache.py`.

3. **semantic_cache.ipynb**: A Jupyter notebook variation of the llm_semantic_cache.py script, demonstrating semantic caching with step-by-step markdown explanations and interactive cells.
   - Key features: Mirrors the Python script; includes detailed steps and experimentation suggestions; embeds Q&A pairs, stores in DB, retrieves semantically similar answers.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.

4. **selectai.sql**: Pure Select AI examples demonstrating "inline LLM" SQL capabilities directly in the database.
   - Key features: Shows various SELECT AI queries for natural language database interactions.
   - How to run: Execute in SQL client connected to 23ai database.
   - Docs: [Select AI Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/select-ai.html)

5. **selectai_demo.py**: Demonstrates Oracle SELECT AI functionality using the Python select-ai library. It showcases various Profile methods (narrate, show_sql, explain_sql, run_sql, chat, generate, get_attributes, list) with examples adapted for the WORKSHOP_ADMIN.STUDENTS table, providing a comprehensive Python alternative to SQL-based SELECT AI queries.
   - Key features: Demonstrates all major Profile methods programmatically; includes comprehensive examples and interactive query loop.
   - How to run: `uv run database/selectai_demo.py`.

6. **rag.sql**: Full RAG implementation in 23ai using embeddings, similarity search, and citations.
   - Key features: Demonstrates database-centric RAG with vector operations and LLM integration.
   - How to run: Execute in SQL client connected to 23ai database.
   - Docs: [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/overview-ai-vector-search.html).

## Project Ideas

Here are some ideas for projects you can build upon these examples:

1. **Build a "Chat with my tables" application**:
   - Implement automatic schema discovery for any database.
   - Use NL2SQL for structured Q&A on tabular data.
   - Add GenAI summarization for query results.

2. **Create an in-database semantic search view**:
   - Store vector embeddings in 23ai with proper indexing.
   - Build views that combine similarity search with traditional SQL filtering.
   - Connect to OCI GenAI for answer generation with citations.
   - Resources: [Vector Indexes in Oracle](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/create-vector-indexes-and-hybrid-vector-indexes.html).

3. **Compare Select AI vs external LLM performance**:
   - Benchmark latency and cost for the same NL queries.
   - Implement hybrid approaches that use both inline and external LLMs.
   - Analyze accuracy differences between approaches.

4. **Advanced semantic caching system**:
   - Implement cache expiration and LRU eviction policies.
   - Add multi-tenant support with user-specific caches.
   - Integrate with existing RAG pipelines for performance optimization.

## Resources and Links

- **Documentation**:
  - [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [Oracle Autonomous Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
  - [Select AI](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/select-ai.html)
  - [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/overview-ai-vector-search.html)
  - [Python-oracledb](https://python-oracledb.readthedocs.io/)
  - [SelectAi python](https://github.com/oracle/python-select-ai)

- **Slack Channels**:
  - **#generative-ai-users**: Questions about OCI Gen AI.
  - **#adb-select-ai-users**: Questions on Select AI.
  - **#ww-autonomous-int**: Questions about Oracle Autonomous Database.
  - **#igiu-innovation-lab**: General discussions on your project.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
