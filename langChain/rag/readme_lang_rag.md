## Welcome to the LangChain RAG (Retrieval-Augmented Generation) Module

In this module, we will experiment with the LLM's ability to answer questions using proprietary data.

In this module, we will explore the following capabilities:
1. Use community document loaders to generate text chunks from files.
2. Integration of OCI Generative AI embedding models for fast embedding from text chunks.
3. Semantic search using Oracle DB as a knowledge base for retrieval.
4. Full RAG example integrating OCI Gen AI for embeddings and LLM to answer user queries.


Oracle AI database is used in this module. Refer to [this page](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW).
- The database requires the wallet to be downloaded.
- Remember to update the database section per your setup in `sandbox.yaml`.
- As the database schema is shared, set a unique `prefix` in the database section of `sandbox.yaml`. Your Oracle user ID is a good choice.

## Environment Setup
- `sandbox.yaml`: Contains OCI config, compartment, DB details, and wallet path.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to Oracle 23 AI DB and OCI Generative AI services.

## Suggested Study Order and File Descriptions
The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **langchain_chunks.py**: Demonstrates loading and chunking documents using LangChain text splitters. Learn how to break down PDFs into manageable text chunks for further processing.
   - Key features: Uses PyPDFLoader and RecursiveCharacterTextSplitter; shows chunk previews with metadata.
   - How to run: `uv run langChain/rag/langchain_chunks.py`.
   - Docs: [LangChain Document Loaders](https://docs.langchain.com/oss/python/langchain/knowledge-base#1-documents-and-document-loaders), [Text Splitters](https://docs.langchain.com/oss/python/integrations/splitters).

2. **langchain_embedding.py**: Demonstrates embedding generation using OCI Generative AI for chunks from a PDF document. Explore how to convert text into vectors for similarity searches.
   - Key features: Direct OCI SDK for embeddings (LangChain mode commented for reference); displays embedding dimensions and metadata.
   - How to run: `uv run langChain/rag/langchain_embedding.py`.
   - Docs: [OCI Gen AI Embeddings](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm#embed-models), [LangChain Embeddings](https://docs.langchain.com/oss/python/langchain/knowledge-base#embeddings).

3. **langchain_semantic_search.py**: Demonstrates a semantic search example using OCI Generative AI for embeddings and Oracle DB for vector storage and retrieval. Perform vector similarity searches over stored embeddings.
   - Key features: Embeds queries, stores chunks in Oracle DB, retrieves top results using cosine similarity.
   - How to run: `uv run langChain/rag/langchain_semantic_search.py`.
   - Docs: [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/), [OCI GenAI SDK](https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models).

4. **langchain_rag_23ai.py**: Demonstrates a full RAG (Retrieval-Augmented Generation) example using OCI Generative AI for embeddings and LLM, with Oracle DB for vector storage and semantic search.
   - Key features: Embeds documents, stores in DB, retrieves context, generates answers via LLM with citations.
   - How to run: `uv run langChain/rag/langchain_rag_23ai.py`.
   - Docs: [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai), [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview).

## Project Ideas
Here are some ideas for projects you can build upon these examples:

1. Create a "talk to my document" application:
   - Allow users to upload documents.
   - Parse and chunk documents using various strategies (e.g., semantic chunking – search for libraries like `langchain_experimental` for advanced splitters).
   - Experiment with similarity algorithms (COSINE is popular, but try Euclidean or DOT product).
   - Add rerankers (e.g., using Cohere or cross-encoders) to reorder retrieved documents.
   - Include citations in responses for transparency.
   - Resources: [Semantic Chunking Guide](https://docs.langchain.com/docs/guides/semantic-chunking), [Reranking Techniques](https://www.sbert.net/docs/pretrained-models/ce-msmarco.html).

2. Build a chatbot with custom knowledge base:
   - Extend the RAG example to handle multiple document types (e.g., PDFs, text files).
   - Implement conversation history using LangChain's memory modules.
   - Add evaluation metrics (e.g., BLEU or ROUGE) to assess answer quality.
   - Resources: [LangChain Memory](https://docs.langchain.com/oss/python/langchain/memory), [Chatbot Evaluation](https://huggingface.co/docs/evaluate/main/en/tasks/question_answering).

3. Optimize for production:
   - Implement caching for embeddings to avoid recomputation.
   - Use streaming for LLM responses in the RAG pipeline.
   - Integrate with a web UI (e.g., Streamlit or Gradio).
   - Resources: [LangChain Caching](https://docs.langchain.com/oss/python/langchain/caching), [Streamlit Docs](https://docs.streamlit.io/).

## Resources and Links
- **Documentation**:
  - [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)
  - [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)
  - [OCI Python SDK](https://github.com/oracle/oci-python-sdk)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#generative-ai-users**: Questions about OCI Gen AI.
  - **#adb-select-ai-users**: Questions about Select AI.
  - **#ww-autonomous-int**: Questions about Oracle Autonomous Database.
