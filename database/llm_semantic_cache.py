"""
What this file does:
Demonstrates semantic caching using OCI Generative AI embeddings and Oracle Database vector search. It stores Q&A pairs as embeddings and retrieves semantically similar answers for user queries, reducing the need for repeated LLM calls.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Oracle DB Vectors: https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference/models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run database/llm_semantic_cache.py

Comments to important sections of file:
- Step 1: Load config and initialize clients.
- Step 2: Set up Oracle DB connection and create vector table.
- Step 3: Generate embeddings for Q&A pairs.
- Step 4: Insert embeddings into DB.
- Step 5: Interactive semantic search and response.
"""

import os
import array
import oci
import oracledb
from dotenv import load_dotenv
from envyaml import EnvYAML
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails

# Constants
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

EMBED_MODEL = "cohere.embed-multilingual-v3.0"
# Available embedding models: cohere.embed-english-v3.0, cohere.embed-multilingual-v3.0, cohere.embed-english-light-v3.0, cohere.embed-multilingual-light-v3.0

LLM_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# Available models with tool calling support: cohere.command-r-08-2024, cohere.command-r-plus-08-2024, cohere.command-a-03-2025
LLM_MODEL = "cohere.command-a-03-2025"

# Sample Q&A pairs for semantic caching
qa_pairs = [
    {
        "question": "What is the largest continent by land area?",
        "answer": "Asia is the largest continent, covering about 30% of Earth's land area. It is home to diverse cultures, languages, and ecosystems."
    },
    {
        "question": "Which country has the longest coastline in the world?",
        "answer": "Canada has the longest coastline, stretching over 202,080 kilometers. Its vast coastlines are along the Atlantic, Pacific, and Arctic Oceans."
    },
    {
        "question": "What river is the longest in the world?",
        "answer": "The Nile River is traditionally considered the longest river, flowing over 6,650 kilometers through northeastern Africa. It passes through countries like Egypt and Sudan."
    },
    {
        "question": "Which desert is the largest hot desert in the world?",
        "answer": "The Sahara Desert is the largest hot desert, covering approximately 9.2 million square kilometers. It spans across North Africa from the Atlantic Ocean to the Red Sea."
    },
    {
        "question": "What is the smallest country in the world by land area?",
        "answer": "Vatican City is the smallest country, with an area of just 44 hectares (110 acres). It serves as the spiritual and administrative center of the Roman Catholic Church."
    },
    {
        "question": "Which mountain is the highest in the world above sea level?",
        "answer": "Mount Everest is the highest mountain above sea level, standing at 8,848 meters (29,029 feet). It is part of the Himalayas and located on the border between Nepal and China."
    },
    {
        "question": "What ocean is the deepest in the world?",
        "answer": "The Pacific Ocean is the deepest ocean, with an average depth of about 4,280 meters. The Mariana Trench within it reaches depths of over 10,900 meters."
    },
    {
        "question": "Which two continents are entirely located in the Southern Hemisphere?",
        "answer": "Australia and Antarctica are entirely located in the Southern Hemisphere. Both continents have unique ecosystems and climates."
    },
    {
        "question": "What country has the most time zones?",
        "answer": "France has the most time zones when including its overseas territories. In total, it spans 12 different time zones across various regions worldwide."
    },
    {
        "question": "Which lake is considered the world's largest by surface area?",
        "answer": "Lake Superior, part of North America's Great Lakes, is often considered the largest freshwater lake by surface area. It covers approximately 82,100 square kilometers."
    }
]

def load_config(config_path):
    """Load configuration from a YAML file."""
    
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def create_table(cursor, table_prefix):
    """Drop and create semantic cache table."""
    sql_statements = [
        f"DROP TABLE {table_prefix}_semantic_cache PURGE",
        f"""
        CREATE TABLE {table_prefix}_semantic_cache (
            id NUMBER,
            question VARCHAR2(4000),
            answer VARCHAR2(4000),
            embedding VECTOR,
            PRIMARY KEY (id)
        )
        """
    ]

    for stmt in sql_statements:
        try:
            cursor.execute(stmt)
        except Exception as e:
            # Ignore if table doesn't exist and create a new one
            print(f"Skipping error: {e}")


def insert_data(cursor, table_prefix, id, question, answer, vec):
    """Insert Q&A pair with embedding into table."""
    cursor.execute(f"INSERT INTO {table_prefix}_semantic_cache VALUES (:1, :2, :3, :4)", [
        id, question, answer, vec
    ])


