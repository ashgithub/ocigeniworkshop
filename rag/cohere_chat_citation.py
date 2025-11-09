"""
What this file does:
Demonstrates how to pass custom documents to OCI Generative AI (Cohere models) for chat responses with citations. This is a basic form of RAG without external storage—documents are provided directly in the request.

Documentation to reference:
- OCI GenAI Chat: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- Cohere Documents and Citations: https://docs.cohere.com/docs/documents
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference

Relevant slack channels:
- #generative-ai-users: For questions on OCI GenAI
- #igiu-innovation-lab: General discussions on projects
- #igiu-ai-learning: Help with sandbox environment or running this code

Env setup:
- sandbox.yaml: Ensure "oci" section has configFile and profile set.
- .env: Loaded for any additional variables.

How to run the file:
uv run rag/cohere_chat_citation.py

Comments to important sections of file:
- Step 1: Import dependencies and define constants.
- Step 2: Load configuration and set up OCI client.
- Step 3: Define helper functions for chat requests and details.
- Step 4: Prepare documents and chat history (optional).
- Step 5: Build and send chat request, print response with citations.
- Experiment: Try different messages (uncomment examples), add/remove documents, adjust citation_quality (FAST vs ACCURATE), or include chat_history for context.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

# Step 1: Import OCI dependencies
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    OnDemandServingMode, 
    CohereChatRequest, 
    ChatDetails
)
import oci
import os

# Constants
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

COHERE_MODEL_ID = "cohere.command-a-03-2025"  # Other options: cohere.command-r-08-2024, cohere.command-r-plus-08-2024
INFERENCE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Step 2: Load configuration and initialize OCI client
def load_configuration(config_file_path):
    """Load sandbox configuration from YAML file."""
    try:
        return EnvYAML(config_file_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file_path}' not found.")
        return None

sandbox_config = load_configuration(SANDBOX_CONFIG_FILE)
if sandbox_config is None:
    raise RuntimeError("Failed to load sandbox configuration.")

oci_config = oci.config.from_file(
    os.path.expanduser(sandbox_config["oci"]["configFile"]), 
    sandbox_config["oci"]["profile"]
)

inference_client = GenerativeAiInferenceClient(
    config=oci_config,
    service_endpoint=INFERENCE_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

compartment_id = sandbox_config["oci"]["compartment"]

# Step 3: Helper functions to build chat requests and details
def create_chat_request(message, documents=None, use_history=False, citation_quality="FAST"):
    """Create a Cohere chat request with optional documents and history."""
    chat_request = CohereChatRequest()
    chat_request.preamble_override = (
        "Provide factual answers based on the provided documents. "
        "Include citations if possible. If the answer is not in the documents, say so."
    )
    chat_request.message = message
    chat_request.is_stream = False
    chat_request.max_tokens = 500  # Adjust for longer/shorter responses
    chat_request.temperature = 0.75  # Higher = more random (default 0.3)
    chat_request.top_p = 0.7  # Nucleus sampling (default 0.75)
    chat_request.frequency_penalty = 1.0  # Reduces repetition (max 1.9)
    
    if documents:
        chat_request.documents = documents  # Restricts response to these docs
    
    if use_history:
        chat_request.chat_history = get_chat_history()
    
    chat_request.citation_quality = (
        CohereChatRequest.CITATION_QUALITY_FAST if citation_quality == "FAST" 
        else CohereChatRequest.CITATION_QUALITY_ACCURATE
    )
    
    return chat_request

def create_chat_details(chat_request):
    """Create chat details for OCI inference."""
    details = ChatDetails()
    details.serving_mode = OnDemandServingMode(model_id=COHERE_MODEL_ID)
    details.compartment_id = compartment_id
    details.chat_request = chat_request
    return details

# Step 4: Define sample documents and optional chat history
def get_sample_documents():
    """Return sample documents for citation testing."""
    return [
        {
            "title": "Oracle",
            "snippet": (
                "Oracle database services and products offer customers cost-optimized and high-performance "
                "versions of Oracle Database, the world's leading converged, multi-model database management "
                "system, as well as in-memory, NoSQL and MySQL databases. Oracle Autonomous Database, "
                "available on premises via Oracle Cloud@Customer or in the Oracle Cloud Infrastructure, "
                "enables customers to simplify relational database environments and reduce management workloads."
            ),
            "website": "https://www.oracle.com/database",
            "id": "ORA001"
        },
        {
            "title": "Amazon",
            "snippet": (
                "AWS provides the broadest selection of purpose-built databases allowing you to save, grow, "
                "and innovate faster. Purpose Built: Choose from 15+ purpose-built database engines including "
                "relational, key-value, document, in-memory, graph, time series, wide column, and ledger databases. "
                "Performance at Scale: Get relational databases that are 3-5X faster than popular alternatives, "
                "or non-relational databases that give you microsecond to sub-millisecond latency. "
                "Fully Managed: AWS continuously monitors your clusters to keep your workloads running with "
                "self-healing storage and automated scaling, so that you can focus on application development. "
                "Secure & Highly Available: AWS databases are built for business-critical, enterprise workloads, "
                "offering high availability, reliability, and security."
            ),
            "website": "https://aws.amazon.com/free/database/e",
            "id": "AWS001"
        }
    ]

def get_chat_history():
    """Optional chat history for context-aware responses."""
    from oci.generative_ai_inference.models import CohereUserMessage, CohereChatBotMessage
    user_message = CohereUserMessage(message="Tell me something about Oracle.")
    bot_reply = CohereChatBotMessage(
        message="Oracle is one of the largest vendors in the enterprise IT market and the shorthand name "
                "of its flagship product. The database software sits at the center of many corporate IT"
    )
    return [user_message, bot_reply]

# Step 5: Main execution - Send chat request and print results
documents = get_sample_documents()

# Experiment: Choose a message below (uncomment one)
# message = "Tell me about Ashish?"  # Should use Oracle doc and cite it
# message = "Tell me about Oracle's databases"  # Should cite Oracle snippet
message = "Tell me about Amazon's databases"  # Should cite AWS snippet
# message = "Tell me about its databases"  # With history: Refers to previous Oracle context

chat_request = create_chat_request(
    message=message, 
    documents=documents, 
    use_history=False,  # Set to True to test history
    citation_quality="FAST"  # Or "ACCURATE" for better but slower citations
)

chat_details = create_chat_details(chat_request)

response = inference_client.chat(chat_details)

# Print the response and citations
print("************************** Chat Response **************************")
print(response.data.chat_response.text)
print("\n************************** Citations **************************")
print(response.data.chat_response.citations)

# Experiment suggestions:
# 1. Change COHERE_MODEL_ID to another Cohere model and compare responses.
# 2. Modify temperature (0.3 for factual, 1.0 for creative) or top_p to see variation.
# 3. Add your own documents (e.g., from a PDF snippet) and query about them.
# 4. Enable use_history=True and use a follow-up message to test conversation flow.
# 5. Set citation_quality="ACCURATE" for more precise citations (may be slower).
