import time
import sys
import os
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai_oci_client import OciOpenAILangChainClient

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#
#
#  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
#  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
#  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
#  if you have errors running sample code reach out for help in #igiu-ai-learning
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"
llm_service_endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

MESSAGE = """
    why is the sky blue? explain in 2 sentences like I am 5
"""

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

selected_llms = [
    "openai.gpt-4.1",
    "openai.gpt-5",
#    "cohere.command-a-03-2025",      # cohere doesnt support openAi compaitable APIs yet 
#    "cohere.command-r-08-2024",      # cohere doesnt support openAi compaitable APIs yet 
    "meta.llama-4-maverick-17b-128e-instruct-fp8",
    "meta.llama-4-scout-17b-16e-instruct",
    "xai.grok-4",
    "xai.grok-4-fast-non-reasoning"
]

def make_client(model_id):
    return OciOpenAILangChainClient(
        profile=scfg['oci']['profile'],
        compartment_id=scfg['oci']['compartment'],
        model=model_id,
        service_endpoint=llm_service_endpoint
    )

if __name__ == "__main__":
    for model_id in selected_llms:
        client = make_client(model_id)

        print(f"\n**************************Chat Result (invoke) for {model_id} **************************")
        start = time.perf_counter()
        response = client.invoke(MESSAGE)
        print(response.content)
        print(f"\nInvoke done in {time.perf_counter() - start:.2f}s")

        print(f"\n**************************Chat Stream Result (stream) for {model_id} **************************")
        start = time.perf_counter()
        for chunk in client.stream(MESSAGE):
            if hasattr(chunk, 'additional_kwargs') and 'finish_reason' in chunk.additional_kwargs:
                print(f"\nFinish Reason: {chunk.additional_kwargs['finish_reason']}")
                break
            print(getattr(chunk, 'content', ''), end='', flush=True)
        print(f"\nStream done in {time.perf_counter() - start:.2f}s")
