# Documentation: https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm
# GitHub SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference
# Postman collection: 
# Slack channels:#generative-ai-userst or #igiu-innovation-lab
# If you have errors running sample code, reach out for help in #igiu-ai-learning


from dotenv import load_dotenv
from envyaml import EnvYAML
import oci
import base64
import  os 

#####
# Make sure your sandbox.yaml and .env files are set up for your environment.
# You might have to specify the full path depending on your current working directory (cwd).
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


llm_client = None
llm_payload = None
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

def get_message():
        content1 = oci.generative_ai_inference.models.TextContent()
        content1.text = MESSAGE
        content2 = oci.generative_ai_inference.models.ImageContent()
        image_url = oci.generative_ai_inference.models.ImageUrl()
        image_url.url = f"data:image/jpeg;base64,{encode_image(FILE_TO_ANALYZE)}"
        content2.image_url = image_url
        message = oci.generative_ai_inference.models.UserMessage()
        message.content = [content1,content2] 

        return message

def get_chat_request():
        chat_request = oci.generative_ai_inference.models.GenericChatRequest()
        #chat_request.message = get_message() . notice for multimodal we give an array of messages 
        chat_request.messages = [get_message()]
        chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
        chat_request.num_generations = 1
        chat_request.is_stream = False 
        chat_request.max_tokens = 500
        chat_request.temperature = 0.75


        return chat_request

def get_chat_detail (llm_request,compartmentId, model_id):
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail
        
scfg = load_config(SANDBOX_CONFIG_FILE)
if scfg is not None and 'oci' in scfg and 'configFile' in scfg['oci'] and 'profile' in scfg['oci'] and 'compartment' in scfg['oci']:
    config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]), scfg["oci"]["profile"])
    compartment_id = scfg["oci"]["compartment"]
else:
    print("Error: Invalid configuration for OCI.")
    exit(1)


llm_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
import time

for model_id in MODEL_LIST:
    banner = "=" * 80
    print(f"\n{banner}\nRESULTS FOR MODEL: {model_id}\n{banner}")
    start_time = time.time()
    llm_payload = get_chat_detail(get_chat_request(),
                                  compartment_id,
                                  model_id)
    llm_response = llm_client.chat(llm_payload)
    if llm_response is not None and hasattr(llm_response, 'data') and hasattr(llm_response.data, 'chat_response') and llm_response.data.chat_response is not None and hasattr(llm_response.data.chat_response, 'choices') and llm_response.data.chat_response.choices:
        llm_text = llm_response.data.chat_response.choices[0].message.content[0].text
        print(llm_text)
    else:
        print("Error: Invalid response from LLM.")
    end_time = time.time()
    print(f"{banner}\nTime taken: {end_time - start_time:.2f} seconds\n")
