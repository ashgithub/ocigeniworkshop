import os
import sys
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper
from langchain_core.messages import HumanMessage

#####
# List of available models (uncomment/change LLM_MODEL as needed)
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# openai.gpt-4.1
# openai.gpt-4o
# xai.grok-4
# xai.grok-3
# xai.grok-4-fast-non-reasoning
LLM_MODEL = "xai.grok-4-fast-non-reasoning"

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
llm_service_endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


load_dotenv()

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)



questions = [
    "Tell me something about Oracle",
    "What are some key insights of the actual products?",
    "Which is the company we are talking about?"
]

if __name__ == "__main__":
    client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
    )

    print("\n====== WITHOUT History (Stateless each turn) ======")
    for idx, q in enumerate(questions):
        user_msg = HumanMessage(q)
        response = client.invoke([user_msg])
        print(f"\nUSER {idx+1}: {q}")
        print(f"RESPONSE {idx+1}: {getattr(response, 'content', response)}")

    print("\n====== WITH History (Growing Conversation) ======")
    msgs = []
    for idx, q in enumerate(questions):
        user_msg = HumanMessage(q)
        msgs.append(user_msg)
        response = client.invoke(msgs)
        msgs.append(response)
        print(f"\nUSER {idx+1}: {q}")
        print(f"RESPONSE {idx+1}: {getattr(response, 'content', response)}")
