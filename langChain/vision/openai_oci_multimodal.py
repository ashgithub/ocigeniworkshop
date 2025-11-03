
# Documentation: https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm
# GitHub SDK: TBD- yet not released 
# Postman collection: 
# Slack channels:#generative-ai-users or #igiu-innovation-lab
# If you have errors running sample code, reach out for help in #igiu-ai-learning
# Add parent directory to path for imports

import os
import sys

from dotenv import load_dotenv
from envyaml import EnvYAML
import base64
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from openai_oci_client import OciOpenAILangChainClient



#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd`
#####
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

MODEL_LIST = [
    "meta.llama-4-scout-17b-16e-instruct",
    "openai.gpt-4.1",
    "xai.grok-4"
]

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

MESSAGE = "tell me this image"
FILE_TO_ANALYZE = "./vision/dussera-b.jpg"

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

scfg = load_config(SANDBOX_CONFIG_FILE)
if scfg is not None and 'oci' in scfg and 'profile' in scfg['oci'] and 'compartment' in scfg['oci']:
    compartment_id = scfg["oci"]["compartment"]
    profile = scfg["oci"]["profile"]
else:
    print("Error: Invalid configuration for OCI.")
    exit(1)

for model_id in MODEL_LIST:
    banner = "=" * 80
    print(f"\n{banner}\nRESULTS FOR MODEL: {model_id}\n{banner}")
    start_time = time.time()

    llm_client = OciOpenAILangChainClient(
        profile=profile,
        compartment_id=compartment_id,
        model=model_id,
        service_endpoint=llm_service_endpoint
    )

    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": MESSAGE},
            {
               "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(FILE_TO_ANALYZE)}"
                }
            },
        ]
    }

    response = llm_client.invoke([message])
    print(response.content)

    end_time = time.time()
    print(f"{banner}\nTime taken: {end_time - start_time:.2f} seconds\n")
