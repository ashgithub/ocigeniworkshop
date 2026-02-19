"""
What this file does:
Demonstrates basic chat functionality using OCI Generative AI with Cohere models. Shows how to make a simple chat request, configure parameters like temperature and max tokens, and experiment with different settings for reproducible results.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models
- Cohere Chat Response: https://github.com/oracle/oci-python-sdk/blob/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/generative_ai_inference/models/cohere_chat_response.py

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/cohere_chat.py

Comments to important sections of file:
- Step 1: Load configuration and initialize client.
- Step 2: Configure chat request parameters.
- Step 3: Make chat request and display results.
- Step 4: Experiment with different seeds for reproducibility.
- Step 5: Experiment with max tokens parameter.
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


def create_chat_request():
    """Create a Cohere chat request with specified parameters."""
    chat_request = CohereChatRequest()
    chat_request.preamble_override = PREAMBLE_OVERRIDE
    chat_request.message = USER_MESSAGE
    chat_request.is_stream = False  # Set to True for streaming responses
    chat_request.max_tokens = 500  # Maximum tokens to generate; can lead to incomplete responses if too low
    chat_request.temperature = 1.0  # Higher values mean more random; default = 0.3
    chat_request.seed = 7555  # Makes best effort for deterministic responses; not guaranteed
    chat_request.top_p = 0.7  # Only tokens with total probability p are considered; max=0.99, min=0.01, default=0.75
    chat_request.top_k = 0  # Only top k tokens considered; 0 turns it off, max=500
    chat_request.frequency_penalty = 0.0  # Reduces token repetition; max=1.0, min=0.0

    return chat_request


def create_chat_details(chat_request, compartment_id):
    """Create chat details payload for the OCI Generative AI API."""
    chat_details = ChatDetails()
    chat_details.serving_mode = OnDemandServingMode(model_id=CHAT_MODEL)
    chat_details.compartment_id = compartment_id
    chat_details.chat_request = chat_request

    return chat_details

config_data = load_config(SANDBOX_CONFIG_FILE)

# Load OCI configuration
oci_config = oci.config.from_file(
    os.path.expanduser(config_data["oci"]["configFile"]),
    config_data["oci"]["profile"]
)

# Initialize the Generative AI client
chat_client = GenerativeAiInferenceClient(
    config=oci_config,
    service_endpoint=SERVICE_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

# Step 2: Configure chat request parameters
chat_request = create_chat_request()
chat_payload = create_chat_details(chat_request, config_data["oci"]["compartment"])

# Step 3: Make chat request and display results
response = chat_client.chat(chat_payload)

print(f"************************** Chat Result (Seed: {chat_request.seed}) **************************")
generated_text = response.data.chat_response.text
print(generated_text)

# Step 4: Experiment with different seeds for reproducibility
chat_request.seed = 7555  # Try changing this value to see if we can reproduce the original response
print(f"\n************************** Chat Result (Seed: {chat_request.seed}) **************************")
response = chat_client.chat(chat_payload)
generated_text = response.data.chat_response.text
print(f"Finish reason: {response.data.chat_response.finish_reason}")
print(generated_text)

# Step 5: Experiment with max tokens parameter
print(f"\n************************** Chat Result (Max tokens: {chat_request.max_tokens}) **************************")
chat_request.max_tokens = 10  # Try different values (e.g., 50, 100, 1000) to see how response length changes
response = chat_client.chat(chat_payload)
generated_text = response.data.chat_response.text
print(f"Finish reason: {response.data.chat_response.finish_reason}")
print(generated_text)

# Additional experimentation ideas:
# - Try different temperatures (0.0 for deterministic, 2.0 for very random)
# - Experiment with top_p values (0.1 for focused, 0.9 for diverse)
# - Test different preamble overrides to change model behavior
# - Try different chat models from the available list
