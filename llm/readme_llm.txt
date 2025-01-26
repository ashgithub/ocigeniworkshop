
Welcome to the LLM Module. In this module, we will experiment with the OCI GenAI apis, particularly the Cohere models 

Specifically, we will try the following capabilities:
1. Chat api for conversations & various parameters 
2. Remembersing past conversations (history) 
3. Processing the streaming response from LLM 
4. enforcing the output format for LLM responses 
5. oci langauge service as an example for small language model 

Remember to set up your sandbox.json file per your environment. This module only uses the "oci" section 

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. cohere_chat.py : simple example on how to invoke oci api 
2. cohere_stream.py : looking at how to process LLM as a stream to reduce response latency 
3. cohere_chat_history.py : how to remember past conversation so LLM can resond within the conversation context
4. cohere_output_schema.py : specying JSON schema to force output to be specified format
5. llm.ipynb : Jupyter notebook version of above 
6. oci_language.py, oci-language.ipynb : LLMs are slow & expensive, SLMs like oci-langauge can ve useful. simple examples on how to use the oci-language service for simople language tasks 

Here are some ideas of projects you can do (See notebook files for details):
    -  create a bot that remembers the conversation.
        - eg Q1. what are the 5 top tourist spot in India
        - eg q2. tell me more about 3rd one. whats the best time to vist 
    -  specify the output schema and ask the question again. some ideas of schema
         - name of toursit spot, address, best time to visit, highlighths, year established etc 
    - ask the question again and see that it retirns the 5 spots in the format asked 
    - remove the schema and see if you can stream the response    

Here are few slack channels to help you:  

#igiu-ai-learning  : if you have issues with environment or cant get this code working 
#igiu-innovation-lab : discuss project ideas
#generative-ai-users :  if you have questions about OCI GenAI  API  

