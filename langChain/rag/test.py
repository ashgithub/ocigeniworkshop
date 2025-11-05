import os
import json
import oci
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails

SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/sandbox.json"

EMBED_MODEL = "cohere.embed-multilingual-v3.0"
LLM_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

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

# Using lang doc loading
pdf_path = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/langChain/rag/Sample1.pdf"

print(f"Loading PDF: {pdf_path}")
loader = PyPDFLoader(pdf_path)
docs = loader.load()  # returns a list of Document objects

print(f"Loaded {len(docs)} pages from the PDF.")
print(f"Example page content:\n{docs[0].page_content[:250]}...\n")

# Text splitters
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)

splits = text_splitter.split_documents(docs)
print(f"Created {len(splits)} text chunks for embedding.")

# Inspect one split
print(f"Example chunk:\n{splits[0].page_content[:250]}...\n")

llm_client = GenerativeAiInferenceClient(
    config=config,
    service_endpoint=LLM_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240),
)

def get_embed_payload(chunks, embed_type):
    """Build embedding payload for OCI Generative AI."""
    embed_text_detail = EmbedTextDetails()
    embed_text_detail.serving_mode = OnDemandServingMode(model_id=EMBED_MODEL)
    embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
    embed_text_detail.input_type = embed_type
    embed_text_detail.compartment_id = compartment_id
    embed_text_detail.inputs = chunks
    return embed_text_detail

# Extract the content
texts = [chunk.page_content for chunk in splits]

# Try the embeding models
print("Creating embeddings...")
embed_payload = get_embed_payload(texts, EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT)
embed_response = llm_client.embed_text(embed_payload)

embeddings = embed_response.data.embeddings
print(f"✅ Generated {len(embeddings)} embeddings.")

# Text + embeding
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