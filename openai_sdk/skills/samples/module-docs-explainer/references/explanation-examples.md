# Explanation Examples

Use these shapes as examples, not rigid templates.

## Beginner Topic Request

User asks: "Where should I start if I want to learn agents?"

Answer shape:

1. Start with `openai_sdk/agent_sdk/readme_agent_sdk.md` for the SDK-first path.
2. Then compare with `langChain/agents/readme_agents.md` for framework orchestration.
3. Open one simple script before notebooks.
4. Mention the environment check if they plan to run code.

## Module Deep Dive

User asks: "Explain `langChain/rag`."

Answer shape:

1. State what the module teaches.
2. Name the entry README.
3. Group files by concept: chunking, embeddings, retrieval, reranking, full RAG.
4. Suggest one read-only pass and one runnable command.
5. Call out credentials or local files needed for execution.

## Path Comparison

User asks: "OpenAI SDK or LangChain first?"

Answer shape:

1. Recommend `openai_sdk` for most new users in this repo.
2. Recommend `langChain` when they want framework abstractions and orchestration patterns.
3. Mention `oci_genai` as useful for direct OCI-native patterns, not the default first stop.
4. Give one concrete file from each path so the comparison is actionable.
