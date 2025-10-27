## Welcome to the agents Module.
In this module, we will experiment with the llms ability to call functions.  
Funtion calling ability is synonymous to using a tool. Agent can be given a set of tools and Agent can decomprose the problem and se the set of tools to solve it.

> [!IMPORTANT]  
> Last update 10/27/2025
> Current langchain-oci version 0.1.5 requires past langchain version 0.3.27
> This langchain version along with langchain-oci version have some errors when using openai / grok models with multi tool calls over the create_agent method.
> To avoid errors, when using multi step flows langchain agents, use the external library ```openai_oci_client``` available in the folder.
> Examples of openai / grok models are provided when required inside each code sample.
> Manual multi step option is also available at ```langchain_multi_manual.py```. This option does not require the ```openai_oci_client``` and supports openai /grok models.
> Latest langchain version 1.0.0 has method create_agent which supports better this kind of flows, in this workshop this version is not used.

In this module we will look at following abilities: 
1. Single Step tool:  LLM invoking a single function/ using a single tool
2. Multi Step tool : LLM orcestrating a sequence of function calls.

Remember to set up your `sandbox.json` file per your environment. This module only uses the "oci" section

The module covers two different ways to do the tool calls during the flow execution:
1. **Manual**: build a list of messages (similar to chat history). Requires to manually manage message context, 
adding the user message, tool call and tool response to the list before the next LLM invokation. Use the langchain-oci 
library for all the operations, including grok / openai models without need of ```openai_oci_client``` external library.
2. **LangChain Agent**: use ```create_agent``` function to build a solid function calling agent. In this option, 
all the tool calls and reasoning are automatically managed by langchain and the model (langchain-oci only supports cohere models). 
Best option when having long multi step flows. It requires the use of ```openai_oci_client``` external library to call agents using openai / grok models.

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:
1. **langchain_step.py, langchain_step_stream.py, singlestep_tool.ipynb**: agent that calls a function
2. **langchain_step_manual.py**: llm calling a binded function and context messages
3. **langchain_multi_step.py, langchain_multi_step_stream.py, multistep_tool.ipynb** : agent orchestration across multiple tools
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