
## Welcome to the LLM Module

In this module, we will experiment with OCI Generative AI APIs, exploring both Cohere models for advanced language tasks and OpenAI-compatible models for unified access to various hosted LLMs. We also demonstrate OCI Language service for efficient small language model tasks.

In this module, we will explore the following capabilities:
1. Basic chat functionality with Cohere models and parameter experimentation
2. Conversation history management for contextual responses
3. Streaming responses for real-time token delivery
4. Structured output generation with JSON schemas
5. OpenAI-compatible API usage with multiple model providers
6. Conversational streaming with history maintenance
7. Natural language processing with OCI Language service

## Environment Setup
- `sandbox.yaml`: Contains OCI config, compartment, and other details.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to OCI Generative AI and Language services.

## Suggested Study Order and File Descriptions
The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **cohere_chat.py**: Demonstrates basic chat functionality using OCI Generative AI with Cohere models. Shows how to make simple chat requests, configure parameters like temperature and max tokens, and experiment with different settings.
   - Key features: Parameter experimentation (temperature, max_tokens, seed), response formatting, model availability listing.
   - How to run: `uv run llm/cohere_chat.py`.
   - Docs: [OCI Gen AI Chat Models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm), [Cohere Chat API](https://docs.cohere.com/docs/chat-api).

2. **cohere_chat_history.py**: Demonstrates chat with conversation history using Cohere models. Shows how to maintain context across multiple interactions by including previous messages in chat requests.
   - Key features: Conversation history management, context-aware responses, history vs no-history comparison.
   - How to run: `uv run llm/cohere_chat_history.py`.
   - Docs: [Chat History Management](https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai-inference/20231130/ChatDetails/)

3. **cohere_chat_stream.py**: Demonstrates streaming chat responses with Cohere models. Shows how to receive responses in real-time as tokens are generated for better user experience.
   - Key features: Real-time token streaming, event processing, flush printing for smooth output.
   - How to run: `uv run llm/cohere_chat_stream.py`.
   - Docs: [Streaming Responses](https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai-inference/20231130/ChatDetails/), [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events).

4. **cohere_output_schema.py**: Demonstrates structured output generation with JSON schemas using Cohere models. Shows how to enforce specific response formats and validate outputs against schemas.
   - Key features: JSON schema constraints, multiple format comparisons (text, JSON, schema-validated), nested object handling.
   - How to run: `uv run llm/cohere_output_schema.py`.
   - Docs: [Structured Outputs](https://docs.cohere.com/docs/structured-outputs-json)

5. **openai_xai_llama_chat.py**: Demonstrates OpenAI-compatible chat using Meta Llama models through OCI. Shows unified API access to various hosted models.
   - Key features: OpenAI-compatible API usage, multiple model support (OpenAI, xAI, Meta), parameter configuration.
   - How to run: `uv run llm/openai_xai_llama_chat.py`.
   - Docs: [OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai), [Available Models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm).

6. **openai_xai_llama_chat_history.py**: Demonstrates conversational chat with history using OpenAI-compatible models. Shows context maintenance across multi-turn conversations.
   - Key features: Message history management (system, user, assistant), conversation persistence, context-aware responses.
   - How to run: `uv run llm/openai_xai_llama_chat_history.py`.


7. **openai_xai_llama_chat_stream.py**: Demonstrates streaming chat with OpenAI-compatible models. Shows real-time response generation for conversational applications.
   - Key features: Streaming event processing, token-by-token output, real-time UI enablement.
   - How to run: `uv run llm/openai_xai_llama_chat_stream.py`.
 

8. **oci_language.py**: Demonstrates OCI Language service for NLP tasks including sentiment analysis, key phrases, NER, text classification, and PII masking.
   - Key features: Multiple NLP analyses (sentiment, key phrases, NER, classification, PII), batch processing, comprehensive results display.
   - How to run: `uv run llm/oci_language.py`.
   - Docs: [OCI Language Overview](https://docs.oracle.com/en-us/iaas/language/using/home.htm),
9. **llm.ipynb**: Jupyter notebook version covering Cohere chat examples with interactive markdown explanations.
   - Key features: Interactive execution, step-by-step explanations, visual learning format.
   - How to run: Open in Jupyter or VS Code and run cells sequentially.


10. **oci-language.ipynb**: Jupyter notebook demonstrating OCI Language service with markdown explanations.
    - Key features: Interactive NLP exploration, visual results display, educational format.
    - How to run: Open in Jupyter or VS Code and run cells sequentially.
    - Docs: [OCI Language](https://docs.oracle.com/en-us/iaas/language/using/home.htm), 
## Project Ideas
Here are some ideas for projects you can build upon these examples:

1. Build a conversational AI assistant with memory:
   - Implement persistent conversation history across sessions
   - Add conversation summarization for long contexts
   - Integrate with external knowledge sources for enhanced responses
   - Resources: [LangChain Memory](https://docs.langchain.com/oss/python/langchain/memory),

2. Create a structured data extraction system:
   - Use JSON schemas to extract specific information from unstructured text
   - Build APIs that return validated, structured data
   - Implement multi-step extraction with validation and correction


3. Develop a real-time chat application:
   - Implement streaming responses for live user interaction
   - Add typing indicators and progress feedback
   - Support multiple concurrent conversations
   - 

4. Build an NLP analysis dashboard:
   - Combine multiple OCI Language analyses into comprehensive reports
   - Create visualizations for sentiment trends and entity relationships
   - Implement batch processing for large document collections


5. Create a multi-model comparison tool:
   - Compare responses across different models (Cohere, OpenAI, xAI, Meta)
   - Analyze performance, cost, and quality metrics
   - Implement A/B testing for model selection
  

## Resources and Links
- **Documentation**:
  - [OCI Generative AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  - [OCI Language Service](https://docs.oracle.com/en-us/iaas/language/using/home.htm)
  - [OpenAI Compatible SDK](https://github.com/oracle-samples/oci-openai)
  - [Cohere Documentation](https://docs.cohere.com/)

- **Slack Channels**:
  - **#generative-ai-users**: For questions on OCI Gen AI APIs and models
  - **#oci_ai_lang_service_users**: For questions on OCI Language service
  - **#igiu-innovation-lab**: General discussions on your projects
  - **#igiu-ai-learning**: Help with sandbox environment or running code
  - **#igiu-ai-accelerator-collab**: Collaboration on AI services and tools
