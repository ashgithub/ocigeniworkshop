"""
What this file does:
Demonstrates streaming chat functionality using OCI Generative AI with Cohere models. Shows how to receive responses in real-time as tokens are generated, providing a better user experience for longer responses and enabling progressive UI updates.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- Streaming Responses: https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai-inference/20231130/ChatDetails/
- Server-Sent Events: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/cohere_chat_stream.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Configure streaming chat request.
- Step 3: Make streaming chat request.
- Step 4: Process streaming events and display results.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, CohereChatRequest, ChatDetails
import oci
import json
import os

# Step 1: Load configuration and initialize client
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available Cohere chat models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
CHAT_MODEL = "cohere.command-r-08-2024"

# OCI Generative AI service endpoint for US Chicago region
SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Sample preamble to override the model's default behavior
PREAMBLE_OVERRIDE = """
You always answer in a one stanza poem.
"""

# Sample user message
USER_MESSAGE = """
Why is the sky blue?
"""


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def create_streaming_chat_request():
    """Create a Cohere chat request configured for streaming responses."""
    chat_request = CohereChatRequest()
    chat_request.preamble_override = PREAMBLE_OVERRIDE
    chat_request.message = USER_MESSAGE
    chat_request.is_stream = True  # Enable streaming for real-time token delivery
    chat_request.max_tokens = 500  # Maximum tokens to generate
    chat_request.temperature = 1.0  # Higher values mean more random; default = 0.3
    chat_request.seed = 7555  # Makes best effort for deterministic responses
    chat_request.top_p = 0.7  # Only tokens with total probability p considered
    chat_request.top_k = 0  # Only top k tokens considered; 0 turns it off
    chat_request.frequency_penalty = 0.0  # Reduces token repetition

    return chat_request


def create_chat_details(chat_request, compartment_id):
    """Create chat details payload for the OCI Generative AI API."""
    chat_details = ChatDetails()
    chat_details.serving_mode = OnDemandServingMode(model_id=CHAT_MODEL)
    chat_details.compartment_id = compartment_id
    chat_details.chat_request = chat_request

    return chat_details


# Load configuration and initialize client
config_data = load_config(SANDBOX_CONFIG_FILE)
oci_config = oci.config.from_file(
    os.path.expanduser(config_data["oci"]["configFile"]),
    config_data["oci"]["profile"]
)

chat_client = GenerativeAiInferenceClient(
    config=oci_config,
    service_endpoint=SERVICE_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

# Step 2: Configure streaming chat request
chat_request = create_streaming_chat_request()
chat_payload = create_chat_details(chat_request, config_data["oci"]["compartment"])

# Step 3: Make streaming chat request
streaming_response = chat_client.chat(chat_payload)

# Step 4: Process streaming events and display results
print("************************** Streaming Chat Response **************************")
print("Response (streaming in real-time):")

for event in streaming_response.data.events():
    event_data = json.loads(event.data)

    # Check if the stream has finished
    if 'finishReason' in event_data:
        print(f"\n\nFinish reason: {event_data['finishReason']}")
        break

    # Print the generated text as it arrives
    if 'text' in event_data:
        print(event_data['text'], end="", flush=True)

    # Optional: Add timestamps for debugging
    # import datetime
    # print(f"{datetime.datetime.now()} {event_data}")

print("\n\nStreaming complete!")

# Additional experimentation ideas:
# - Compare streaming vs non-streaming response times
# - Try different max_tokens values to see how streaming handles long responses
# - Experiment with different temperatures to observe real-time creativity changes
# - Implement progress indicators or UI updates based on streaming events
# - Handle streaming in web applications using Server-Sent Events (SSE)
