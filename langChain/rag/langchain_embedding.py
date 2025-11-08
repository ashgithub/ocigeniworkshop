"""
What this file does:
Demonstrates embedding generation using OCI Generative AI for chunks from a PDF document.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- LangChain: https://docs.langchain.com/oss/python/langchain/overview
- OCI langchain SDK: https://github.com/oracle-devrel/langchain-oci-genai  note: as of Nov 2025 it is not compatible with langchain v1.0. supports all OCI models including Cohere
- OCI GenAI SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI 
 - #igiu-innovation-lab: general discussions on your project 
 - #igiu-ai-learning: help with sandbox environment or help with running this code 

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/rag/langchain_embedding.py

Comments to important sections of file:
- Step 1: Load config and initialize clients.
- Step 2: Load and chunk the PDF document.
- Step 3: Generate embeddings for chunks.
- Step 4: Display results.
"""

import os
import json
import oci
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_oci.embeddings import OCIGenAIEmbeddings  requires langchain 0.3x, doesn't work with 1.0.0 yet

from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails

# Reference: https://docs.langchain.com/oss/python/integrations/splitters

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

EMBED_MODEL = "cohere.embed-english-light-v3.0"
# Available embedding models https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm#embed-models

# cohere.embed-v4.0
# cohere.embed-multilingual-v3.0
# cohere.embed-multilingual-light-v3.0
# cohere.embed-english-v3.0
# cohere.embed-english-light-v3.0

OCI_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

def get_embed_payload(chunks, embed_type):
    """Build embedding payload for OCI Generative AI."""
    embed_text_detail = EmbedTextDetails()
    embed_text_detail.serving_mode = OnDemandServingMode(model_id=EMBED_MODEL)
    embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
    embed_text_detail.input_type = embed_type
    embed_text_detail.compartment_id = compartment_id
    embed_text_detail.inputs = chunks
    return embed_text_detail

# Step 1: Load config and initialize clients
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

config = oci.config.from_file(
    os.path.expanduser(scfg["oci"]["configFile"]),
    scfg["oci"]["profile"]
)
compartment_id = scfg["oci"]["compartment"]

embed_client = GenerativeAiInferenceClient(
     config=config,
     service_endpoint=OCI_ENDPOINT,
     retry_strategy=oci.retry.NoneRetryStrategy(),
     timeout=(10, 240),
 )

# Step 2: Load and chunk the PDF document
pdf_path = "./langChain/rag/Sample1.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=200,
    add_start_index=True
)
splits = text_splitter.split_documents(docs)
texts = [chunk.page_content for chunk in splits]

print(f"Created {len(splits)} text chunks for embedding.")

# Step 3: Generate embeddings for chunks
# Uncomment below for LangChain mode (requires langchain 0.3x, doesn't work with 1.0.0 yet)
# llm_embed_client = OCIGenAIEmbeddings(
#     model_id=EMBED_MODEL,
#     service_endpoint=OCI_ENDPOINT,
#     compartment_id=compartment_id
# )
# embeddings = llm_embed_client.embed_documents(texts)


# we will use the oci apis for embedding
embed_payload = get_embed_payload(texts, EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT)
embed_response = embed_client.embed_text(embed_payload)
embeddings = embed_response.data.embeddings

print(f"Generated {len(embeddings)} embeddings.")

# Step 4: Display results
embedded_docs = [
    {
        "text": texts[i],
        "embedding": embeddings[i],
        "metadata": splits[i].metadata
    }
    for i in range(len(texts))
]

# Show a preview of one embedding
print("\nExample embedded document:")
print(json.dumps({
    "sample_text": embedded_docs[0]["text"][:200],
    "embedding_dim": len(embedded_docs[0]["embedding"]),
    "metadata": embedded_docs[0]["metadata"]
}, indent=2))
