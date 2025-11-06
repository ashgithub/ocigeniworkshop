
## Welcome to the Function Calling Module.
In this module, we will experiment with the LLMs' ability to call functions.
Function calling ability is synonymous with using a tool. An agent can be given a set of tools, and the agent can decompose the problem and see the set of tools to solve it.

In this module, we will look at the following abilities:
1. Single-step tool: LLM invoking a single function/using a single tool.
2. Multi-step tool: LLM orchestrating a sequence of functions.

The following two are not directly related to tools/functions but can help in your LLM/RAG pipeline:
3. Classification: Using LLM to classify given text. This can be used to find the right set of tools to give the LLM.
4. Semantic Cache: Ability to cache answers and retrieve them using semantic search instead of key lookup.

Note:
1. OCI GenAI only supports function calling for Cohere models and not Llama.
2. There are streaming and non-streaming versions of code. The streaming version is fragile.
the database schema is shared, set a unique `prefix` in the database section of `sandbox.yaml`. Your Oracle user ID is a good choice.

Remember to set up your `sandbox.yaml` file per your environment. This module only uses the "oci" section.

Example code in this module is available both as Jupyter notebook and Python code. They are very similar:
1. **single_step_demo.py, single_step_demo_streaming.py, singlestep_tool.ipynb**: LLM calling a function.
2. **multi_step_demo.py, multi_step_demo_streaming.py, multistep_tool.ipynb**: LLM orchestration across multiple tools.
3. **llm_classification.py, classification.ipynb**: Classifying the given sentence.



Here are some ideas for projects you can do (see notebook files for details):
- Create an agent that finds the credentials for a user.
    - Build a simple mock data retrieval tool.
- Create an agent that suggests clothes.
    - Build weather tool.
    - Build closet clothes tool.
    - Build day agenda details tool.
    - Agent can call as a chain of tools to provide best clothes.

Here are a few Slack channels to help you:
- **#igiu-ai-learning**: If you have issues with environment or can't get this code working.
- **#igiu-innovation-lab**: Discuss project ideas.
- **#generative-ai-users**: If you have questions about OCI GenAI API.

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml`.

Example `.env`:
```
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
