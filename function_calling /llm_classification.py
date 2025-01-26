#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci

#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####

CONFIG_PROFILE = "AISANDBOX"
compartmentId= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
llm_client = None
llm_payload = None

def get_chat_request():
        cohere_chat_request = CohereChatRequest()
        cohere_chat_request.preamble_override = """
        
        You are a call classifier you carefully analyze teh question and classify it into one of the following categories. 
        you then return just the category in response
        
        categories: billing, outage, program, service
        
        eg: 
        question:  can i pay my bill by creditcard
        answer: billing
        question: i need to cancel my service as i am moving
        answer: service
        question: when will by power come back on?
        answer: outage
        
        """
        cohere_chat_request.is_stream = False 
        cohere_chat_request.max_tokens = 500
        cohere_chat_request.temperature = 0.75
        cohere_chat_request.top_p = 0.7
        cohere_chat_request.frequency_penalty = 1.0

        return cohere_chat_request

def get_chat_detail (llm_request):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id="cohere.command-r-plus")
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail

config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_payload =get_chat_detail(get_chat_request())
llm_payload.chat_request.message = "why is my bill so high"

llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.text
        
print (llm_text)