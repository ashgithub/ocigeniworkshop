#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-agent-users or #igiu-innovation-lab slack channel

from oci.generative_ai_agent_runtime import GenerativeAiAgentRuntimeClient
import oci
#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####

CONFIG_PROFILE = "AISANDBOX"
compartmentId= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 

GENAI_URL = "https://agent-runtime.generativeai.us-chicago-1.oci.oraclecloud.com"
GENAI_CHAT_ENDPOINT = "ocid1.genaiagentendpoint.oc1.us-chicago-1.amaaaaaaghwivzaab2dsqrl4xsbevpi4kc7lsmwmr76qxkmeeovgksv2hylq"


def inference_api(message, session_id, preamble=""):
    chat_detail = oci.generative_ai_agent_runtime.models.ChatDetails()
    chat_detail.user_message = preamble + " " + message
    chat_detail.session_id = session_id
    chat_response = genai_client.chat(GENAI_CHAT_ENDPOINT, chat_detail)
    return chat_response.data.message.content


def get_genai_client():
    return GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=GENAI_URL,
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240),
    )


config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

genai_client = get_genai_client()

create_session_details = oci.generative_ai_agent_runtime.models.CreateSessionDetails(
    display_name="display_name", description="description"
)
create_session_response = genai_client.create_session(create_session_details, GENAI_CHAT_ENDPOINT)
session_id = create_session_response.data.id

while True:
        query = input("\n\nAsk a question: ").strip().lower()
        result = inference_api(query, session_id, preamble="answer  in bullet points")
        print("****** citation ********")
        print(result.citations)
        print("****** answer ********")
        print(result.text)

#sample questions 
#   - how often do i need to service battery
#    - when should oil be replace din recloser
#    - what is accepted co2 in DGA