import oci, json,os


SANDBOX_CONFIG_FILE = "sandbox.json"
LLM_MODEL = "meta.llama-3.3-70b-instruct" 
LLM_URL= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


message_history=[]
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
        chat_request.is_stream = False
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

    message_history.append(get_user_text_message(text))
    chat_detail.chat_request.messages = message_history
    llm_response = llm_client.chat(chat_detail)    
#    output = ""
#    for event in llm_response.data.events():
#            output +=  json.loads(event.data)['message']['content'][0]["text"]
#            yield output 
        
    generated_text = llm_response.data.chat_response.choices[0].message.content[0].text
    message_history.append (get_assistant_text_message(generated_text))
    return generated_text
        
    

#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])


llm_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
                config=config,
                service_endpoint=LLM_URL,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_request = get_chat_request()
chat_detail = get_chat_detail(llm_request,scfg["oci"]["compartment"])
message_history.append(get_system_text_message("provide a brief answer in 2-3sentences"))

print(chat("tell me two things about India"))
print("-----")
print(chat("tell me more about second thing"))