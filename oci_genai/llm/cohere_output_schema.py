"""
What this file does:
Demonstrates structured output generation using OCI Generative AI with Cohere models and JSON schemas. Shows how to enforce specific response formats, validate outputs against schemas, and generate structured data like lists and nested objects.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- Structured Outputs: https://docs.cohere.com/docs/structured-outputs-json
- JSON Schema: https://json-schema.org/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run llm/cohere_output_schema.py

Important sections:
- Step 1: Load configuration and initialize client.
- Step 2: Define JSON schemas for structured output.
- Step 3: Configure chat request with different response formats.
- Step 4: Make requests and compare different output formats.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    OnDemandServingMode, CohereChatRequest, ChatDetails,
    CohereResponseTextFormat, CohereResponseJsonFormat
)
import oci
import json
import os

# Step 1: Load configuration and initialize client
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available Cohere chat models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# Note: Response schema is only supported for Cohere models from 08-2024 and later
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
CHAT_MODEL = "cohere.command-a-03-2025"

# OCI Generative AI service endpoint for US Chicago region
SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Preamble instructing the model to respond in JSON format
PREAMBLE_OVERRIDE = """
Answer in JSON only.
"""

# User message requesting structured data
USER_MESSAGE = """
Generate a list of 3 science fiction books.
"""


def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


# Step 2: Define JSON schemas for structured output
# Simple schema for a single book object
SIMPLE_BOOK_SCHEMA = {
    "type": "object",
    "required": ["title", "author", "publication_year"],
    "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "publication_year": {"type": "integer"},
    },
}

# Complex schema for an array of books with nested author objects
NESTED_BOOK_SCHEMA = {
    "type": "object",
    "required": ["authors"],  # Note: schema requires "authors" but we asked for books
    "properties": {
        "authors": {  # This schema expects "authors" array but message asks for books
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "author", "publication_year"],
                "properties": {
                    "title": {"type": "string"},
                    "author": {
                        "type": "object",
                        "required": ["fname", "lname"],
                        "properties": {
                            "fname": {"type": "string"},
                            "lname": {"type": "string"}
                        }
                    },
                    "publication_year": {"type": "integer"}
                }
            }
        }
    }
}


def create_chat_request(response_format=None):
    """Create a Cohere chat request with specified response format."""
    chat_request = CohereChatRequest()
    chat_request.preamble_override = PREAMBLE_OVERRIDE
    chat_request.message = USER_MESSAGE
    chat_request.is_stream = False  # Streaming not supported with structured output
    chat_request.max_tokens = 500  # Maximum tokens to generate
    chat_request.temperature = 1.0  # Higher values mean more random
    chat_request.seed = 7555  # Makes best effort for deterministic responses
    chat_request.top_p = 0.7  # Only tokens with total probability p considered
    chat_request.top_k = 0  # Only top k tokens considered; 0 turns it off
    chat_request.frequency_penalty = 0.0  # Reduces token repetition

    # Set response format (text, JSON, or JSON with schema)
    chat_request.response_format = response_format or CohereResponseTextFormat()

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
    timeout=(10, 30)
)

# Step 3: Configure chat request with different response formats
# Step 4: Make requests and compare different output formats

def run_format_test(title, response_format, note=None):
    """Run one response-format test and keep the workshop script moving."""

    print(f"\n************************** {title} **************************", flush=True)
    if note:
        print(note, flush=True)
    chat_request = create_chat_request(response_format)
    chat_payload = create_chat_details(chat_request, config_data["oci"]["compartment"])
    try:
        response = chat_client.chat(chat_payload)
    except Exception as exc:
        print(f"SKIPPED: response format unavailable or timed out for {CHAT_MODEL}.", flush=True)
        print(f"Reason: {exc}", flush=True)
        return
    print("Response:", response.data.chat_response.text, flush=True)


run_format_test(
    "Test 1: Text format with JSON instruction in preamble",
    CohereResponseTextFormat(),
)
run_format_test(
    "Test 2: JSON format without schema",
    CohereResponseJsonFormat(),
)
run_format_test(
    "Test 3: JSON format with simple schema",
    CohereResponseJsonFormat(schema=SIMPLE_BOOK_SCHEMA),
    "Note: Schema restricts to single object, even though we asked for 3 books",
)
run_format_test(
    "Test 4: JSON format with nested schema",
    CohereResponseJsonFormat(schema=NESTED_BOOK_SCHEMA),
    "Note: This schema expects 'authors' array but message asks for 'books' - demonstrates schema constraints",
)

# Additional experimentation ideas:
# - Create schemas that match your data requirements exactly
# - Try different schema constraints (required fields, data types, nested structures)
# - Experiment with array schemas for generating lists
# - Use structured output for API responses or data validation
# - Compare schema enforcement vs prompt-based formatting
