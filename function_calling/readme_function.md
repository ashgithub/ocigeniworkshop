## Welcome to the Function Calling Module

In this module, we will experiment with the LLMs' ability to call functions.
Function calling ability is synonymous with using a tool. An agent can be given a set of tools, and the agent can decompose the problem and see the set of tools to solve it.

In this module, we will look at the following abilities:
1. Single-step tool: LLM invoking a single function/using a single tool.
2. Multi-step tool: LLM orchestrating a sequence of functions.
3. Classification: Using LLM to classify given text. This can be used to find the right set of tools to give the LLM.
4. Llama tool example: Function calling with Llama models using different tool definitions.

## Environment Setup
- `sandbox.yaml`: Contains OCI config and compartment details.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to OCI Generative AI services.

## Suggested Study Order and File Descriptions
The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **single_step_demo.py**: Demonstrates single-step function calling using OCI Generative AI Cohere models. Shows how to define tools, make tool calls, and provide tool results to get a final response.
   - Key features: Defines a shopping tool, makes a single tool call, handles tool results.
   - How to run: `uv run function_calling/single_step_demo.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

2. **single_step_demo_streaming.py**: Demonstrates single-step function calling with streaming using OCI Generative AI Cohere models. Shows how to handle streaming responses and tool calls.
   - Key features: Streaming chat response, tool call extraction from stream, tool result handling.
   - How to run: `uv run function_calling/single_step_demo_streaming.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

3. **singlestep_tool.ipynb**: A Jupyter notebook variation of the single_step_demo.py script, demonstrating single-step function calling with markdown explanations and interactive cells.
   - Key features: Mirrors the Python script; includes step-by-step markdown for understanding; defines a shopping tool, makes a single tool call, handles tool results.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

4. **multi_step_demo.py**: Demonstrates multi-step function calling using OCI Generative AI Cohere models. Shows how the model can make multiple tool calls sequentially to accomplish a complex task.
   - Key features: Multiple tools (sales report, calculator), iterative tool calling with chat history.
   - How to run: `uv run function_calling/multi_step_demo.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

5. **multi_step_demo_streaming.py**: Demonstrates multi-step function calling with streaming using OCI Generative AI Cohere models. Shows how to handle streaming responses in multi-step tool calling scenarios.
   - Key features: Streaming responses with multiple tool calls, chat history management.
   - How to run: `uv run function_calling/multi_step_demo_streaming.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

6. **multistep_tool.ipynb**: A Jupyter notebook variation of the multi_step_demo.py script, demonstrating multi-step function calling with markdown explanations and interactive cells.
   - Key features: Mirrors the Python script; includes step-by-step markdown for understanding; multiple tools (sales report, calculator), iterative tool calling with chat history.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

7. **llama_tool_example.py**: Demonstrates function calling using OCI Generative AI Llama models. Shows how to define tools and handle tool calls with Llama models in a multi-step conversation.
   - Key features: Llama-specific tool definitions, multi-step conversation with tool results.
   - How to run: `uv run function_calling/llama_tool_example.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Llama Models](https://www.llama.com/).

8. **llm_classification.py**: Demonstrates text classification using OCI Generative AI Cohere models. Shows how to prompt the model to classify customer questions into predefined categories using a custom preamble.
   - Key features: Custom preamble for classification, categories like billing, outage, program, service.
   - How to run: `uv run function_calling/llm_classification.py`.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

9. **classification.ipynb**: A Jupyter notebook variation of the llm_classification.py script, demonstrating text classification with markdown explanations and interactive cells.
   - Key features: Mirrors the Python script; includes step-by-step markdown for understanding; classification with custom preamble.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.
   - Docs: [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm), [Cohere Command Models](https://docs.cohere.com/docs/command-r).

Note: OCI GenAI only supports function calling for Cohere models and not Llama. For Llama models, different tool definition approaches are used.

## Project Ideas
Here are some ideas for projects you can build upon these examples:

1. Create an agent that finds the credentials for a user:
   - Build a simple mock data retrieval tool that simulates user credential lookup.
   - Implement secure tool calls to retrieve user information based on queries.
   - Resources: [Tool Calling Best Practices](https://docs.cohere.com/docs/tool-calling), [OCI Security](https://docs.oracle.com/en-us/iaas/Content/security/home.htm).

2. Build a personal shopping assistant:
   - Create tools for inventory checking, price comparison, and order placement.
   - Use multi-step calling to handle complex shopping scenarios (e.g., check stock, calculate total, process payment).
   - Resources: [E-commerce Integration](https://docs.oracle.com/en/cloud/saas/fusion-service/index.html), [Multi-step Tool Calling](https://docs.cohere.com/docs/multi-step-tool-calling).

3. Create an agent that suggests clothes based on weather and schedule:
   - Build weather API tool to get current conditions.
   - Build closet inventory tool to list available clothing.
   - Build calendar tool to check daily agenda.
   - Agent orchestrates multiple tool calls to provide personalized clothing recommendations.
   - Resources: [Weather APIs](https://openweathermap.org/api), [Calendar Integration](https://docs.oracle.com/en/cloud/saas/fusion-service/index.html).

4. Implement a customer support chatbot with tool routing:
   - Use classification to route queries to appropriate tools (billing, technical support, account management).
   - Integrate with CRM systems for customer data lookup.
   - Combine with semantic caching for improved response times.
   - Resources: [Chatbot Development](https://docs.oracle.com/en/cloud/saas/fusion-service/index.html), [Semantic Caching](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/).

## Resources and Links
- **Documentation**:
  - [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [Cohere Command Models](https://docs.cohere.com/docs/command-r)
  - [Llama Models](https://www.llama.com/)
  - [OCI Python SDK](https://github.com/oracle/oci-python-sdk)
  - [Oracle Autonomous Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/index.html)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas and collaboration.
  - **#igiu-ai-learning**: Help with sandbox environment setup and running code.
  - **#generative-ai-users**: Questions about OCI Gen AI APIs and models.
  - **#adb-select-ai-users**: Questions about Select AI and database integrations.
