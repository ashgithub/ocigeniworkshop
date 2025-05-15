#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel

# if you have errors running sample code reach out for help in #igiu-ai-learning
# we can pass the documents to LLM & get citations back. 

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, RerankTextDetails 
import oci
import os,json

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

RERANK_MODEL ="cohere.rerank-english-v3.1" 
#RERANK_MODEL ="cohere.rerank-multilingual-v3.0"
#RERANK_MODEL ="cohere.rerank.3-5"
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
llm_client = None
llm_payload = None

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{config_path}': {e}")
        return None


def get_rerank_detail (compartmentId):
        rerank_detail = RerankTextDetails()
        rerank_detail.serving_mode = OnDemandServingMode(model_id=RERANK_MODEL)
        rerank_detail.compartment_id = compartmentId
        rerank_detail.input  = "tell me about dogs"
        rerank_detail.documents  = get_documents()

        return rerank_detail


def get_documents():
    return  [
                "cats are cute",  #0
                "puppies are small dogs", #1
                "cats dont wag their tails", #2 
                "dogs wag tails", #3 
                " planes war is called dog fight", #4 
                " dogpile is not about pets" # 5
                ]

#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])



llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_payload =get_rerank_detail(scfg["oci"]["compartment"])

llm_payload.input = "tell me about dogs"

llm_response = llm_client.rerank_text(llm_payload)

# Print result
print("**************************Chat Result**************************")
print(llm_response.data)
        