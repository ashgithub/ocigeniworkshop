## Welcome to the Database Module

In this module you’ll explore how Oracle Autonomous Database (23ai) and **Select AI** enable Large Language Model (LLM) workflows ​directly inside the database and how to combine them with Retrieval-Augmented Generation (RAG).

### What you will try

1. **Natural-Language-to-SQL (NL2SQL)** – Ask questions in plain English and let the database generate and execute the SQL for you.  
2. **Select AI** – Compare “inline LLM” SQL (`SELECT AI …`) with external LLM calls.  
3. **Database-centric RAG** – Use SQL and Embeddings stored in the database to build a full RAG pipeline that returns citations.  
4. **Hybrid RAG** – Orchestrate Select AI with OCI GenAI to blend structured and unstructured knowledge.

---

### Environment setup

1. Download the **ADB / 23ai wallet** and unzip it locally.  
2. In **sandbox.yaml** populate the `db` section (wallet directory, user, password, service name, prefix).  
3. Verify `oci` section is complete (needed for embedding generation or bucket staging).  
4. Optional: add sensitive values to `.env` and load them with `python-dotenv`.

---

### Example code

| Task | Script / Notebook |
|------|-------------------|
| NL2SQL demo with Select AI | `nl2sql_demo.py` |
| Pure Select AI examples (inline SQL) | `selectai.sql` |
| Full RAG in 23ai (embeddings, similarity search, citations) | `rag.sql` |

Run SQL files with SQLcl or SQL Developer.  
Run Python with `python database/nl2sql_demo.py`.

---

### Project ideas

* Build a **“Chat with my tables”** app – automatic schema discovery, Select AI for structured Q&A, plus GenAI summarisation.  
* Store vector embeddings in 23ai, create an **in-database semantic search** view, then connect it to OCI GenAI for answers with citations.  
* Compare cost / latency of Select AI versus external LLM calls for the same NL prompt workload.

---

### Helpful links

* Slack **#adb-select-ai-users** – questions on Select AI.  
* Slack **##ww-autonomous-int** - questions on autonomous database
* Slack **#generative-ai-users** – OCI GenAI discussions. 
* Slack **#igiu-innovation-lab** – project ideas  
* Slack **#igiu-ai-learning** – help with code or environment issues   
* Docs: <https://docs.oracle.com/en/cloud/paas/autonomous-database/select-ai/>  

---


