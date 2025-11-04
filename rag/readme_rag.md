
## Welcome to the RAG (Retrieval Augmented Generation) Module.

In this module, we will experiment with the LLM ability to answer questions using proprietary data.

In this module, we will look at the following abilities:
1. "Documents" attribute of OCI GenAI API and ability for citations.
2. Using OCI Agents for "off-the-shelf" RAG ability.
3. Leveraging 23ai database for home-grown RAG.
4. Introduction to Select AI.
5. Select AI with RAG.

[link](https://)

Remember to set up your `sandbox.yaml` file per your environment. This module only uses the "oci" and "db" sections.

Oracle 23ai database is used in this module; refer to [this page](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW).
- The database requires the wallet to be downloaded.
- Remember to update the database section per your setup in `sandbox.yaml`.
- As the database schema is shared, set a unique `prefix` in the database section of `sandbox.yaml`. Your Oracle user ID is a good choice.

Example code in this module is available both as Jupyter notebook and Python code. They are very similar:

1. **cohere_chat_citation.py, RAG-documents.ipynb**: Use of `documents` to pass non-public text to LLM and see a response with citations based on it.
2. **oci_rag_agents.py, RAG-agents.ipynb**: Leverage OCI GenAI Agent service for an out-of-the-box agent (see rag_agents.md for setup).
3. **cohere_rag_23ai.py, RAG-full.ipynb**: Full home-grown RAG implementation using 23ai.
4. **select_ai.sql**: SQL script to demonstrate SelectAI capability.
5. **rag.sql**: SQL script for doing full RAG in database.



Here are some ideas for projects you can do (see notebook files for details):

1. Create a "talk to my document" application by hand.
    - Allow user to upload the docs.
    - Parse and chunk the doc using various chunking strategies (semantic chunking is advised; search the net for different approaches).
    - Try different algorithms for similarity search. COSINE is popular, but Euclidean, Dot Product, etc., are also common.
    - Try rerankers to see if your retrieved documents were reordered.
    - Include citations in your response.

Here are a few Slack channels to help you:

- **#igiu-innovation-lab**: Discuss project ideas.
- **#igiu-ai-learning**: If you have issues with environment or can't get your code to work.
- **#generative-ai-users**: Questions about OCI GenAI.
- **#adb-select-ai-users**: Questions about Oracle 23ai Select AI.

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml`.

Example `.env`:
```
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
```
Load with `python-dotenv` if needed: `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`.
