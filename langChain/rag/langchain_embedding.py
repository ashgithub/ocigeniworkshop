""" Sample file to perform embedding using langchain_oci methods and traditional GenAI connections """
import os
import json
import oci
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_oci.embeddings import OCIGenAIEmbeddings
# from oci.generative_ai_inference import GenerativeAiInferenceClient
# from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails

# Reference: https://docs.langchain.com/oss/python/integrations/splitters

SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/sandbox.json"

EMBED_MODEL = "cohere.embed-v4.0"
# Availble embedding models https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm#embed-models

# cohere.embed-v4.0
# cohere.embed-multilingual-v3.0
# cohere.embed-multilingual-light-v3.0
# cohere.embed-english-v3.0
# cohere.embed-english-light-v3.0

LLM_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Step 1: load the config files
def load_config(config_path):
    """Load configuration from sandbox.json."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {e}")

scfg = load_config(SANDBOX_CONFIG_FILE)

config = oci.config.from_file(
    os.path.expanduser(scfg["oci"]["configFile"]),
    scfg["oci"]["profile"]
)
compartment_id = scfg["oci"]["compartment"]

""" Load document and chunk, details on langchain_chunks.py """

pdf_path = "Sample1.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=200,
    add_start_index=True
)
splits = text_splitter.split_documents(docs)

""" Start the embedding phase """

llm_embed_client = OCIGenAIEmbeddings(
    model_id=EMBED_MODEL,
    service_endpoint=LLM_ENDPOINT,
    compartment_id=compartment_id
)

# Extract the content from the chunks
texts = [chunk.page_content for chunk in splits]

# Step 2: Use the common langchain_oci library to perform embedding
# Use the OCI langchain client to perform the embeddings
embeddings = llm_embed_client.embed_documents(texts)

# Traditional mode: Use the oci_gen_ai service instances

# llm_client = GenerativeAiInferenceClient(
#     config=config,
#     service_endpoint=LLM_ENDPOINT,
#     retry_strategy=oci.retry.NoneRetryStrategy(),
#     timeout=(10, 240),
# )
# 
# def get_embed_payload(chunks, embed_type):
#     """Build embedding payload for OCI Generative AI."""
#     embed_text_detail = EmbedTextDetails()
#     embed_text_detail.serving_mode = OnDemandServingMode(model_id=EMBED_MODEL)
#     embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
#     embed_text_detail.input_type = embed_type
#     embed_text_detail.compartment_id = compartment_id
#     embed_text_detail.inputs = chunks
#     return embed_text_detail
# 
# embed_payload = get_embed_payload(texts, EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT)
# embed_response = llm_client.embed_text(embed_payload)
# 
# embeddings = embed_response.data.embeddings

print(f"Generated {len(embeddings)} embeddings.")

# Text + embeding for display
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