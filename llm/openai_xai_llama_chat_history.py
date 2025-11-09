"""
What this file does:
Demonstrates conversational chat with history using OpenAI-compatible models through OCI Generative AI. Shows how to maintain conversation context across multiple interactions by building and managing message history with system, user, and assistant messages.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- Chat History: https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai-inference/20231130/ChatDetails/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/openai_xai_llama_chat_history.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Set up conversation history with system message.
- Step 3: Create functions for managing different message types.
- Step 4: Implement conversational chat function.
- Step 5: Demonstrate multi-turn conversation.
"""

import oci
import os

from dotenv import load_dotenv
from envyaml import EnvYAML

# Step 1: Load configuration and initialize client
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available OpenAI-compatible models
CHAT_MODEL = "meta.llama-3.3-70b-instruct"
SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Global conversation history (maintains context across interactions)
conversation_history = []


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def create_system_message(message_text):
    """Create a system message to set assistant behavior."""
    content = oci.generative_ai_inference.models.TextContent()
    content.text = message_text

    system_message = oci.generative_ai_inference.models.SystemMessage()
    system_message.content = [content]

    return system_message


def create_assistant_message(message_text):
    """Create an assistant message for conversation history."""
    content = oci.generative_ai_inference.models.TextContent()
    content.text = message_text

    assistant_message = oci.generative_ai_inference.models.AssistantMessage()
    assistant_message.content = [content]

    return assistant_message


def create_user_message(message_text):
    """Create a user message for the conversation."""
    content = oci.generative_ai_inference.models.TextContent()
    content.text = message_text

    user_message = oci.generative_ai_inference.models.UserMessage()
    user_message.content = [content]

    return user_message


def create_chat_request():
    """Create a generic chat request for conversational AI."""
    chat_request = oci.generative_ai_inference.models.GenericChatRequest()
    chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    chat_request.num_generations = 1
    chat_request.is_stream = False  # Set to True for streaming responses
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


def conversational_chat(user_input, chat_client, chat_details):
    """Handle a conversational turn, maintaining history."""
    # Add user message to history
    conversation_history.append(create_user_message(user_input))

    # Update chat request with current history
    chat_details.chat_request.messages = conversation_history

    # Make the API call
    response = chat_client.chat(chat_details)
    generated_text = response.data.chat_response.choices[0].message.content[0].text

    # Add assistant response to history
    conversation_history.append(create_assistant_message(generated_text))

    return generated_text


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

# Step 2: Set up conversation history with system message
conversation_history.append(
    create_system_message("Provide a brief answer in 2-3 sentences.")
)

# Initialize chat components
chat_request = create_chat_request()
chat_details = create_chat_details(chat_request, config_data["oci"]["compartment"], CHAT_MODEL)

# Step 3-5: Demonstrate multi-turn conversation
print("🤖 Conversational Chat with History:")
print("=" * 50)

# First turn
user_question_1 = "Tell me two things about India in bullets"
print(f"User: {user_question_1}")
response_1 = conversational_chat(user_question_1, chat_client, chat_details)
print(f"Assistant: {response_1}")
print("-" * 30)

# Second turn (maintains context from first interaction)
user_question_2 = "Tell me more about the second thing"
print(f"User: {user_question_2}")
response_2 = conversational_chat(user_question_2, chat_client, chat_details)
print(f"Assistant: {response_2}")

print("\n💡 Experimentation Ideas:")
print("- Add more conversation turns to see context retention")
print("- Try different system messages to change assistant behavior")
print("- Test with different models to compare conversation quality")
print("- Implement conversation persistence (save/load history)")
print("- Add conversation length limits to manage token usage")
