"""
What this file does:
Demonstrates streaming chat functionality using OpenAI-compatible models through OCI Generative AI. Shows how to receive responses in real-time as tokens are generated, enabling better user experience and progressive UI updates for conversational applications.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- Streaming Responses: https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai-inference/20231130/ChatDetails/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/openai_xai_llama_chat_stream.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Configure streaming chat request.
- Step 3: Create streaming chat function.
- Step 4: Make streaming request and display results.
"""

import oci
import json
import os

from dotenv import load_dotenv
from envyaml import EnvYAML

# Step 1: Load configuration and initialize client
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available OpenAI-compatible models
CHAT_MODEL = "meta.llama-3.3-70b-instruct"
SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def create_user_message(message_text):
    """Create a user message for the conversation."""
    content = oci.generative_ai_inference.models.TextContent()
    content.text = message_text

    user_message = oci.generative_ai_inference.models.UserMessage()
    user_message.content = [content]

    return user_message


def create_streaming_chat_request():
    """Create a generic chat request configured for streaming."""
    chat_request = oci.generative_ai_inference.models.GenericChatRequest()
    chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    chat_request.num_generations = 1
    chat_request.is_stream = True  # Enable real-time streaming
    chat_request.max_tokens = 500
    chat_request.temperature = 0.75

    return chat_request


def create_chat_details(chat_request, compartment_id, model_id):
    """Create chat details payload for the OCI Generative AI API."""
    chat_details = oci.generative_ai_inference.models.ChatDetails()
    chat_details.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
    chat_details.compartment_id = compartment_id
    chat_details.chat_request = chat_request

    return chat_details


def streaming_chat(user_input, chat_client, chat_details):
    """Handle streaming chat interaction."""
    # Set the user message
    chat_details.chat_request.messages = [create_user_message(user_input)]

    # Make streaming request
    streaming_response = chat_client.chat(chat_details)

    print("🤖 Streaming Response:")
    print("-" * 30)

    # Process streaming events
    for event in streaming_response.data.events():
        event_data = json.loads(event.data)
        if 'message' in event_data and 'content' in event_data['message']:
            token_text = event_data['message']['content'][0]["text"]
            print(token_text, end='', flush=True)

    print("\n\nStreaming complete!")


# Load configuration and initialize client
config_data = load_config(SANDBOX_CONFIG_FILE)
oci_config = oci.config.from_file(
    os.path.expanduser(config_data["oci"]["configFile"]),
    config_data["oci"]["profile"]
)

chat_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=oci_config,
    service_endpoint=SERVICE_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

# Step 2: Configure streaming chat request
chat_request = create_streaming_chat_request()
chat_details = create_chat_details(chat_request, config_data["oci"]["compartment"], CHAT_MODEL)

# Step 3-4: Make streaming request and display results
streaming_chat("Tell me two things about India", chat_client, chat_details)

print("\n💡 Experimentation Ideas:")
print("- Compare streaming vs non-streaming response times")
print("- Try different user messages and observe token-by-token generation")
print("- Implement real-time UI updates based on streaming events")
print("- Test with different models to compare streaming behavior")
print("- Add conversation history while maintaining streaming")
