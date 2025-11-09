## Welcome to the RAG (Retrieval-Augmented Generation) Module

In this module, we will experiment with the LLM's ability to answer questions using proprietary data, focusing on OCI Generative AI services.

In this module, we will explore the following capabilities:
1. Passing documents to OCI GenAI API for responses with citations.
2. Using OCI Agents for out-of-the-box RAG functionality.
3. Building a home-grown RAG solution using OCI embeddings, Oracle DB for vector storage, and Cohere models.
4. Introduction to full RAG pipeline: chunking, embedding, retrieval, augmentation, generation.

Oracle 26ai database is used in some examples; refer to [this page](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW).
- The database requires the wallet to be downloaded.
- Remember to update the database section per your setup in `sandbox.yaml`.
- As the database schema is shared, set a unique `prefix` in the database section of `sandbox.yaml`. Your Oracle user ID is a good choice.

Example code in this module is available both as Jupyter notebooks and Python scripts. They are very similar and build progressively:

## Environment Setup
- `sandbox.yaml`: Contains OCI config, compartment, DB details (if used), and wallet path. Ensure "oci" and "db" sections are configured.
- `.env`: Load environment variables (e.g., if additional keys needed).
- Use UV for environment management: `uv sync` to install dependencies.
- For DB examples: Download wallet and update paths in `sandbox.yaml`.

## Suggested Study Order and File Descriptions
Study in this order for progressive understanding:

1. **cohere_chat_citation.py, RAG-chat-citations.ipynb**: Demonstrates passing documents directly to Cohere models via OCI GenAI for chat responses with citations. No external storage needed.
   - Key features: Builds chat requests with documents, handles citations, adds chat history.
   - How to run: `uv run rag/cohere_chat_citation.py` or open notebook and run cells.
   - Experiment: Try different models (e.g., cohere.command-r-plus), adjust temperature/top_p, add more documents, or test with/without history.
   - Docs: [OCI GenAI Chat Models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm), [Cohere Documents](https://docs.cohere.com/docs/documents).

2. **oci_rag_agents.py, RAG-agents.ipynb**: Leverages OCI GenAI Agent service for ready-made RAG with a shared knowledge base.
   - Key features: Creates sessions, chats with agent endpoint, handles citations from ingested docs.
   - Setup: See rag_agents.md for uploading docs to shared knowledge base and ingesting.
   - How to run: `uv run rag/oci_rag_agents.py` or open notebook and run cells. Ensure agent endpoint in `sandbox.yaml`.
   - Experiment: Add your own PDFs (e.g., with images/charts) to knowledge base, ask domain-specific questions, compare session vs. sessionless endpoints.
   - Docs: [OCI GenAI Agents](https://docs.oracle.com/en-us/iaas/Content/generative-ai/agents.htm).

3. **cohere-rag-26ai.py, RAG-full.ipynb**: Full home-grown RAG: chunk text, embed with Cohere, store/retrieve from Oracle DB, generate with Cohere.
   - Key features: Manual chunking, DB vector storage, cosine similarity search, augment prompt with retrieved chunks, citations via documents.
   - How to run: `uv run rag/cohere-rag-26ai.py` or open notebook and run cells. Requires DB setup.
   - Experiment: Try different chunk sizes/overlap, similarity metrics (COSINE/DOT/EUCLIDEAN), add reranking (see cohere docs), use real PDFs instead of mock chunks.
   - Docs: [OCI Embeddings](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm#embed-models), [Oracle Vector Search](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/).

Note: For production, consider libraries like LangChain for easier chunking/retrieval (see langChain/rag/ examples). rag_agents.md provides detailed setup for OCI Agents knowledge base.

## Project Ideas
Here are ideas to extend these examples:

1. Build a "talk-to-document" app:
   - Upload/parse/chunk real docs (PDFs/text).
   - Experiment with chunking strategies (fixed-size vs. semantic).
   - Add reranking for better retrieval.
   - Include UI (e.g., Streamlit) for interactive chat.
   - Resources: [Cohere Rerank](https://docs.cohere.com/docs/rerank), [LangChain Chunking](https://docs.langchain.com/oss/python/langchain/splitting).

2. Hybrid RAG with Agents:
   - Combine home-grown retrieval with OCI Agents for complex queries.
   - Test on domain docs (e.g., technical manuals) and evaluate citations.

3. Optimize Retrieval:
   - Implement caching for embeddings.
   - Compare models (e.g., multilingual vs. English embeddings).
   - Add filters (e.g., distance threshold < 0.5).

## Resources and Links
- **Documentation**:
  - [OCI GenAI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [Cohere Models on OCI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm)
  - [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas.
  - **#igiu-ai-learning**: Issues with environment/code.
  - **#generative-ai-users**: OCI GenAI questions.
  - **#igiu-ai-accelerator-collab**: Advanced RAG toolkit discussions.
