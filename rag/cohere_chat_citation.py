#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel

# if you have errors running sample code reach out for help in #igiu-ai-learning
# we can pass the documents to LLM & get citations back. 

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci
import os,json

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

LLM_MODEL = "cohere.command-r-plus-08-2024" 
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

def get_chat_request():
        cohere_chat_request = CohereChatRequest()
        cohere_chat_request.preamble_override = "Provide factual answers based of document provided nclude citations if you can. Say you cant answer if the answer is not in provided documents "
        #cohere_chat_request.message = "Tell me one fact about earth"
        cohere_chat_request.is_stream = False 
        cohere_chat_request.max_tokens = 500
        cohere_chat_request.temperature = 0.75
        cohere_chat_request.top_p = 0.7
        cohere_chat_request.frequency_penalty = 1.0
     #   cohere_chat_request.chat_history = None  # try adding history see ../llm/cohere_chat_history.py ofr details
        cohere_chat_request.documents = get_documents()  # will only answer from supplied documnets not frm its own knopwledge
        cohere_chat_request.citation_quality =  cohere_chat_request.CITATION_QUALITY_FAST # FAST or accurate
#        cohere_chat_request.citation_quality =  cohere_chat_request.CITATION_QUALITY_ACCURATE # FAST or accurate
        return cohere_chat_request

def get_chat_detail (llm_request,compartmentId):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        print(f"documents are {llm_request.documents}")
        print(f"citation quality {llm_request.citation_quality}")
        return chat_detail


def get_history():
        previous_chat_message = oci.generative_ai_inference.models.CohereUserMessage(message="Tell me something about Oracle.")
        previous_chat_reply = oci.generative_ai_inference.models.CohereChatBotMessage(message="Oracle is one of the largest vendors in the enterprise IT market and the shorthand name of its flagship product. The database software sits at the center of many corporate IT")
        return [previous_chat_message, previous_chat_reply]

def get_documents():
    return  [
                 {
                        "title": "Oracle",
                        "snippet": "Oracle database services and products offer customers cost-optimized and high-performance versions of Oracle Database, the world's leading converged, multi-model database management system, as well as in-memory, NoSQL and MySQL databases. Oracle Autonomous Database, available on premises via Oracle Cloud@Customer or in the Oracle Cloud Infrastructure, enables customers to simplify relational database environments and reduce management workloads.",
                        "website": "https://www.oracle.com/database",
                        "id": "ORA001"
                },
                 {
                        "title": "Amazon",
                        "snippet": """ AWS provides the broadest selection of purpose-built databases allowing you to save, grow, and innovate faster.
Purpose Built
Choose from 15+ purpose-built database engines including relational, key-value, document, in-memory, graph, time series, wide column, and ledger databases.
Performance at Scale
Get relational databases that are 3-5X faster than popular alternatives, or non-relational databases that give you microsecond to sub-millisecond latency.
Fully Managed
AWS continuously monitors your clusters to keep your workloads running with self-healing storage and automated scaling, so that you can focus on application development.
Secure & Highly Available
AWS databases are built for business-critical, enterprise workloads, offering high availability, reliability, and security.
""",
                        "website": "https://aws.amazon.com/free/database/e",
                        "id": "AWS001"
                }
]

#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])



llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_payload =get_chat_detail(get_chat_request(),scfg["oci"]["compartment"])

# experiment by uncommenting one of teh following three lines 
#llm_payload.chat_request.message = "Tell me about Ashish ?"  # should answer with oracle document & citation 
#llm_payload.chat_request.message = "tell me about oracles  databases"  # should answer with oracle document & citation 
llm_payload.chat_request.message = "tell me about Amazon's databases"  # Should answert with aws document and citation
#llm_payload.chat_request.message = "tell me about its databases"  # uses history to resolve it, and use appropriate citation  

llm_response = llm_client.chat(llm_payload)

# Print result
print("**************************Chat Result**************************")
#llm_text = llm_response.data.chat_response.text
print(llm_response.data.chat_response.text)
print("************************** Citations**************************")  # citations are from documents given, not from its own corpus
print(llm_response.data.chat_response.citations)
        