## Welcome to the AI Developer learning path.

This learning path  is desigend to work our AI sandbox. See instructions in #igiu-ai-learning slack channel.


## Setup for running code locally
The examples are based on Python 3.13+. Both Python scripts and Jupyter notebooks are available. We use UV for dependency management and execution.

1. Request access to sandbox `#igiu-ai-learning`.
   - Set up API keys and DB access based on the document [here](https://gbuconfluence.oraclecorp.com/display/D2OPS/AISandbox#AISandbox-ToAccessADW)
   - Update the `sandbox.yaml` file per your environment (you can change the yaml file itself, or use the `.env` file. You can base it off `.example.env` ).
  
2. AI sandbox gives you access to two regions:
   1. Chicago: AI services, AI Playground, and Gen AI Agents are in this region.
   2. Phoenix: 26 AI Database, object buckets, and compute (if available) will be in this region.

3. Resources in the sandbox are shared:
   3. Object bucket in `chicago` is a read-only replica, so any files you drop in `phoenix` will show up in Chicago automatically.
   4. Same bucket is shared by all users of AI sandbox; thus, best to use your Oracle User ID as `prefix` for your objects (configure it in `sandbox.yaml`).
   5. Same schema in 26ai will be shared by all users; thus, best to use your tables with your Oracle User ID as `prefix` for table names (configure in `sandbox.yaml`).
   - For DB examples: Download the 26ai wallet, unzip locally, and update `sandbox.yaml` with path, user, service name, password (or via `.env`).

3. Setup UV environment:
    - Install UV: https://docs.astral.sh/uv/getting-started/installation/
    - `uv sync` to install dependencies (`oci`, `oracledb`, `python-dotenv`, etc.) from `pyproject.toml`.
    - Run `uv run AISandboxEnvCheck.py` to verify setup.
    - To run scripts: `uv run <path/to/script>` (e.g., `uv run langChain/llm/langchain_oci_chat.py`).
    - For notebooks: Open via  Jupyter plugin in VS Code. Note you will have to set up the `cwd` see any noteboox for instructions

4. We recommend following this progressive learning path, starting with core concepts and building to advanced integrations. Each module includes Python scripts, Jupyter notebooks, and detailed readmes with run instructions, docs, and project ideas.

   ** OCI supported LLMs via Langchain**
   - **langChain/llm**: LLM interactions with chat, history, streaming, structured output, async, reasoning via OCI GenAI.
   - **langChain/rag**: RAG with document chunking, OCI embeddings, Oracle DB vector search, AIA reranking.
   - **langChain/function_calling**:  Tool calling & MCP  using langchain.
   - **langChain/agents**: Aadvanced agent workflows with A2A & LangGraph examples 
   -**langChain/multimodal**: Vision & Speech using multimodal LLMs via langchain

   ** OCI Supported LLMs via OCI APIs :**
   - **oci_genai/llm**: Introduction to OCI Generative AI APIs using Cohere and OpenAI-compatible models (chat, streaming, structured output, history, OCI Language NLP).
   - **oci_genai/rag**: Retrieval-Augmented Generation with OCI Agents, document citations, and home-grown pipelines using embeddings and Oracle DB.
   - **oci_genai/function_calling**: Function calling (tools) for single/multi-step agentic workflows with Cohere and Llama models, including classification.

   **Other OCI AI Services:**
   - **oci_genai/speech**: Text-to-Speech (TTS) and Speech-to-Text (STT) using OCI Speech with Oracle and Whisper models.
   - **oci_genai/vision**: Image/video analysis with OCI Vision (object/text detection) and Document Understanding (OCR, extraction), plus multimodal LLMs.
   - **database**: AI in Oracle Autonomous Database 26ai – NL2SQL, Select AI, database-centric RAG, semantic caching.


   Refer to each module's readme for setup, study order, experiments, and Slack channels. Join #igiu-ai-learning for help.

5. OCI commands to manage your files in object buckets (replace `NAMESPACE`, `BUCKET`, `PREFIX` with your values from `sandbox.yaml`):
   - List objects: `oci os object list --all --fields name,timeCreated --namespace NAMESPACE --bucket-name BUCKET --prefix PREFIX`
   - Upload file: `oci os object put --namespace NAMESPACE --bucket-name BUCKET --prefix PREFIX --file your_file.txt`
   - Bulk delete: `oci os object bulk-delete --namespace NAMESPACE --bucket-name BUCKET --prefix PREFIX`

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml` (e.g., DB_PASSWORD).

Example `.env`:
```
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
```

## Additional Notes
- This workshop focuses
  -  OCI GenAI python sdk  (https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models)
  -  OCI Open AI sdk (https://github.com/oracle-samples/oci-openai)
  -  Ocacle Langchain sdk (https://github.com/oracle/langchain-oracle/tree/main)
- For issues, use #igiu-ai-learning Slack.
