"""
What this file does:
Demonstrates structured output using Pydantic models and JSON schemas with OCI's OpenAI-compatible API. Shows how to generate structured data responses including simple JSON, complex nested objects, and Pydantic class instances.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- LangChain Structured Output: https://python.langchain.com/docs/how_to/structured_output/
- Pydantic Models: https://docs.pydantic.dev/latest/concepts/models/
- OpenAI Structured Outputs: https://platform.openai.com//guides/structured-outputs

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).
- Note: Structured output is supported by OpenAI and Grok models, but not Cohere or Meta models.

How to run the file:
uv run langChain/llm/openai_oci_structured_output.py

Comments to important sections of file:
- Step 1: Import dependencies and define schemas.
- Step 2: Load config and initialize client.
- Step 3: Demonstrate simple JSON schema output.
- Step 4: Demonstrate complex nested JSON schema.
- Step 5: Demonstrate Pydantic class output.
- Step 6: Demonstrate composed Pydantic class output.
"""

import sys
import os
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Step 1: Import dependencies and define schemas
# Supported models for structured output: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
LLM_MODEL = "openai.gpt-4o"  # Cohere/Meta models don't support structured output

MESSAGE = """
  Give me the information about the current science fiction books.
"""

# Pydantic class schema
class BookInventory(BaseModel):
    """Information about a book in a store or library inventory."""
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
    books: List[BookInventory] = Field(description="List of books available at the branch")

# JSON schemas defined using OpenAI schema rules: https://platform.openai.com/docs/guides/structured-outputs
book_review_schema = {
    "title": "book_review",
    "description": "User review information for a specific book",
    "type": "object",
    "properties": {
        "book_title": {"type": "string", "description": "Title of the book being reviewed"},
        "reviewer_name": {"type": "string", "description": "Name of the person who wrote the review"},
        "rating": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Rating score between 1 and 5"},
        "verified_purchase": {"type": "boolean", "description": "True if the reviewer purchased the book"},
        "comments": {"type": "string", "description": "Text of the user's review"}
    },
    "required": ["book_title", "reviewer_name", "rating"]
}

# Complex JSON schema with nested objects (arrays)
library_event_schema = {
    "title": "library_event",
    "description": "Details about a scheduled event in a library",
    "type": "object",
    "properties": {
        "event_name": {"type": "string", "description": "Title of the event"},
        "is_free": {"type": "boolean", "description": "Whether attendance is free"},
        "max_attendees": {"type": "integer", "minimum": 0, "description": "Maximum number of attendees allowed"},
        "duration_minutes": {"type": "integer", "minimum": 0, "description": "Duration of the event in minutes"},
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

# Step 2: Load config and initialize client
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

llm_client = OCIOpenAIHelper.get_client(
    model_name=LLM_MODEL,
    config=scfg
)

# Step 3: Demonstrate simple JSON schema output
print("**************************Chat Response with JSON output**************************")
simple_json_model = llm_client.with_structured_output(book_review_schema)
response = simple_json_model.invoke(MESSAGE)
print(response)

# Step 4: Demonstrate complex nested JSON schema
print("**************************Chat Response with complex JSON output**************************")
complex_json_model = llm_client.with_structured_output(library_event_schema)
response = complex_json_model.invoke(MESSAGE)
print(response)

# Step 5: Demonstrate Pydantic class output
print("**************************Chat Response with Pydantic class output**************************")
pydantic_model = llm_client.with_structured_output(BookInventory)
response = pydantic_model.invoke(MESSAGE)
print(response)
print(type(response))

# Step 6: Demonstrate composed Pydantic class output
print("**************************Chat Response with Composed Pydantic class output**************************")
composed_pydantic_model = llm_client.with_structured_output(LibraryBranch)
response = composed_pydantic_model.invoke(MESSAGE)
print(response)
print(type(response))
