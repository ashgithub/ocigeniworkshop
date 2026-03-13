# Welcome to the Function Calling Module

This module explores how LLMs use tools to solve user problems. In LangChain, function calling and tool calling are synonymous  related: the model decides when to call a tool, provides arguments, and then uses the tool result to continue reasoning.

## What You Will Learn

In this module, you will learn how to:

1. Handle single-step and multi-step tool calls
2. Compare manual tool orchestration with automatic agent orchestration
3. Understand how LangChain binds tools to models
4. Use notebooks to experiment with tool-calling patterns interactively
5. Extend function calling into Model Context Protocol (MCP) workflows

## Environment Setup

- `sandbox.yaml`: Contains OCI configuration and compartment details.
- `.env`: Loads environment variables and optional overrides.
- Ensure you have access to OCI Generative AI services before running the examples.

## Suggested Study Order and File Descriptions

The files are designed to build on one another. Study them in this order for a progressive understanding:

1. **`langchain_single_manual.py`**
   - Demonstrates basic single-step function calling where the model requests a single tool
   - Highlights: manual tool execution, message history management, and final model reinvocation
   - Run: `uv run langChain/function_calling/langchain_single_manual.py`

2. **`langchain_single_auto.py`**
   - Demonstrates single-step function calling with automatic agent orchestration
   - Highlights: `create_agent`, automatic tool handling, and streaming updates
   - Run: `uv run langChain/function_calling/langchain_single_auto.py`

3. **`langchain_multi_manual.py`**
   - Demonstrates manual multi-step tool orchestration in a loop
   - Highlights: iterative tool calling, tool maps, and explicit model/tool handoff
   - Run: `uv run langChain/function_calling/langchain_multi_manual.py`

4. **`langchain_multi_auto.py`**
   - Demonstrates multi-step tool orchestration with automatic agent handling
   - Highlights: agent-managed multi-step reasoning and streamed progress output
   - Run: `uv run langChain/function_calling/langchain_multi_auto.py`

5. **`singlestep_tool.ipynb`**
   - Notebook walkthrough of single-step tool calling in both manual and automatic forms
   - Highlights: guided explanations, experiments, and side-by-side comparison with the Python scripts
   - Run: open in VS Code or Jupyter and execute cells sequentially

6. **`multistep_tool.ipynb`**
   - Notebook walkthrough of multi-step tool orchestration in both manual and automatic forms
   - Highlights: iterative tool loops, message handling, and streamed agent behavior
   - Run: open in VS Code or Jupyter and execute cells sequentially

7. **`mcp/`**
   - Model Context Protocol servers and client integration examples
   - Highlights: external tool servers, MCP transports, tool discovery, and host integration
   - Includes: `weather_mcp_server.py`, `bill_mcp_server.py`, `langchain_mcp_auto.py`, `langchain_mcp_manual.py`, `langchain_mcp.ipynb`, `readme_mcp.md`, and related utilities

## Project Ideas

Here are some ideas for projects you can build on top of these examples:

1. **Build a personal assistant agent**
   - Create tools for weather, calendar, and email summaries.
   - Implement multi-step orchestration to plan a day based on weather and schedule.

2. **Intelligent tool router**
   - Classify user queries and route them to specialized tools.
   - Compare manual routing with model-driven routing.

3. **Semantic cache integration**
   - Combine tool-calling with semantic caching to reduce repeated work.
   - Experiment with caching thresholds and repeated queries.

4. **Streaming-first tool workflows**
   - Improve streaming output and explore how streamed updates help debugging.

5. **Guardrailed tool-calling agent**
   - Add validation or safety checks before allowing certain tools to run.

## Ideas for Experimenting

- **Prompt Engineering**: Change the prompt wording and observe how tool selection changes.
- **Model Selection**: Compare reasoning and non-reasoning models across manual and automatic patterns.
- **Tool Design**: Add more tools or change tool parameters and outputs.
- **Streaming Behavior**: Compare non-streamed and streamed execution.
- **Workflow Design**: Test where manual orchestration is easier to debug than agent-based automation.

## Resources and Links

- **Documentation**:
  - [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [LangChain Agents and Tools](https://docs.langchain.com/oss/python/langchain/agents)
  - [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)
  - [MCP Specification](https://modelcontextprotocol.io/specification)
  - [Fast MCP](https://gofastmcp.com/getting-started/welcome)
  - [LangChain MCP](https://docs.langchain.com/oss/python/langchain/mcp)
  - [OCI Python SDK](https://github.com/oracle/oci-python-sdk)
  - [OCI OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai)
  

- **Slack Channels**:
  - **#igiu-ai-learning**: Help with environment setup or running code
  - **#igiu-innovation-lab**: Discuss project ideas
  - **#generative-ai-users**: Questions about OCI Generative AI
