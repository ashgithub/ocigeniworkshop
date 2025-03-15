#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-agent-users or #igiu-innovation-lab slack channel

# if you have errors running sample code reach out for help in #igiu-ai-learning

from oci.generative_ai_agent_runtime import GenerativeAiAgentRuntimeClient
import oci
import os,json 

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

GENAI_URL = "https://agent-runtime.generativeai.us-chicago-1.oci.oraclecloud.com"

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
    
def inference_api(message, session_id, endpoint,preamble=""):
    chat_detail = oci.generative_ai_agent_runtime.models.ChatDetails()
    chat_detail.user_message = preamble + " " + message
    chat_detail.session_id = session_id
    chat_response = genai_client.chat(endpoint, chat_detail)
    return chat_response.data.message.content


def get_genai_client(config):
    return GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=GENAI_URL,
        retry_strategy=oci.retry.NoneRetryStrategy(),
        timeout=(10, 240),
    )


#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
session_endpoint = scfg["agent"]["endpoint"] 
sessionless_endpoint = scfg["agent"]["no_session_endpoint"] 
session = scfg["agent"]["session"]  
genai_client = get_genai_client(config)

if session == True:

    create_session_details = oci.generative_ai_agent_runtime.models.CreateSessionDetails(
        display_name="Inno Lab C2M Agent ", description="The end has access to C2M documentation and can answer any questions on it"
    )
    create_session_response = genai_client.create_session(create_session_details,session_endpoint )
    session_id = create_session_response.data.id if session == True else None
    endpoint = session_endpoint
else:
    session_id = None
    endpoint = sessionless_endpoint

while True:
        query = input("\n\nAsk a question: ").strip().lower()
        result = inference_api(query, session_id, endpoint, preamble="You are an expert of Oracles C2M. Answer teh questions professionally & factually. If you dont know the answer say so. Always quote the source form yhour knowledgebase")
        print("****** citation ********")
        print(result.citations)
        print("****** answer ********")
        print(result.text)

#sample questions 
#   - how often do i need to service battery
#    - when should oil be replace din recloser
#    - what is accepted co2 in DGA