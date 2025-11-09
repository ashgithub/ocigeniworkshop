
"""
What this file does:
Demonstrates multimodal LLM capabilities using OCI Generative AI models to analyze images. It encodes an image in base64, sends it to different models with a text prompt, and compares responses.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai  note: supports OpenAI, XAI & Meta models. Also supports OpenAI Responses API
- LangChain: https://docs.langchain.com/oss/python/langchain/overview

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and profile details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/vision/openai_oci_multimodal.py

Comments to important sections of file:
- Step 1: Load config and initialize clients.
- Step 2: Define models and image to analyze.
- Step 3: Encode image to base64.
- Step 4: Loop through models, send multimodal prompt, and measure response time.
- Experimentation: Try changing USER_PROMPT_TEXT to ask different questions about the image, or use a different IMAGE_FILE_PATH.
"""

import os
import sys
import base64
import time

from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from oci_openai_helper import OCIOpenAIHelper

# Step 1: Load config and initialize clients
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

sandbox_config = load_config(SANDBOX_CONFIG_FILE)
if sandbox_config is not None and 'oci' in sandbox_config and 'profile' in sandbox_config['oci'] and 'compartment' in sandbox_config['oci']:
    compartment_id = sandbox_config["oci"]["compartment"]
    profile = sandbox_config["oci"]["profile"]
else:
    print("Error: Invalid configuration for OCI.")
    exit(1)

# Step 2: Define models and image to analyze
MODEL_LIST = [
    "meta.llama-4-scout-17b-16e-instruct",
    "openai.gpt-4.1",
    "xai.grok-4"
]

USER_PROMPT_TEXT = "tell me about this image"
IMAGE_FILE_PATH = "./vision/dussera-b.jpg"

# Step 3: Encode image to base64
def encode_image_to_base64(image_path):
    """Encode an image file to base64 string for API transmission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Step 4: Loop through models, send multimodal prompt, and measure response time
for model_id in MODEL_LIST:
    banner = "=" * 80
    print(f"\n{banner}\nRESULTS FOR MODEL: {model_id}\n{banner}")
    start_time = time.time()

    llm_client = OCIOpenAIHelper.get_client(
        model_name=model_id,
        config=sandbox_config
        )

    encoded_image = encode_image_to_base64(IMAGE_FILE_PATH)
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": USER_PROMPT_TEXT},
            {
               "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            },
        ]
    }

    response = llm_client.invoke([message])
    print(response.content)

    end_time = time.time()
    print(f"{banner}\nTime taken: {end_time - start_time:.2f} seconds\n")

# Experimentation suggestions:
# - Change USER_PROMPT_TEXT to "describe the colors in this image" or "what objects do you see?"
# - Try a different IMAGE_FILE_PATH, e.g., "./langChain/vision/receipt.png" (make sure the file exists)
# - Add more models to MODEL_LIST to compare different capabilities
