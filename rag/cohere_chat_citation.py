#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel
# we can pass the documents to LLM & get citations back. 

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci
import json

#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####


CONFIG_PROFILE = "AISANDBOX"
compartmentId= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
llm_client = None
llm_payload = None

def get_chat_request():
        cohere_chat_request = CohereChatRequest()
        cohere_chat_request.preamble_override = "you always answer in a one stanza poem."
        #cohere_chat_request.message = "Tell me one fact about earth"
        cohere_chat_request.is_stream = False 
        cohere_chat_request.max_tokens = 500
        cohere_chat_request.temperature = 0.75
        cohere_chat_request.top_p = 0.7
        cohere_chat_request.frequency_penalty = 1.0
        cohere_chat_request.chat_history = get_history()
        cohere_chat_request.documents = get_documents()  # will only answer from supplied documnets not frm its own knopwledge
        return cohere_chat_request

def get_chat_detail (llm_request):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id="cohere.command-r-plus")
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

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
        "website": "https://www.oracle.com/database"
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
        "website": "https://aws.amazon.com/free/database/e"
    }
]


config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_payload =get_chat_detail(get_chat_request())
llm_payload.chat_request.message = "tell me about its databases"  # uses history to resolve it 

llm_response = llm_client.chat(llm_payload)

# Print result
print("**************************Chat Result**************************")
#llm_text = llm_response.data.chat_response.text
print(llm_response.data.chat_response.text)
print("************************** Citations**************************") . # citations are from documents given, not from its own corpus
print(llm_response.data.chat_response.citations)
        