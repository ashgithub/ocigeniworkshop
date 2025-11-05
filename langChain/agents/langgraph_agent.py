# TODO: Cris is changing the create_react_agent method before next PR

from langgraph.prebuilt import create_react_agent
# create_react_agent has been moved to `langchain.agents`. Please update your import to `from langchain.agents import create_agent`. Deprecated in LangGraph V1.0 to be removed in V2.0.
# langchain-oci current latest version 0.1.5 not compatible with langchain 1.0.0
from langchain_oci.chat_models import ChatOCIGenAI
from langchain.tools import tool

@tool
def get_weather(city:str)->str:
    """ Gets the weather in a given city """
    return f"Is sunny at {city}"

llm_model = ChatOCIGenAI(
    model_id="openai.gpt-4.1",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="<compartiment>",
    auth_file_location="<location>",
    auth_profile="<profile>"
)

system_prompt = "You are a helpful assistant"

agent = create_react_agent(
    model=llm_model,
    tools=[get_weather],
    prompt=f"{system_prompt}"
)

response = agent.invoke({"messages":[{"role":"user","content":"What is the weather in SF?"}]})
print(response)