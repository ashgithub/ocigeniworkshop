"""
What this file does:
Demonstrates chat functionality with conversation history using OCI Generative AI Cohere models. Shows how to maintain context across multiple interactions by including previous messages in the chat request, enabling more coherent and context-aware responses.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
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
uv run llm/cohere_chat_history.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Set up conversation history.
- Step 3: Configure chat request with history.
- Step 4: Make chat request and display results.
- Step 5: Experiment with and without history.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, CohereChatRequest, ChatDetails
import oci
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

# Preamble to instruct the model on how to respond based on conversation history
PREAMBLE_OVERRIDE = """
Answer the questions in a professional tone, based on the conversation history.
"""

# Current user message (will be set later)
CURRENT_MESSAGE = ""


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def create_sample_history():
    """Create sample conversation history for demonstration.

    In a real application, you would build this history from actual user interactions.
    History should be provided as pairs: user message followed by bot response.
    """
    # Previous user message
    user_message = oci.generative_ai_inference.models.CohereUserMessage(
        message="Tell me something about Oracle."
    )

    # Previous bot response
    bot_response = oci.generative_ai_inference.models.CohereChatBotMessage(
        message="Oracle is one of the largest vendors in the enterprise IT market and the shorthand name of its flagship product. The database software sits at the center of many corporate IT infrastructures."
    )

    return [user_message, bot_response]


def create_chat_request_with_history():
    """Create a Cohere chat request that includes conversation history."""
    chat_request = CohereChatRequest()
    chat_request.preamble_override = PREAMBLE_OVERRIDE
    chat_request.message = CURRENT_MESSAGE
    chat_request.is_stream = False  # Set to True for streaming responses
    chat_request.max_tokens = 500  # Maximum tokens to generate
    chat_request.temperature = 1.0  # Higher values mean more random; default = 0.3
    chat_request.seed = 7555  # Makes best effort for deterministic responses
    chat_request.top_p = 0.7  # Only tokens with total probability p considered
    chat_request.top_k = 0  # Only top k tokens considered; 0 turns it off
    chat_request.frequency_penalty = 0.0  # Reduces token repetition
    chat_request.chat_history = create_sample_history()  # Include conversation history

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

# Step 2: Set up conversation history
# (Handled in create_sample_history function)

# Step 3: Configure chat request with history
chat_request = create_chat_request_with_history()
chat_request.message = "What is its flagship product?"  # This refers to "it" from the history

chat_payload = create_chat_details(chat_request, config_data["oci"]["compartment"])

# Step 4: Make chat request and display results
response = chat_client.chat(chat_payload)

print("************************** Chat Result with History **************************")
generated_text = response.data.chat_response.text
print(generated_text)

# Step 5: Experiment with and without history
print("\n************************** Experiment: Without History **************************")
# Comment out the next line to see how the response changes without context
chat_request.chat_history = None  # Remove history
response_no_history = chat_client.chat(chat_payload)
print("Response without history:")
print(response_no_history.data.chat_response.text)

# Additional experimentation ideas:
# - Try different conversation histories to see how context affects responses
# - Add more message pairs to the history for longer conversations
# - Experiment with different preamble instructions for varied response styles
# - Test how the model handles ambiguous pronouns ("it", "they") with and without history
