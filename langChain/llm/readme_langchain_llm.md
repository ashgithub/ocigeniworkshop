## Welcome to the LangChain LLM Module

In this module, we will experiment with Large Language Model (LLM) capabilities using OCI's OpenAI-compatible API and LangChain. We will explore basic chat interactions, advanced features like streaming and structured output, and best practices for integrating LLMs into applications.

In this module, we will explore the following capabilities:
1. Basic chat completion using both OCI OpenAI-compatible and LangChain APIs.
2. Conversation history management for multi-turn interactions.
3. Streaming responses for real-time processing.
4. Structured output using JSON schemas and Pydantic models.
5. Asynchronous operations for concurrent processing.
6. Model performance comparison across different LLM providers.

OCI Gen AI provides OpenAI-compatible APIs that support advanced features like structured output, function calling, and reasoning. The module demonstrates both the OCI OpenAI-compatible library (best for OpenAI features) and LangChain OCI library (broader model support).

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment details.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to OCI Generative AI services and proper authentication configured.

## Suggested Study Order and File Descriptions

The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **langchain_oci_chat.py**: Demonstrates basic chat functionality using LangChain's ChatOCIGenAI client for OCI Generative AI models. Shows single calls, batch processing, parameter tuning, model performance comparison, and different prompt types.
   - Key features: Uses LangChain OCI integration; demonstrates multiple models and timing comparisons.
   - Compatibility note: Uses `langchain_oci` library which is not compatible with LangChain v1.0.0 as of November 2025. Requires downgrading to LangChain 0.3.x.
   - How to run: `uv run langChain/llm/langchain_oci_chat.py`.
   - Docs: [LangChain OCI Integration](https://python.langchain.com/docs/integrations/providers/oci/), [OCI Gen AI Chat Models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm).

2. **openai_oci_chat.py**: Demonstrates basic chat functionality using OCI's OpenAI-compatible API for LLM interactions. Shows single calls, batch processing, parameter tuning, model performance comparison, and different prompt types.
   - Key features: Direct OCI OpenAI-compatible API usage; model switching and performance timing.
   - How to run: `uv run langChain/llm/openai_oci_chat.py`.
   - Docs: [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai), [OpenAI API Reference](https://platform.openai.com/docs/api-reference).

3. **openai_oci_history.py**: Demonstrates conversation history management in chat interactions using OCI's OpenAI-compatible API. Shows the difference between stateless conversations and conversations with maintained history.
   - Key features: Multi-turn conversations; context preservation across interactions.
   - How to run: `uv run langChain/llm/openai_oci_history.py`.
   - Docs: [LangChain Messages](https://docs.langchain.com/oss/python/langchain_core/messages), [Conversation Memory](https://docs.langchain.com/oss/python/langchain/memory).

4. **openai_oci_stream.py**: Demonstrates streaming responses with OCI's OpenAI-compatible API, comparing invoke vs stream methods across multiple models with performance timing. Shows real-time token streaming and finish reasons.
   - Key features: Real-time response streaming; performance comparison between streaming and non-streaming.
   - How to run: `uv run langChain/llm/openai_oci_stream.py`.
   - Docs: [LangChain Streaming](https://docs.langchain.com/oss/python/langchain/chat_models#streaming), [OpenAI Streaming API](https://platform.openai.com/docs/api-reference/streaming).

5. **openai_oci_async.py**: Demonstrates asynchronous operations using OCI's OpenAI-compatible API for concurrent LLM calls. Shows async invoke and streaming with performance comparisons between sequential and concurrent execution.
   - Key features: Concurrent processing; asyncio patterns for multiple model calls.
   - How to run: `uv run langChain/llm/openai_oci_async.py`.
   - Docs: [Python Asyncio](https://docs.python.org/3/library/asyncio.html), [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai).

6. **openai_oci_structured_output.py**: Demonstrates structured output using Pydantic models and JSON schemas with OCI's OpenAI-compatible API. Shows how to generate structured data responses including simple JSON, complex nested objects, and Pydantic class instances.
   - Key features: JSON schema enforcement; Pydantic model validation; nested object structures.
   - How to run: `uv run langChain/llm/openai_oci_structured_output.py`.
   - Docs: [LangChain Structured Output](https://python.langchain.com/docs/how_to/structured_output/), [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/).

7. **openai_oci_reasoning.py**: Demonstrates reasoning capabilities with advanced models like GPT-5 using OCI's OpenAI-compatible API. Shows how to enable reasoning features, capture reasoning summaries, and monitor token usage.
   - Key features: Model reasoning traces; token usage breakdown; advanced model capabilities.
   - How to run: `uv run langChain/llm/openai_oci_reasoning.py`.
   - Docs: [OpenAI Reasoning API](https://platform.openai.com/docs/guides/reasoning), [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai).

8. **openai_oci_llm.ipynb**: A Jupyter notebook variation demonstrating comprehensive usage of OpenAI-compatible LLMs via LangChain. Covers basic chat, model performance comparison, batching, streaming, conversation history, structured output, and reasoning capabilities.
   - Key features: Interactive tutorial; step-by-step examples; hands-on exercises and experimentation.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview), [Jupyter Notebooks](https://jupyter.org/).

## Project Ideas

Here are some ideas for projects you can build upon these examples:

1. **Create a multi-model chatbot**:
   - Build a chatbot that can switch between different models based on the task.
   - Compare response quality and speed across models.
   - Add user preferences for model selection.
   - Resources: [Multi-Model Chatbots](https://docs.langchain.com/oss/python/langchain/chat_models), [Model Selection Strategies](https://platform.openai.com/docs/guides/model-selection).

2. **Develop a structured data extraction system**:
   - Use structured output to extract information from unstructured text.
   - Build schemas for different document types (invoices, resumes, articles).
   - Implement validation and error handling for malformed outputs.
   - Resources: [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/), [JSON Schema](https://json-schema.org/).

3. **Build a real-time conversation analyzer**:
   - Use streaming to analyze conversations as they happen.
   - Implement sentiment analysis or topic detection.
   - Add real-time feedback or suggestions.
   - Resources: [Streaming Processing](https://docs.langchain.com/oss/python/langchain/chat_models#streaming), [Real-time Analytics](https://kafka.apache.org/).

4. **Create an async batch processing pipeline**:
   - Process large volumes of text using async operations.
   - Implement queuing and rate limiting.
   - Add monitoring and logging for production use.
   - Resources: [Async Python](https://docs.python.org/3/library/asyncio.html), [Production Pipelines](https://docs.celeryproject.org/).

5. **Develop a reasoning-powered problem solver**:
   - Use reasoning models to break down complex problems.
   - Implement step-by-step problem solving with explanations.
   - Add verification and confidence scoring.
   - Resources: [Reasoning Models](https://platform.openai.com/docs/guides/reasoning), [Problem Solving Techniques](https://en.wikipedia.org/wiki/Problem_solving).

## Resources and Links

- **Documentation**:
  - [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)
  - [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
  - [Pydantic Models](https://docs.pydantic.dev/latest/)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas and share implementations.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#generative-ai-users**: Questions about OCI Gen AI and model capabilities.
