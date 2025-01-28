
## Welcome to the RAG (Retrival Augmented Generation) Module. 

In this module, we will experiment with the llm ability to answer questions using  proprietary data


In this module we will look at following ability:
1. "Documents" attribute of oci gen ai api & ability for citations
2. Using Oci Agents ofr "off the shelf Rag ability 
3. leveraging 23ai database for home grown rag 
4. Introduction to sleect AI 
5. Select AI with RAG


Remember to set up your `sandbox.json` file per your environment. This module only uses the "oci" & "db" section 

Oracle 23 ai databased is used in this module: 
    - The database requires the wallet to be downlaoded. 
    - Remember to update the database section per your setup in `sandbox.json` 
    - As the database schmea is shared, set a unique `prefix` in teh datbase section of `sanbox.json`. Your Oralce user id is a good choice

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. **cohere_chat_citation, RAG-documents.ipynb**: Use of `documents`  to pass non-pubic text text to llm and see a resposne with citation based on it 
2. **oci_rag_agents, RAG-agents.ipynb**: Leverage  OCI GenAI Agent service for a out of the box agent (see agent_readme.md for setup) 
3. **cohere_rag_23ai.py, RAG-full.ipynb**: full homegrown rag implementation using 23ai
4. **select_ai.sql**: SQl sript to demonstrate selectai capability
5. **rag.sql**: Sql script for doing full rag in database.



Here are some ideas of projects you can do (See notebook files for details):
   
1. create an "talk to my document" application by hand 
    - allow user to upload the docs
    - parse and chunck the doc using various chunking strategies (semnatic chunking is adviced. search teh net ofr different approaches)
    - try different algorithm for similarity search. COSINE is popular, but Euclidean, DOR etc are also common 
    - try rerankers to see if your retrived documents were reordered
    - include citations in your

Here are few slack channels to help you:  

- **#igiu-innovation-lab** : discuss project ideas
- **#igiu-ai-learning** : if you have issues with environment or cant get your code to work 
- **#generative-ai-users** : questions about oci gen ai 
- **#adb-select-ai-users** : questions about oracle 23ai select ai 

