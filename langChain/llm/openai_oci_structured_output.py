import sys
import os
from pydantic import BaseModel,Field
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai_oci_client import OciOpenAILangChainClient, OciOpenAILangGraphClient

from dotenv import load_dotenv
from envyaml import EnvYAML
# SOURCE: https://python.langchain.com/docs/how_to/structured_output/#the-with_structured_output-method

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#
#
#  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
#  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
#  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
#  if you have errors running sample code reach out for help in #igiu-ai-learning
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4o" # cohere / meta-llama models does not support structured output
# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# openai.gpt-4.1
# openai.gpt-4o
# xai.grok-4
# xai.grok-3
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# In the following section, different output schemas are declared to be used with the models

from pydantic import BaseModel, Field
from typing import List

# Pydantic class schema
class BookInventory(BaseModel):
    """Information about a book in a store or library inventory."""
    # Requires always a description

    # Name of the field : type = Field description to help model generate
    title: str = Field(description="Title of the book")
    author: str = Field(description="Author of the book")
    publication_year: int = Field(description="Publication year of the book")
    in_stock: bool = Field(description="True if the book is currently available in stock")
    copies_available: int = Field(ge=0, description="Number of copies available")
    price_usd: float = Field(ge=0.0, description="Price of the book in USD")

class LibraryBranch(BaseModel):
    """Details about a library branch and the books it holds."""

    branch_name: str = Field(description="Name of the library branch")
    is_open: bool = Field(description="Indicates if the branch is currently open")
    address: str = Field(description="Physical address of the branch")
    total_staff: int = Field(ge=0, description="Number of staff members")
    has_reading_area: bool = Field(description="Whether the branch has a public reading area")

    # Possible to use other pydantic classes nested
    books: List[BookInventory] = Field(description="List of books available at the branch")
     

# JSON scehmas defined using openai schema rules: https://platform.openai.com/docs/guides/structured-outputs
book_review_schema = {
    "title": "book_review",
    "description": "User review information for a specific book",
    "type": "object",
    "properties": {
        "book_title": {
            "type": "string",
            "description": "Title of the book being reviewed"
        },
        "reviewer_name": {
            "type": "string",
            "description": "Name of the person who wrote the review"
        },
        "rating": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Rating score between 1 and 5"
        },
        "verified_purchase": {
            "type": "boolean",
            "description": "True if the reviewer purchased the book"
        },
        "comments": {
            "type": "string",
            "description": "Text of the user's review"
        }
    },
    "required": ["book_title", "reviewer_name", "rating"]
}


# Complex json schema with nested objects (arrays)
library_event_schema = {
    "title": "library_event",
    "description": "Details about a scheduled event in a library",
    "type": "object",
    "properties": {
        "event_name": {
            "type": "string",
            "description": "Title of the event"
        },
        "is_free": {
            "type": "boolean",
            "description": "Whether attendance is free"
        },
        "max_attendees": {
            "type": "integer",
            "minimum": 0,
            "description": "Maximum number of attendees allowed"
        },
        "duration_minutes": {
            "type": "integer",
            "minimum": 0,
            "description": "Duration of the event in minutes"
        },
        "location": {
            "type": "object",
            "description": "Location details for the event",
            "properties": {
                "branch_name": {"type": "string"},
                "room": {"type": "string"},
                "is_virtual": {"type": "boolean"}
            },
            "required": ["branch_name"]
        },
        "guest_speakers": {
            "type": "array",
            "description": "List of guest speakers for the event",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "topic": {"type": "string"},
                    "is_main_speaker": {"type": "boolean"}
                },
                "required": ["name", "topic"]
            }
        }
    },
    "required": ["event_name", "is_free", "max_attendees", "location"]
}

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: Use the OciOpenAILangGraphClient from openai_oci_client.py to use output models
#llm_client = OciOpenAILangChainClient(
llm_client = OciOpenAILangGraphClient(
        profile=scfg['oci']['profile'],
        compartment_id=scfg['oci']['compartment'],
        model=LLM_MODEL,
        service_endpoint=llm_service_endpoint
    )


MESSAGE = """
  Give me the information about the current science fiction books.
"""

# Call the LLM client using the output format
print(f"**************************Chat Response with JSON output **************************") 
# Method to bind the output
simple_json_model = llm_client.with_structured_output(book_review_schema)
# Calling the model
response = simple_json_model.invoke(MESSAGE)
print(response)

print(f"**************************Chat Response with complex JSON output **************************") 
complex_json_model = llm_client.with_structured_output(library_event_schema)
response = complex_json_model.invoke(MESSAGE)
print(response)

print(f"**************************Chat Response with Pydantic class output **************************")
# Binds a pydantic class
pydantic_model = llm_client.with_structured_output(BookInventory)
response = pydantic_model.invoke(MESSAGE)
print(response)
print(type(response))

print(f"**************************Chat Response with Composed Pydantic class output **************************") 
composed_pydantic_model = llm_client.with_structured_output(LibraryBranch)
response = composed_pydantic_model.invoke(MESSAGE)
print(response)
print(type(response))