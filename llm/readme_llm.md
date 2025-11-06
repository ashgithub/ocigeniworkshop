
## Welcome to the LLM Module.
In this module, we will experiment with the OCI GenAI APIs, particularly the Cohere models.

Specifically, we will try the following capabilities:
1. Chat API for conversations and various parameters.
2. Remembering past conversations (history).
3. Processing the streaming response from LLM.
4. Enforcing the output format for LLM responses.
5. OCI Language service as an example for a small language model.

Remember to set up your `sandbox.yaml` file per your environment. This module only uses the "oci" section.

Example code in this module is available both as Jupyter notebook and Python code. They are very similar:

1. **cohere_chat.py**: Simple example on how to invoke OCI API.
2. **cohere_chat_stream.py**: Looking at how to process LLM as a stream to reduce response latency.
3. **cohere_chat_history.py**: How to remember past conversation so LLM can respond within the conversation context.
4. **cohere_output_schema.py**: Specifying JSON schema to force output to be a specified format.
5. **openai_xai_llama_chat.py**: Simple example using Llama 3-based XAI model in OCI GenAI.
6. **openai_xai_llama_chat_stream.py**: Streaming Llama-based responses via OCI GenAI.
7. **openai_xai_llama_chat_history.py**: Maintains conversation history with Llama XAI model.
8. **llm.ipynb**: Jupyter notebook version of the above.
9. **oci_language.py, oci-language.ipynb**: LLMs are slow and expensive; SLMs like OCI Language can be useful. Simple examples on how to use the OCI Language service for simple language tasks.

Here are some ideas for projects you can do (see notebook files for details):
- Create a bot that remembers the conversation.
    - e.g., Q1: What are the 5 top tourist spots in India?
    - e.g., Q2: Tell me more about the 3rd one. What's the best time to visit?
- Specify the output schema and ask the question again. Some ideas for the schema:
    - Name of tourist spot, address, best time to visit, highlights, year established, etc.
- Ask the question again and see that it returns the 5 spots in the format asked.
- Remove the schema and see if you can stream the response.

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
```
Load with `python-dotenv` if needed: `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`.
