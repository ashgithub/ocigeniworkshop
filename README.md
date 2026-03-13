# OCI AI Developer Learning Path

This repository is a structured, hands-on learning path for Python developers who want to explore OCI AI services, LangChain, Oracle Database 23ai/26ai, and related multimodal and agentic workflows.

It is designed to work with the AI sandbox environment and includes:

- Python script examples
- Jupyter notebooks for guided learning
- module-level READMEs with setup notes, study order, and project ideas
- progressive examples that move from basic LLM usage to RAG, tool calling, agents, multimodal workflows, and database-centric AI patterns

If you need sandbox access or help with setup, use the `#igiu-ai-learning` Slack channel.

## Who This Repository Is For

This repository is intended for:

- Python developers who are new to OCI AI services
- developers learning LangChain and agentic workflows
- engineers exploring Oracle Database + AI patterns
- workshop users who want runnable examples and guided notebooks

## Quick Start

If you want the fastest path to a working local setup:

1. Request sandbox access through `#igiu-ai-learning`.
2. Configure `sandbox.yaml` and `.env` for your environment.
3. Install dependencies with `uv sync`.
4. Run:

   ```bash
   uv run AISandboxEnvCheck.py
   ```

5. Start with one of these:
   - `langChain/llm/readme_langchain_llm.md`
   - `langChain/agents/readme_agents.md`
   - `langChain/agents/agents.ipynb`

## Environment and Sandbox Setup

### 1. Request sandbox access

Request access through `#igiu-ai-learning`.

- Set up API keys and database access based on the sandbox instructions available [here](https://gbuconfluence.oraclecorp.com/display/D2OPS/AISandbox#AISandbox-ToAccessADW).
- Update `sandbox.yaml` for your environment.
- You can either edit `sandbox.yaml` directly or reference sensitive values through `.env`.
- Use `.example.env` as a starting point where helpful.

### 2. Understand the sandbox regions

The AI sandbox provides access to two OCI regions:

1. **Chicago**
   - AI services
   - AI Playground
   - Gen AI Agents

2. **Phoenix**
   - 26 AI Database
   - Object Storage buckets
   - Compute resources (if available)

### 3. Understand shared resources

Some sandbox resources are shared across users:

- The Object Storage bucket in **Chicago** is a read-only replica of the bucket in **Phoenix**.
  - Files uploaded in Phoenix will appear in Chicago automatically.
- The bucket is shared across users.
  - Use your Oracle user ID as your object `prefix` in `sandbox.yaml`.
- The 26ai database schema is also shared.
  - Use your Oracle user ID as your table-name `prefix` in `sandbox.yaml`.
- For database examples:
  - download the 26ai wallet
  - unzip it locally
  - update `sandbox.yaml` with the wallet path, user, service name, and password
  - optionally inject sensitive values through `.env`

### 4. Set up the local environment with UV

This repository uses **UV** for dependency management and execution.

1. Install UV:
   - https://docs.astral.sh/uv/getting-started/installation/

2. Sync dependencies:

   ```bash
   uv sync
   ```

3. Verify your setup:

   ```bash
   uv run AISandboxEnvCheck.py
   ```

## Running Code

### Running Python scripts

Use:

```bash
uv run <path/to/script>
```

Example:

```bash
uv run langChain/llm/langchain_oci_chat.py
```

### Running notebooks

Open notebooks in VS Code with the Jupyter extension (or use JupyterLab).

Some notebooks expect the working directory to be the repository root. If needed, follow the notebook-specific setup guidance for notebook root / `cwd` configuration.

## Recommended Learning Paths

This repository supports two main learning paths.

### Path 1: LangChain-first learning path

This is the recommended path if you want to learn modern LLM application patterns first.

- **`langChain/llm`**
  - Chat, history, streaming, structured output, async, reasoning, and stateful responses

- **`langChain/function_calling`**
  - Tool calling and MCP with LangChain

- **`langChain/agents`**
  - Basic agents, LangGraph workflows, Langfuse tracing, and A2A examples

- **`langChain/rag`**
  - Chunking, embeddings, Oracle DB vector search, and reranking

- **`langChain/multimodal`**
  - Vision and speech workflows using multimodal LLMs

- **`database`**
  - NL2SQL, Select AI, database-centric RAG, and semantic caching in Oracle Database

### Path 2: OCI-native learning path

This path is best if you want to learn OCI AI services through OCI SDKs and platform APIs directly.

- **`oci_genai/llm`**
- **`oci_genai/function_calling`**
- **`oci_genai/rag`**
- **`oci_genai/speech`**
- **`oci_genai/vision`**

## Module Index

### LangChain-based modules

- **`langChain/llm`**
  - LLM interactions with chat, history, streaming, structured output, async, reasoning, and stateful responses

- **`langChain/function_calling`**
  - Single-step and multi-step tool calling
  - Manual vs automatic orchestration
  - MCP integrations

- **`langChain/agents`**
  - Basic agents
  - LangGraph workflows
  - Langfuse tracing
  - A2A communication

- **`langChain/rag`**
  - Document chunking
  - Embeddings
  - Semantic search
  - Full RAG workflows
  - Optional AIA reranking

- **`langChain/multimodal`**
  - Text → image
  - Text → speech
  - Speech → text
  - Image → text

### OCI-native modules

- **`oci_genai/llm`**
- **`oci_genai/function_calling`**
- **`oci_genai/rag`**
- **`oci_genai/speech`**
- **`oci_genai/vision`**

### Database module

- **`database`**
  - AI in Oracle Autonomous Database 26ai
  - NL2SQL
  - Select AI
  - Database-centric RAG
  - Semantic caching

Refer to each module’s README for setup details, study order, experiments, and Slack references.

## OCI Object Storage Helper Commands

Use these commands to manage files in Object Storage.

Replace `NAMESPACE`, `BUCKET`, and `PREFIX` with your values from `sandbox.yaml`.

- List objects:

  ```bash
  oci os object list --all --fields name,timeCreated --namespace NAMESPACE --bucket-name BUCKET --prefix PREFIX
  ```

- Upload a file:

  ```bash
  oci os object put --namespace NAMESPACE --bucket-name BUCKET --prefix PREFIX --file your_file.txt
  ```

- Bulk delete:

  ```bash
  oci os object bulk-delete --namespace NAMESPACE --bucket-name BUCKET --prefix PREFIX
  ```

## Environment Variables

Create a `.env` file at the project root for sensitive values referenced by `sandbox.yaml`.

Typical examples include:
- database passwords
- user prefixes
- optional API keys or tracing settings

Example:

```env
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
```

## Repository Conventions

This repository follows a few important conventions:

- `sandbox.yaml` stores configuration data
- `.env` stores sensitive values referenced by config
- `uv` is the standard way to run scripts
- each module has its own README
- many modules include both Python scripts and notebooks
- notebooks are intended to be guided, teaching-oriented assets rather than raw script dumps

## Primary SDKs and Libraries Used

This workshop focuses primarily on:

- [OCI Generative AI Python SDK](https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models)
- [OCI OpenAI-Compatible SDK](https://github.com/oracle-samples/oci-openai)
- [Oracle LangChain integration](https://github.com/oracle/langchain-oracle/tree/main)

## Need Help?

If you run into issues or want help deciding where to start:

- **`#igiu-ai-learning`**: sandbox setup, execution help, workshop support
- **`#generative-ai-users`**: OCI Generative AI questions
- **`#igiu-innovation-lab`**: project ideas and general discussion
