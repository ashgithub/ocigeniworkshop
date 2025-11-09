"""
What this file does:
Demonstrates OpenAI-compatible chat functionality using OCI Generative AI with Meta Llama models. Shows how to use the OpenAI-compatible API format to interact with various hosted models including OpenAI GPT, xAI Grok, and Meta Llama models through a unified interface.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- Available Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/openai_xai_llama_chat.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Configure chat request parameters.
- Step 3: Make chat request and display results.
- Step 4: Experiment with different models.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

import oci
import os

# Step 1: Load configuration and initialize client
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available OpenAI-compatible models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# OpenAI models:
# openai.gpt-4.1, openai.gpt-4.1-mini, openai.gpt-4.1-nano
# openai.gpt-o1, openai.gpt-o3, openai.gpt-4o, openai.gpt-4o-mini
# openai.gpt-5, openai.gpt-5-mini, openai.gpt-5-nano
# xAI Grok models:
# xai.grok-3, xai.grok-4, xai.grok-4-fast-reasoning, xai.grok-4-fast-non-reasoning
# Meta Llama models:
# meta.llama-4-maverick-17b-128e-instruct-fp8, meta.llama-4-scout-17b-16e-instruct
# meta.llama-3.2-90b-vision-instruct (used in this example)
CHAT_MODEL = "meta.llama-3.2-90b-vision-instruct"

# OCI Generative AI service endpoint for US Chicago region
SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Sample user message
USER_MESSAGE = "What is the capital of France?"


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def create_user_message(message_text):
    """Create a user message for the OpenAI-compatible API."""
    content = oci.generative_ai_inference.models.TextContent()
    content.text = message_text

    user_message = oci.generative_ai_inference.models.UserMessage()
    user_message.content = [content]

    return [user_message]


def create_chat_request(message_text):
    """Create a generic chat request for OpenAI-compatible models."""
    chat_request = oci.generative_ai_inference.models.GenericChatRequest()
    chat_request.messages = create_user_message(message_text)
    chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    chat_request.num_generations = 1
    chat_request.is_stream = False  # Set to True for streaming responses
    chat_request.max_tokens = 500  # Maximum tokens to generate
    chat_request.temperature = 0.75  # Higher values mean more random; default = 0.0
    chat_request.top_p = 0.7  # Only tokens with total probability p considered
    chat_request.top_k = -1  # -1 disables top_k sampling
    chat_request.frequency_penalty = 1.0  # Reduces token repetition

    return chat_request


def create_chat_details(chat_request, compartment_id, model_id):
    """Create chat details payload for the OCI Generative AI API."""
    chat_details = oci.generative_ai_inference.models.ChatDetails()
    chat_details.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
    chat_details.compartment_id = compartment_id
    chat_details.chat_request = chat_request

    return chat_details


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

# Step 2: Configure chat request parameters
chat_request = create_chat_request(USER_MESSAGE)
chat_payload = create_chat_details(chat_request, config_data["oci"]["compartment"], CHAT_MODEL)

# Step 3: Make chat request and display results
response = chat_client.chat(chat_payload)
generated_text = response.data.chat_response.choices[0].message.content[0].text

print("🤖 OpenAI-Compatible Chat Response:")
print("=" * 50)
print(generated_text)

# Step 4: Experiment with different models
print("\n🔄 Model Experimentation Ideas:")
print("- Try different Llama models: meta.llama-4-maverick-17b-128e-instruct-fp8")
print("- Test OpenAI models: openai.gpt-4o, openai.gpt-4o-mini")
print("- Experiment with xAI models: xai.grok-4, xai.grok-4-fast-reasoning")
print("- Adjust temperature: 0.0 for deterministic, 1.0+ for creative responses")
print("- Modify max_tokens: Try 100, 1000, or 2000 for different response lengths")
print("- Enable streaming: Set is_stream=True for real-time responses")
