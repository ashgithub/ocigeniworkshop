"""
What this file does:
Demonstrates a semantic search example using OCI Generative AI for embeddings and Oracle DB for vector storage and semantic search.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- LangChain: https://docs.langchain.com/oss/python/langchain/overview
- Oracle DB Vectors: https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/
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
uv run langChain/rag/langchain_semantic_search.py

Comments to important sections of file:
- Step 1: Load config and initialize clients.
- Step 2: Load and chunk the PDF document.
- Step 3: Generate embeddings for chunks.
- Step 4: Set up Oracle DB connection and create vector table.
- Step 5: Insert embeddings into DB.
- Step 6: Define semantic search function.
- Step 7: Interactive loop for user queries.
- Step 8: Close DB connections.
"""

import os
import array
import oracledb
import oci
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails

# Reference: https://docs.langchain.com/oss/python/langchain/knowledge-base#build-a-semantic-search-engine-with-langchain

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
table_prefix = scfg["db"]["tablePrefix"]
wallet_path = os.path.expanduser(scfg["db"]["walletPath"])

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
embed_payload = get_embed_payload(texts, EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT)
embed_response = embed_client.embed_text(embed_payload)
embeddings = embed_response.data.embeddings

print(f"Generated {len(embeddings)} embeddings.")

# Step 4: Set up Oracle DB connection and create vector table
db_connection = oracledb.connect(
    config_dir=wallet_path,
    user=scfg["db"]["username"],
    password=scfg["db"]["password"],
    dsn=scfg["db"]["dsn"],
    wallet_location=wallet_path,
    wallet_password=scfg["db"]["walletPass"]
)
cursor = db_connection.cursor()

def create_table():
    """Drop and create embedding table."""
    print("Creating table for embeddings...")

    # Use the prefix to avoid usage of the same table per user
    sql_statements = [
        f"DROP TABLE {table_prefix}_embedding PURGE",
        f"""
        CREATE TABLE {table_prefix}_embedding (
            id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            text VARCHAR2(4000),
            vec VECTOR,
            source VARCHAR2(100)
        )
        """
    ]

    for stmt in sql_statements:
        try:
            cursor.execute(stmt)
        except Exception as e:
            # Ignore if table doesn't exist and create a new one
            print(f"Skipping error: {e}")

create_table()

# Step 5: Insert embeddings into DB
for i, emb in enumerate(embeddings):
    chunk_text = texts[i][:3900]  # ensure within VARCHAR2(4000) limit according to table constraint
    metadata_source = f"{splits[i].metadata.get('source', 'pdf-doc')}_start_{splits[i].metadata.get('start_index', 0)}"

    cursor.execute(
        f"INSERT INTO {table_prefix}_embedding (text, vec, source) VALUES (:1, :2, :3)",
        [chunk_text, array.array("f", emb), metadata_source],
    )

db_connection.commit()

# Step 6: Define semantic search function
def semantic_search(query, top_k=3):
    """Perform semantic search over Oracle DB using cosine similarity."""

    query_payload = get_embed_payload([query], EmbedTextDetails.INPUT_TYPE_SEARCH_QUERY)
    query_response = embed_client.embed_text(query_payload)
    query_emb = query_response.data.embeddings[0]
    query_vec = array.array("f", query_emb)

    # Run vector similarity search in Oracle DB
    cursor.execute(f"""
        SELECT text, vector_distance(vec, :1, COSINE) AS distance, source
        FROM {table_prefix}_embedding
        ORDER BY distance
        FETCH FIRST {top_k} ROWS ONLY
    """, [query_vec])

    results = cursor.fetchall()
    print("\nTop Results:")
    for i, (text, dist, source) in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print(f"Distance: {dist:.4f}")
        print(f"Source: {source}")
        print(f"Snippet: {text[:200]}...\n")

# Step 7: Interactive loop for user queries
while True:
    q = input("\nAsk a semantic search query (or 'q' to quit): ").strip()
    if q.lower() == "q":
        break

    # Change the top_k parameter to retrieve the closest k results
    semantic_search(q,top_k=5)

# Step 8: Close DB connections
cursor.close()
db_connection.close()
print("DB session closed")
