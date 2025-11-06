""" Sample langfuse integration that does not require OCI agent connection """
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"Agent.{__name__}")

# Langfuse API connection
langfuse = Langfuse(
    public_key="pk-", # Your keys
    secret_key="sk-",
    host="https://your-cloud-endpoint"
)

langfuse_handler = CallbackHandler()

from langchain.chains import TransformChain

# Function to call lagchain tracing
def uppercase_transform(inputs: dict) -> dict:
    text = inputs["text"]
    return {"output": text.upper()}

chain = TransformChain(
    input_variables=["text"],
    output_variables=["output"],
    transform=uppercase_transform,
)

# invokation with tracing
result = chain.invoke({"text": "<user_input>"}, config={"callbacks": [langfuse_handler]})
print(result)