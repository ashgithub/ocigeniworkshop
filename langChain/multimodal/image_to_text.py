
"""
What this file does:
Demonstrates multimodal image analysis with OCI-hosted models. It encodes an
image in base64, sends it with a text prompt to several models, and compares
their responses.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai
- LangChain: https://docs.langchain.com/oss/python/langchain/overview

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and profile details.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/multimodal/image_to_text.py

Important sections:
- Step 1: Load configuration and initialize the client
- Step 2: Define the models and input image
- Step 3: Encode the image to base64
- Step 4: Invoke each model and compare responses
"""

import base64
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from oci_openai_helper import OCIOpenAIHelper

# Step 1: Load config and initialize clients
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

sandbox_config = load_config(SANDBOX_CONFIG_FILE)
if sandbox_config is None or 'oci' not in sandbox_config or 'profile' not in sandbox_config['oci']:
    print("Error: Invalid configuration for OCI.")
    exit(1)

# Step 2: Define models and image to analyze
MODEL_LIST = [
    "meta.llama-4-scout-17b-16e-instruct",
    "openai.gpt-4.1",
    "xai.grok-4"
]

USER_PROMPT_TEXT = "Tell me about this image."
IMAGE_FILE_PATH = str(Path("langChain/multimodal/otter.png"))

# Step 3: Encode image to base64
def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string for API transmission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Step 4: Loop through models, send multimodal prompt, and measure response time
for model_id in MODEL_LIST:
    banner = "=" * 80
    print(f"\n{banner}\nRESULTS FOR MODEL: {model_id}\n{banner}")
    start_time = time.time()

    llm_client = OCIOpenAIHelper.get_langchain_openai_client(
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
# - Change USER_PROMPT_TEXT to "Describe the colors in this image" or "What objects do you see?"
# - Try a different IMAGE_FILE_PATH, such as another image in this folder
# - Add more models to MODEL_LIST to compare capabilities
