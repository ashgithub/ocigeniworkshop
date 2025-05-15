#!/Users/ashish/anaconda3/bin/python
# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel
# if you have errors running sample code reach out for help in #igiu-ai-learnin

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci
import json, os 

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

# available models with tool calling support
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# cohere.command-a-03-2025

#LLM_MODEL = "cohere.command-r-16k" 
LLM_MODEL = "cohere.command-a-03-2025" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



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
    

#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])    

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))


date_param = oci.generative_ai_inference.models.CohereParameterDefinition()
date_param.description = "Retrieves sales data for this day, formatted as YYYY-MM-DD."
date_param.type = "str"
date_param.is_required = True

report_tool = oci.generative_ai_inference.models.CohereTool()
report_tool.name = "query_daily_sales_report"
report_tool.description = "Connects to a database to retrieve overall sales volumes and sales information for a given day."
report_tool.parameter_definitions = {
    "date": date_param
}

expression_param = oci.generative_ai_inference.models.CohereParameterDefinition()
expression_param.description = "The expression to caculate."
expression_param.type = "str"
expression_param.is_required = True

calculator_tool = oci.generative_ai_inference.models.CohereTool()
calculator_tool.name = "simple_calculator"
calculator_tool.description = "Connects to a database to retrieve overall sales volumes and sales information for a given day."
calculator_tool.parameter_definitions = {
    "expression": expression_param
}

# Step 1, describe the tool spec

chat_request = oci.generative_ai_inference.models.CohereChatRequest()
chat_request.message = "Total sales amount over the 28th and 29th of September."
chat_request.max_tokens = 600
chat_request.is_stream = True
chat_request.is_force_single_step = False
chat_request.tools = [ report_tool, calculator_tool ]

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
# chat_detail.serving_mode = generative_ai_service_bmc_python_client.models.DedicatedServingMode(
#     endpoint_id="ocid1.generativeaiendpoint.oc1.us-chicago-1.amaaaaaabgjpxjqa43esnc2c6yluihthqqfa24ll5y5d4jhct6rgq523rena")
chat_detail.compartment_id =  scfg["oci"]["compartment"]
chat_detail.chat_request = chat_request



chat_response = llm_client.chat(chat_detail)

# Print result
print("\n**************************Step 1 Result**************************")
#print(vars(chat_response))


def get_tool_calls_and_chat_history(chat_response):
    for event in chat_response.data.events():
        res = json.loads(event.data)
        if 'finishReason' in res:
            if 'toolCalls' in res:
                print(f"\ntools to use : {res['toolCalls']}",flush=True)
                return res['toolCalls'], res['chatHistory']
            else:
                return None, res['chatHistory']
#        else:
        if 'text' in res:
            print(res['text'], end="", flush=True)
    print("\n")
    return None, None

tool_results = []
chat_request.message = ""
tool_calls, chat_history = get_tool_calls_and_chat_history(chat_response)
step = 1

# Step 2, provide the tool results for step 1 and ask the model what the next step is
while tool_calls is not None:
    for call in tool_calls:
        call = oci.generative_ai_inference.models.CohereToolCall(**call)
        tool_result = oci.generative_ai_inference.models.CohereToolResult()
        tool_result.call = call
        if call.name == "query_daily_sales_report":
            if call.parameters["date"] == "2023-09-29":
                tool_result.outputs = [
                    {
                        "date": call.parameters["date"],
                        "summary": "Total Sales Amount: 8000, Total Units Sold: 200"
                    }
                ] 
            else:
                tool_result.outputs = [
                    {
                        "date": call.parameters["date"],
                        "summary": "Total Sales Amount: 5000, Total Units Sold: 125"
                    }
                ] 
        else:
            tool_result.outputs = [
                {
                    "expression": call.parameters["expression"],
                    "answer": "13000"
                }
            ]
        tool_results.append(tool_result)

    chat_request.chat_history = chat_history
    chat_request.tool_results = tool_results
    chat_response = llm_client.chat(chat_detail)

    # Print result
    step = step+1
    print(f"\n**************************Step {step} Result**************************",flush=True)
    #print(vars(chat_response))
    tool_calls, chat_history = get_tool_calls_and_chat_history(chat_response)


    for event in chat_response.data.events():
        res = json.loads(event.data)
        if 'finishReason' in res:
            if 'toolCalls' in res:
                print(f"\ntool calls: {res['toolCalls']}",flush=True)
            else:
                print(f"\nfinish reason: {res['finishReason']}",flush=True)
            break
        if 'text' in res:
            print(res['text'], end="", flush=True)
    print("\n")
