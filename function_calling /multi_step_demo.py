#!/Users/ashish/anaconda3/bin/python
# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci
import json

#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####
compartmentId= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 

CONFIG_PROFILE = "AISANDBOX"
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

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
chat_request.is_stream = False
chat_request.is_force_single_step = False
chat_request.tools = [ report_tool, calculator_tool ]

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.command-r-plus-08-2024")
#chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.command-r-16k")
# chat_detail.serving_mode = generative_ai_service_bmc_python_client.models.DedicatedServingMode(
#     endpoint_id="ocid1.generativeaiendpoint.oc1.us-chicago-1.amaaaaaabgjpxjqa43esnc2c6yluihthqqfa24ll5y5d4jhct6rgq523rena")
chat_detail.compartment_id = compartmentId
chat_detail.chat_request = chat_request





chat_response = llm_client.chat(chat_detail)

# Print result
print("**************************Step 1 Result**************************")
print(vars(chat_response))

# Step 2, provide the tool results for step 1 and ask the model what the next step is

tool_results = []
chat_request.message = ""
step = 1
while chat_response.data.chat_response.tool_calls is not None:
    for call in chat_response.data.chat_response.tool_calls:
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

    chat_request.chat_history = chat_response.data.chat_response.chat_history
    chat_request.tool_results = tool_results
    chat_response = llm_client.chat(chat_detail)

    # Print result
    step = step +1 
    print(f"**************************Step {step} Result**************************")
    print(vars(chat_response))