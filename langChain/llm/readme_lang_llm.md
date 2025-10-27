
## Welcome to the LangChain LLM Module. 
In this module we wll explore how to integrate the ```langchain_oci``` library to use along with LangChain methods.
Also how to do **structured output** with openai and grok models

Specifically, we will try the following capabilities:
1. Chat api for conversations & various parameters 
2. Remembersing past conversations (history + graph checkpointer) 
3. Processing the streaming response from LLM
4. Structured output from LLM response
5. LangChain asyncronous capacity

Remember to set up your `sandbox.json` file per your environment. This module only uses the "oci" section 

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. **langchain_chat.py**: simple example on how to invoke a LangChain model with OCI API.
2. **langchain_stream.py**: process LLM response as a streaming using stream chunks and values to reduce user expectation and response latency.
3. **langchain_history.py**: LLM capable of remembering multiturn conversations and context. Integration with a simple graph from LangGraph library.
4. **langchain_async.py**: showcase of async method calling using LangChain.
5. **openai_output_schema.py**: formatted response from JSON schemas and Pydantic classes using openai and grok models.
6. **langchain_llm.ipynb**: notebook version of all the above modules

Here are some ideas of projects you can do (See notebook files for details):
- Create a bot that remembers the conversation.
    - eg Q1. What are the 5 top tourist spots in India
    - eg Q2. Tell me more about 3rd one. whats the best time to vist 
-  Specify the output schema and ask the question again. Some ideas for the  schema: 
    - Name of toursit spot, address, best time to visit, highlighths, year established etc 
- Ask the question again and see that it returns the 5 spots in the format asked 
- Remove the schema and see if you can stream the response    

Here are few slack channels to help you:  
 - **#igiu-ai-learning**  : if you have issues with environment or cant get this code working 
 - **#igiu-innovation-lab** : discuss project ideas
 - **#generative-ai-users**  :  if you have questions about OCI GenAI  API  

