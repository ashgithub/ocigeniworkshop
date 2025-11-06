import oci, json,os


from dotenv import load_dotenv
from envyaml import EnvYAML
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()
LLM_MODEL = "meta.llama-3.3-70b-instruct" 
LLM_URL= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# openai.gpt-4.1
# openai.gpt-4.1-mini
# openai.gpt-4.1-nano
# openai.gpt-o1
# openai.gpt-o3
# openai.gpt-4o
# openai.gpt-4o-mini
# openai.gpt-5
# openai.gpt-5-mini
# openai.gpt-5-nano
# xai.grok-3
# xai.grok-4
# xai.grok-4-fast-reasoning
# xai.grok-4-fast-non-reasoning
# meta.llama-4-maverick-17b-128e-instruct-fp8
# meta.llama-4-scout-17b-16e-instruct

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def get_system_text_message(prompt):
        content = oci.generative_ai_inference.models.TextContent()
        content.text = prompt
        message = oci.generative_ai_inference.models.SystemMessage()
        message.content = [content] 

        return message

def get_assistant_text_message(prompt):
        content = oci.generative_ai_inference.models.TextContent()
        content.text = prompt
        message = oci.generative_ai_inference.models.AssistantMessage()
        message.content = [content] 

        return message
    
def get_user_text_message(prompt):
        content = oci.generative_ai_inference.models.TextContent()
        content.text = prompt
        message = oci.generative_ai_inference.models.UserMessage()
        message.content = [content] 

        return message

def get_chat_request():
        chat_request = oci.generative_ai_inference.models.GenericChatRequest()
        chat_request.messages = None
        chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
        chat_request.num_generations = 1
        chat_request.is_stream = True
        chat_request.max_tokens = 500
        chat_request.temperature = 0.75

        return chat_request

def get_chat_detail (llm_request,compartmentId):
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail


def chat(text):

    message = [get_user_text_message(text)]
    chat_detail.chat_request.messages = message
    llm_response = llm_client.chat(chat_detail)    
    for event in llm_response.data.events():
            output =  json.loads(event.data)['message']['content'][0]["text"]
            print(output,end='',flush=True)
        
        
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])


llm_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
                config=config,
                service_endpoint=LLM_URL,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_request = get_chat_request()
chat_detail = get_chat_detail(llm_request,scfg["oci"]["compartment"])

chat("tell me two things about India")