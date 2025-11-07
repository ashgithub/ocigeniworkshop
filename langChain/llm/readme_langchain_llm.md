## Welcome to the LangChain LLM Module

This module shows how to use OpenAI-compatible LLM models (via OCI) in Python, including chat, multi-turn history, streaming, batch, async, and structured output/schema responses. It leverages the upcoming openai-compatible OCI library and demonstrates practical coding patterns for integrating large language models into scripts and applications. The examples also reference the older `langchain_oci` library for broader model support.

- **openai-compatible oci library:** Supports all OpenAI features except Cohere models. Best for advanced features like structured output and agents.
- **langchain_oci library:** Supports all models, including Cohere, but may not support all advanced OpenAI features.

### Key Capabilities

- **Chat API**: Basic and advanced prompt completion.
- **Conversation History**: Contextual chat (multi-turn).
- **Streaming**: Real-time response processing.
- **Structured Output**: JSON schema and Pydantic-based model outputs.
- **Async Calls**: Concurrent invocation patterns.
- **Batching**: Multiple prompts at once.
- **Model Comparison**: Support for OpenAI, Meta, Cohere, Groq models (where available).

> See `openai_oci_llm.ipynb` for a full step-by-step notebook tutorial.

---

### Example Files

| File Name                        | Description                                                 |
|-----------------------------------|-------------------------------------------------------------|
| `langchain_oci_chat.py`           | Basic chat completion with the OCI LangChain API.           |
| `openai_oci_chat.py`              | Basic chat completion with the OCI OpenAI-compatible API.   |
| `openai_oci_stream.py`            | Streaming response/chunks demo from LLMs.                   |
| `openai_oci_history.py`           | Multi-turn chat conversations and context maintenance.       |
| `openai_oci_async.py`             | Asynchronous (async/await) completions.                     |
| `openai_oci_structured_output.py` | Structured/JSON output and schema enforcement.              |
| `openai_oci_reasoning.py`            | Showing reasoning details via openai responses api       |
| `openai_oci_llm.ipynb`            | Jupyter notebook walk-through for all features above.       |

---

### Getting Started / Configuration

- Set up your credentials in `sandbox.yaml` and make sure the `"oci"` section has correct values for your tenancy/profile/environment.
- Optionally, place sensitive data in a `.env` file (see below for example). Use `python-dotenv` if needed.

**Example `.env`:**
```
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
```

---

### Slack & Community Help

- **#igiu-ai-learning**: For help getting code running or fixing environment issues.
- **#igiu-innovation-lab**: Share ideas, project discussion.
- **#generative-ai-users**: For general OCI GenAI questions.

---

### Suggested Projects & Next Steps

- Build a conversational bot with memory and context.
- Implement custom output schemas and compare structured outputs.
- Send multiple prompts and study response variation among models.
- Integrate streaming for large/long answers.
- Use async or batch processing for speed.
- Refer to the "Exercises" and "Future Work" sections at the end of `openai_oci_llm.ipynb`.

> For more, inspect the notebook for working code and hands-on tasks!
