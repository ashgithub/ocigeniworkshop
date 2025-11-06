
## Welcome to the LangChain RAG (Retrival Augmented Generation) Module. 

In this module, we will experiment with the llm ability to answer questions using  proprietary data

In this module we will look at following ability:
1. Use community document loaders to generate text chunks to use
2. Integration of ```langchain_oci``` embed models library
3. Semantic search full example using Oracle DB as knowledge base
4. Wrap up - full RAG example integrating ```ChatOCIGenAI``` to anser user queries

Remember to set up your `sandbox.json` file per your environment. This module only uses the "oci" & "db" section 

Oracle 23 ai databased is used in this module refer to [this page](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW)
    - The database requires the wallet to be downlaoded. 
    - Remember to update the database section per your setup in `sandbox.json` 
    - As the database schmea is shared, set a unique `prefix` in teh datbase section of `sanbox.json`. Your Oralce user id is a good choice

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. **langchain_chunks.py**: Use of `textSplitters`  and `document_loaders` to chunk non-public files into text packages. 
2. **langchain_embedding.py**: Use of `langchain_oci.embeddings` to perform fast embeding from given text chunks (traditional method using GenAI also available).
3. **langchain_semantic_search.py**: sample semantic search example using 23ai as knowledge base for retrival.
4. **langchain_rag_23ai.py**: full homegrown rag implementation using 23ai

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