def read_data(cursor, table_prefix):
    """Read and display all Q&A pairs from table."""
    cursor.execute(f"SELECT id, question, answer FROM {table_prefix}_semantic_cache")
    for row in cursor:
        print(f"{row[0]}:{row[1]}:{[row[2]]}")


def search_data(cursor, table_prefix, vec, top_k=3):
    """Perform semantic search with cosine similarity."""
    # Try adding the constraint the distance of < 0.5, something we will need to finetune based on data
    cursor.execute(f"""
        SELECT id, question, answer, vector_distance(embedding, :1, COSINE) d
        FROM {table_prefix}_semantic_cache
        ORDER BY d
        FETCH FIRST {top_k} ROWS ONLY
    """, [vec])

    rows = []
    for row in cursor:
        r = [row[0], row[1], row[2], row[3]]
        print(r)
        rows.append(r)

    return rows


def get_embed_payload(questions, embed_type, compartment_id):
    """Build embedding payload for OCI Generative AI."""
    embed_text_detail = EmbedTextDetails()
    embed_text_detail.serving_mode = OnDemandServingMode(model_id=EMBED_MODEL)
    embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
    embed_text_detail.input_type = embed_type
    embed_text_detail.compartment_id = compartment_id
    embed_text_detail.inputs = questions
    return embed_text_detail



# Step 1: Load config and initialize clients
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(
    os.path.expanduser(scfg["oci"]["configFile"]),
    scfg["oci"]["profile"]
)
compartment_id = scfg["oci"]["compartment"]
table_prefix = scfg["db"]["tablePrefix"]
wallet_path = os.path.expanduser(scfg["db"]["walletPath"])

# Create LLM client
llm_client = GenerativeAiInferenceClient(
    config=config,
    service_endpoint=LLM_ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

# Step 2: Set up Oracle DB connection and create vector table
db_connection = oracledb.connect(
    config_dir=wallet_path,
    user=scfg["db"]["username"],
    password=scfg["db"]["password"],
    dsn=scfg["db"]["dsn"],
    wallet_location=wallet_path,
    wallet_password=scfg["db"]["walletPass"]
)
cursor = db_connection.cursor()

print("Creating table for semantic cache...")
create_table(cursor, table_prefix)

# Step 3: Generate embeddings for Q&A pairs
print("Generating embeddings for Q&A pairs...")
embed_payload = get_embed_payload(
    [pair["question"] for pair in qa_pairs],
    EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT,
    compartment_id
)
embed_response = llm_client.embed_text(embed_payload)
embeddings = embed_response.data.embeddings

print(f"Generated {len(embeddings)} embeddings.")

# Step 4: Insert embeddings into DB
for i, emb in enumerate(embeddings):
    insert_data(cursor, table_prefix, i, qa_pairs[i]['question'], qa_pairs[i]['answer'], array.array("f", emb))
    print(f"Inserted Q&A pair {i}")

db_connection.commit()

print("Reading stored Q&A pairs...")
read_data(cursor, table_prefix)

# Step 5: Interactive semantic search and response
print("\nReady for queries. Try rephrasing questions to test semantic matching.")
print("Suggestions for experimentation:")
print("- Change the embedding model (e.g., to 'cohere.embed-english-v3.0')")
print("- Adjust top_k parameter in search_data for more/less results")
print("- Add distance threshold filtering in search query")
print("- Experiment with different similarity algorithms (COSINE, DOT, EUCLIDEAN)")

while True:
    query = input("\nAsk a question (or 'q' to exit): ").strip()
    if query.lower() == "q":
        break

    query_list = [query]
    query_payload = get_embed_payload(
        query_list,
        EmbedTextDetails.INPUT_TYPE_SEARCH_QUERY,
        compartment_id
    )
    query_response = llm_client.embed_text(query_payload)
    query_vec = array.array("f", query_response.data.embeddings[0])

    print(f"Searching for: '{query}'")
    results = search_data(cursor, table_prefix, query_vec, top_k=5)

    print("\n************************** SEMANTIC CACHE RESULTS **************************")
    if results:
        print(f"Best match answer: {results[0][2]}")
        print("\nOther similar questions and distances:")
        for result in results:
            print(f"{result[3]:.4f}: {result[1]}")
    else:
        print("No matches found.")

# Close DB connections
cursor.close()
db_connection.close()
print("Database connection closed.")
