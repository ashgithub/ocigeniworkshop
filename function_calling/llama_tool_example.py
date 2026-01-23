"""
What this file does:
Demonstrates function calling using OCI Generative AI Llama models. Shows how to define tools and handle tool calls with Llama models in a multi-step conversation.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Llama Models: https://www.llama.com/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run function_calling/llama_tool_example.py

Comments to important sections of file:
- Step 1: Define tools and make initial chat request with system and user messages.
- Step 2+: Handle tool calls, provide results, and continue the conversation.
- Experiment: Try different Llama models or modify tool definitions and responses.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import GenericChatRequest, ChatDetails
import oci
import json
import os

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# available models with tool calling support
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# meta.llama-3.3-70b-instruct 
# meta.llama-3.2-90b-vision-instruct
# meta.llama-4-maverick-17b-128e-instruct-fp8
# meta.llama-4-scout-17b-16e-instruct

#LLM_MODEL = "meta.llama-3.3-70b-instruct"  # requires oci-2.144 
LLM_MODEL = "meta.llama-4-scout-17b-16e-instruct"  # requires oci-2.144 
#LLM_MODEL = "meta.llama-4-maverick-17b-128e-instruct-fp8"  # requires oci-2.144 
#LLM_MODEL = "meta.llama-3.2-90b-vision-instruct"  # requires oci-2.144 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])    

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))

report_tool =  oci.generative_ai_inference.models.FunctionDefinition()
report_tool.name = "query_daily_sales_report"
report_tool.description = "Connects to a database to retrieve overall sales volumes and sales information for a given day."
report_tool.parameters = {
    "date": {
                "type": "string",
                "description": "Retrieves sales data for this daye, formatted as YYYY-MM-DD."
            }
}

calculator_tool = oci.generative_ai_inference.models.FunctionDefinition()
calculator_tool.type = oci.generative_ai_inference.models.ToolDefinition.TYPE_FUNCTION
calculator_tool.name = "simple_calculator"
calculator_tool.description = "Connects to a database to retrieve overall sales volumes and sales information for a given day."
calculator_tool.parameters = {
            "city_name": {
                "type": "string",
                "description": "The expression to caculatie"
            }
    }


# system message 
system_msg = oci.generative_ai_inference.models.SystemMessage()
system_msg.content = [
    oci.generative_ai_inference.models.TextContent(
        text = "Please, follow the next instructions: \nYou are a helpful assistant that answers questions from sales administrator about the sales. Use the provided tools to search for data about the sales. When searching, be persistent. If a tool result is not sufficient, suggest revised tool parameters or another tool call."
    )
]

user_msg = oci.generative_ai_inference.models.UserMessage()
user_msg.content = [
    oci.generative_ai_inference.models.TextContent(
        text = "Total sales amount over the 28th and 29th of September."
    )
] 


def get_tool_message(result, id):
        content = oci.generative_ai_inference.models.TextContent()
        content.text = str(result)
        message = oci.generative_ai_inference.models.ToolMessage()
        message.content = [content] 
        message.tool_call_id = call.id

        return message

chat_request = oci.generative_ai_inference.models.GenericChatRequest()
chat_request.messages = [ system_msg, user_msg]
chat_request.max_tokens = 600
chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
#chat_request.is_stream = False
chat_request.is_force_single_step = True
chat_request.tools = [ report_tool, calculator_tool ]
#chat_request.tool_choice = oci.generative_ai_inference.models.ToolChoiceAuto()

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
chat_detail.compartment_id = scfg["oci"]["compartment"]
chat_detail.chat_request = chat_request

# Step 1: Make initial chat request and let LLM figure out tool strategy
chat_response = llm_client.chat(chat_detail)

# Print result
print("**************************Step 1 Result**************************")
print(vars(chat_response))

# Step 2+: Provide tool results and continue the conversation

tool_results = []
step = 1

response_message = chat_response.data.chat_response.choices[0].message
#bug that context cannot be null

while response_message.tool_calls and len(response_message.tool_calls) > 0:
    # add the tool request message to list of messages
    response_message.content = [oci.generative_ai_inference.models.TextContent(text="")]
    chat_request.messages.append(response_message)
    for call in response_message.tool_calls:
        tool_message  = None
  
        if call.name == "query_daily_sales_report":
            date = json.loads(call.arguments)["date"]
            if  date == "2023-09-29":
                    tool_message = get_tool_message(
                        {
                            "date": date,
                            "summary": "Total Sales Amount: 8000, Total Units Sold: 200"
                        }, call.id)
            else:
                    tool_message = get_tool_message(
                        {
                            "date": date,
                            "summary": "Total Sales Amount: 5000, Total Units Sold: 125"
                        }, call.id)
        else:
            tool_message = get_tool_message(
                {
                    "expression": call.arguments,
                    "answer": "13000"
                } , call.id)
        print(f"tool called {call.name=} with {call.arguments=}")
        chat_request.messages.append(tool_message)

    chat_response = llm_client.chat(chat_detail)
    response_message = chat_response.data.chat_response.choices[0].message

    # Print result
    step = step +1 
    print(f"**************************Step {step} Result**************************")
    print(vars(response_message))

print(f"\n\n\************************** final result **************************")
print(response_message.content[0].text)
