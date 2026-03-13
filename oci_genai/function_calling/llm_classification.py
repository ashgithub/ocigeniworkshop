"""
What this file does:
Demonstrates text classification using OCI Generative AI Cohere models. Shows how to prompt the model to classify customer questions into predefined categories using a custom preamble.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Command Models: https://docs.cohere.com/docs/command-r
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run function_calling/llm_classification.py

Important sections:
- Setup: Load config and initialize client.
- Classification: Define preamble with categories and make chat request.
- Experiment: Try different questions or modify categories in the preamble.
"""

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, CohereChatRequest, ChatDetails
import oci
import os
from dotenv import load_dotenv
from envyaml import EnvYAML

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# meta.llama-3.2-90b-vision-instruct
# meta.llama-4-maverick-17b-128e-instruct-fp8
# meta.llama-4-scout-17b-16e-instruct

LLM_MODEL = "cohere.command-a-03-2025" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

llm_client = None
llm_payload = None


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def get_chat_request():
        cohere_chat_request = CohereChatRequest()
        cohere_chat_request.preamble_override = """
        
        You are a call classifier. Carefully analyze the question and classify it into one of the following categories.
        Return only the category name in the response.
        
        categories: billing, outage, program, service
        
        eg: 
        question: can I pay my bill by credit card
        answer: billing
        question: I need to cancel my service because I am moving
        answer: service
        question: when will my power come back on?
        answer: outage
        
        """
        cohere_chat_request.is_stream = False 
        cohere_chat_request.max_tokens = 500
        cohere_chat_request.temperature = 0.75
        cohere_chat_request.top_p = 0.7
        cohere_chat_request.frequency_penalty = 1.0

        return cohere_chat_request

def get_chat_detail (llm_request,compartmentId):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail


# Set up the OCI Gen AI client based on the loaded config.
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
chat_request = get_chat_request();
llm_payload =get_chat_detail(chat_request,scfg["oci"]["compartment"])

llm_payload.chat_request.message = "why is my bill so high"

llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.text
        
print (llm_text)
