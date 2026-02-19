## Welcome to the Function Calling Module
In this module, we will experiment with the LLMs' ability to call functions. Function calling is synonymous with using tools, where an agent can be given a set of tools and decompose problems to solve them using those tools.

In this module, we will explore the following capabilities:
1. Single-step & multi step tools: LLM invoking a single function/tool vs orcestrating a sequence of tool calls
2. Manual vs automated tool call: Different ways of handling LLM tool call requests 


## Environment Setup
- `sandbox.yaml`: Contains OCI config, compartment
- `.env`:  environment variables for secrets
- Ensure you have access to OCI Generative AI services.

## Suggested Study Order and File Descriptions
The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **langchain_single_manual.py**: Demonstrates basic single-step function calling where the LLM requests a single tool toolcall to answer a query.
   - Key features: Binds a single tool to the LLM 
   - How to run: `uv run langChain/function_calling/langchain_single_manual.py`.
   - Docs: [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/)

2. **langchain_multi_manual.py**: Demonstrates llm requesting multiple tool calls to answer a query
   - Key features: Similar to langchain_single_manual.py but with multiple tool requests 
   - How to run: `uv run langChain/function_calling/langchain_multi_manual.py`.
   - Docs: [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/)

3. **langchain_single_auto.py**: Demonstrates basic single-step function calling where langchaiun automatically handles the toolcall to answer a query.
   - Key features: use of langChain agents for automaticl call toolcall handling
   - How to run: `uv run langChain/function_calling/langchain_single_auto.py`.
   - Docs: [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/)

4. **langchain_multi_manual.py**: Demonstrates how multiple tool call can be handled automatically by langchain
   - Key features: use of langChain agents for automaticl call toolcall handling
   - How to run: `uv run langChain/function_calling/langchain_multi_auto.py`.
   - Docs: [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/)


5. **singlestep_tool.ipynb**: A Jupyter notebook variation of single step tool calling demonstrating single-step tool calling with interactive cells and explanations.
   - Key features: Mirrors the Python script; includes markdown for understanding, experiments with models and prompts.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai), [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/).

6. **multistep_tool.ipynb**: A Jupyter notebook variation of  demonstrating multi-step tool orchestration with interactive cells and explanations.
   - Key features: Mirrors the Python script; includes markdown, encourages experimentation with tools and prompts.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai), [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents).

7. **mcp/**: Model Context Protocol servers and client integration (subfolder).
   - Key features: Demonstrates external MCP servers (weather and bill calculation), HTTP and stdio transports, tool discovery, and agent integration.
   - Files: weather_mcp_server.py, bill_mcp_server.py, langchain_host.py, langchain_host.ipynb, readme_mcp.md.
   - How to run: Start weather server first, then run langchain_host.py or use the notebook.
   - Docs: [MCP Specification](https://modelcontextprotocol.io/specification), [LangChain MCP](https://docs.langchain.com/oss/python/langchain/mcp).


## Project Ideas
Here are some ideas for projects you can build upon these examples. Focus on experimenting with tools, models, and pipelines to deepen your understanding:

1. **Build a personal assistant agent**:
   - Create tools for weather, calendar, and email summaries.
   - Implement multi-step orchestration to plan a day based on weather and schedule.
   - Experiment with adding memory (e.g., LangChain's memory modules) to retain context across interactions.
   - Resources: [LangChain Memory](https://docs.langchain.com/oss/python/langchain/memory), [Custom Tools Guide](https://python.langchain.com/docs/how_to/custom_tools/).

2. **Intelligent tool router**:
   - Use classification (from llm_classification.py) to categorize user queries and route to appropriate tools.
   - Add more categories and tools; test accuracy by comparing classified results with manual routing.
   - Experiment with different prompts in the classifier to improve precision.
   - Resources: [Prompt Engineering](https://docs.langchain.com/oss/python/langchain/guides/prompt_engineering), [OCI Gen AI Models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm).

3. **Semantic caching in RAG**:
   - Integrate semantic cache from llm_semantic_cache.py into a RAG pipeline.
   - Measure performance improvements by caching frequent queries.
   - Experiment with different embedding models or similarity thresholds.
   - Resources: [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/), [LangChain Caching](https://docs.langchain.com/oss/python/langchain/caching).

4. **Streaming enhancements**:
   - Modify streaming demos to handle errors gracefully.
   - Compare streaming vs. non-streaming performance in multi-step scenarios.
   - Experiment with partial streaming for tool calls.
   - Resources: [LangChain Streaming](https://python.langchain.com/docs/how_to/streaming/).

5. **Advanced agent with guardrails**:
   - Add guardrails to prevent harmful tool calls (e.g., restrict sensitive data access).
   - Experiment with multi-turn conversations and tool chaining.
   - Resources: [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents), [OCI Gen AI Safety](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm).

## Learning and Experimentation Suggestions
- **Start simple**: Begin with single-step demos to understand tool binding and invocation.
- **Experiment with models**: Try different LLM_MODEL values. from different families (e.g., 'xai,grok-4', 'openai.gpt-5') to see how tool usage varies. try switchig between reasoning & non-reasoning models
- **Modify tools**: Change tool logic or add parameters to observe how the LLM adapts.
- **Debug streaming**: Use streaming versions to learn about real-time responses, but fall back to non-streaming if issues arise.
- **Combine modules**: Integrate classification with tools for smarter agents, or add caching to reduce API calls.
- **Performance tuning**: Time executions and experiment with reasoning parameters for optimization.

## Resources and Links
- **Documentation**:
  - [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [LangChain Agents and Tools](https://docs.langchain.com/oss/python/langchain/agents)
  - [MCP Specification](https://modelcontextprotocol.io/specification)
  - [Fast MCP](https://gofastmcp.com/getting-started/welcome)
  - [LangChain MCP](https://docs.langchain.com/oss/python/langchain/mcp)
  - [OCI Python SDK](https://github.com/oracle/oci-python-sdk)
  - [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai)
  - [Oracle DB Vectors](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/)

- **Slack Channels**:
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#igiu-innovation-lab**: Discuss project ideas.
  - **#generative-ai-users**: Questions about OCI Gen AI.
