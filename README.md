## Welcome to the AI Developer learning path.

You can use this learning path with our AI sandbox. See instructions in #igiu-ai-learning slack channel.

Other resources of help:
1. [Training Video](https://oracle-my.sharepoint.com/:v:/p/ashish_ag_agarwal/EUIBQblxmdlGtxFPg6C6Vv4Byx9KZRCQWaoELwUvLMYyXw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=BC9qVl)
2. [Powerpoint](https://oracle-my.sharepoint.com/:p:/p/ashish_ag_agarwal/EW8530J_QrpTi8XIe3FMmZABjOfVlJQQkfoUqCNDxpUDQQ?e=HcViLd)

## Setup for running code locally
The examples are based on Python 3.11+. Both Python scripts and Jupyter notebooks are available. We use UV for dependency management and execution.

1. Request access to sandbox `#igiu-ai-learning`.
   - Set up API keys and DB access based on the document [here](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW).
   - Update the `sandbox.yaml` file per your environment (OCI config, compartment, DB wallet path, bucket prefix, etc.).
  
2. Note the AI sandbox gives you access to two regions:
   1. Chicago: AI services, AI Playground, and Gen AI Agents are in this region.
   2. PHX: 23 AI Database, object buckets, and compute (if available) will be in this region.
   3. Object bucket in CHI is a read-only replica, so any files you drop in PHX will show up in Chicago automatically.
   4. Same bucket is shared by all users of AI sandbox; thus, best to use your Oracle User ID as `prefix` for your objects (configure it in `sandbox.yaml`).
   5. Same schema in 23ai will be shared by all users; thus, best to use your tables with your Oracle User ID as `prefix` for table names (configure in `sandbox.yaml`).
   - For DB examples: Download the 23ai wallet, unzip locally, and update `sandbox.yaml` with path, user, service name, password (via `.env`).

3. Setup UV environment:
    - Install UV: https://docs.astral.sh/uv/getting-started/installation/
    - `uv sync` to install dependencies (`oci`, `oracledb`, `python-dotenv`, etc.) from `pyproject.toml`.
    - Run `uv run AISandboxEnvCheck.py` to verify setup.
    - To run scripts: `uv run <path/to/script>` (e.g., `uv run llm/cohere_chat.py`).
    - For notebooks: Open in Jupyter/VS Code after `uv sync`.

4. We recommend following this progressive learning path, starting with core concepts and building to advanced integrations. Each module includes Python scripts, Jupyter notebooks, and detailed readmes with run instructions, docs, and project ideas.

   **Core LLM and Agentic Basics:**
   - **llm**: Introduction to OCI Generative AI APIs using Cohere and OpenAI-compatible models (chat, streaming, structured output, history, OCI Language NLP).
   - **rag**: Retrieval-Augmented Generation with OCI Agents, document citations, and home-grown pipelines using embeddings and Oracle DB.
   - **function_calling**: Function calling (tools) for single/multi-step agentic workflows with Cohere and Llama models, including classification.

   **OCI AI Services:**
   - **speech**: Text-to-Speech (TTS) and Speech-to-Text (STT) using OCI Speech with Oracle and Whisper models.
   - **vision**: Image/video analysis with OCI Vision (object/text detection) and Document Understanding (OCR, extraction), plus multimodal LLMs.
   - **database**: AI in Oracle Autonomous Database 23ai – NL2SQL, Select AI, database-centric RAG, semantic caching.

   **Advanced: LangChain Integration (using LangChain 1.0.3):**
   - **langChain/llm**: LLM interactions with chat, history, streaming, structured output, async, reasoning via OCI GenAI.
   - **langChain/rag**: RAG with document chunking, OCI embeddings, Oracle DB vector search, AIA reranking.
   - **langChain/function_calling**: Tool calling and agents with streaming support using OCI OpenAI-compatible.
   - **langChain/agents**: Work in progress – advanced agent workflows and LangGraph examples (check readme).

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
Dependencies like `python-dotenv` are installed via `uv sync`. Load in code: `from dotenv import load_dotenv; load_dotenv()`.

## Additional Notes
- This workshop focuses on OCI GenAI library (https://github.com/oracle-samples/oci-openai) and LangChain 1.0.3.
- Keep code simple for teaching; each file has comments on purpose, docs, env, run command, key sections.
- Update module readmes as you experiment.
- For issues, use #igiu-ai-learning Slack.
