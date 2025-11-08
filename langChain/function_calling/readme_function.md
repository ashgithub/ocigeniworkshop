## Welcome to the agents Module.
In this module, we will experiment with the llms ability to call functions.  
Funtion calling ability is synonymous to using a tool. Agent can be given a set of tools and Agent can decomprose the problem and se the set of tools to solve it.


In this module we will look at following abilities: 
1. Single Step tool:  LLM invoking a single function/ using a single tool
2. Multi Step tool : LLM orcestrating a sequence of function calls.

Remember to set up your `sandbox.yaml` file per your environment. This module only uses the "oci" section

The module covers two different ways to do the tool calls during the flow execution:
1. **Manual**: build a list of messages (similar to chat history). Requires to manually manage message context, 
adding the user message, tool call and tool response to the list before the next LLM invokation. Use the openai compatible oci sdk 
library for all the operations, including grok / openai models using langchain 1.0.0 agents 
2. **LangChain Agent**: use ```create_agent``` function to build a solid function calling agent. In this option, 
all the tool calls and reasoning are automatically managed by langchain 

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:
1. **langchain_step.py,  singlestep_tool.ipynb**: agent that calls a function
2. **langchain_step_manual.py**: llm calling a binded function and context messages
3. **langchain_multi_step.py, multistep_tool.ipynb** : agent orchestration across multiple tools
4. **langchain_multi_manual.py**: llm orchestration across different binded functions and context messages

Here are some ideas of projects you can do (See notebook files for details):
- Create an agent that finds the credentials for a user
    - Build a simple mock data retrival tool
- Create and agent that suggest clothes
    - Build weather tool
    - Build closet clothes tool
    - Build day agenda details tool
    - Agent can call as chain of tools to provide best clothes.

Here are few slack channels to help you: 

- **#igiu-ai-learning**  : if you have issues with environment or cant get this code working 
- **#igiu-innovation-lab** : discuss project ideas
- **#generative-ai-users** :  if you have questions about OCI GenAI  API  