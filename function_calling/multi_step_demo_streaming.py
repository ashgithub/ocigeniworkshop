"""
What this file does:
Demonstrates multi-step function calling with streaming using OCI Generative AI Cohere models. Shows how to handle streaming responses in multi-step tool calling scenarios.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Command Models: https://docs.cohere.com/docs/command-r
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run function_calling/multi_step_demo_streaming.py

Comments to important sections of file:
- Step 1: Define multiple tools and make initial streaming chat request.
- Step 2+: Provide tool results and continue the streaming conversation with chat history.
- Experiment: Try changing tool outputs or observing streaming behavior in multi-step scenarios.
"""

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import CohereChatRequest, ChatDetails
import oci
import json
import os
from dotenv import load_dotenv
from envyaml import EnvYAML

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# available models with tool calling support
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# cohere.command-a-03-2025

#LLM_MODEL = "cohere.command-r-16k" 
LLM_MODEL = "cohere.command-a-03-2025" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



def load_config(config_path):
    """Load configuration from a YAML file using EnvYAML."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
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

# Step 1: Define multiple tools and make initial streaming chat request
chat_request = oci.generative_ai_inference.models.CohereChatRequest()
chat_request.message = "Total sales amount over the 28th and 29th of September."
chat_request.max_tokens = 600
chat_request.is_stream = True
chat_request.is_force_single_step = False
chat_request.tools = [report_tool, calculator_tool]

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
chat_detail.compartment_id = scfg["oci"]["compartment"]
chat_detail.chat_request = chat_request

chat_response = llm_client.chat(chat_detail)

# Print result
print("\n**************************Step 1 Result**************************")

def get_tool_calls_and_chat_history(chat_response):
    for event in chat_response.data.events():
        res = json.loads(event.data)
        if 'finishReason' in res:
            if 'toolCalls' in res:
                print(f"\ntools to use : {res['toolCalls']}", flush=True)
                return res['toolCalls'], res['chatHistory']
            else:
                return None, res['chatHistory']
        if 'text' in res:
            print(res['text'], end="", flush=True)
    print("\n")
    return None, None

tool_results = []
chat_request.message = ""
tool_calls, chat_history = get_tool_calls_and_chat_history(chat_response)
step = 1

# Step 2+: Provide tool results and continue the streaming conversation with chat history
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
