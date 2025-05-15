#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel
# if you have errors running sample code reach out for help in #igiu-ai-learning

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oracledb
import array
import oci
import os, json

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

EMBED_MODEL = "cohere.embed-multilingual-v3.0"

# cohere.embed-english-v3.0
# cohere.embed-multilingual-v3.0
# cohere.embed-english-light-v3.0 
# cohere.embed-multilingual-light-v3.0
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# available models with tool calling support
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# cohere.command-a-03-2025

#LLM_MODEL = "cohere.command-r-16k" 
LLM_MODEL = "cohere.command-a-03-2025" 



# The input text to vectorize
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

tablename_prefix = None
compartmentId = None

def load_config(config_path):
    """Load configuration from a JSON file."""
    
    try:
        with open(config_path, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{config_path}': {e}")
        return None

 
def create_table(cursor):
	sql = [
		f"""drop table if exists {tablename_prefix}_semantic_cache purge"""	,
  
  
		f"""
 		create table {tablename_prefix}_semantic_cache (
   			id number,
			question varchar2(4000),
			answer varchar2(4000),
			embedding vector,
			primary key (id)
		)"""
	]
 
	for s in sql : 
		cursor.execute(s)


def insert_data(cursor, id, question, answer, vec):
	cursor.execute(f"insert into {tablename_prefix}_semantic_cache values (:1, :2, :3, :4)", [
				   id, question, answer, vec])


def read_data(cursor):
	cursor.execute(f"select id,question,answer from {tablename_prefix}_semantic_cache")
	for row in cursor:
		print(f"{row[0]}:{row[1]}:{[row[2]]}")

 # COSINE, DOT, EUCLIDEAN
def search_data(cursor, vec,):
# try adding the constraint the distance of < 0.5 is something we will need to finetune based on data
	cursor.execute(f"""
		select id,question,answer, vector_distance(embedding, :1, COSINE) d 
		from {tablename_prefix}_semantic_cache
		order by d
		fetch first 3 rows only
	""", [vec])

	rows =[]
	for row in cursor:
		r = [row[0], row[1], row[2], row[3]]
		print(r)
		rows.append(r)

	return rows

#boilerplate text for embeddings
def get_embed_payload(questions,embed_type):
	embed_text_detail = EmbedTextDetails()
	embed_text_detail.serving_mode = OnDemandServingMode(model_id="cohere.embed-english-v3.0")
	embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
	embed_text_detail.input_type =embed_type 
	embed_text_detail.compartment_id = compartmentId
	embed_text_detail.inputs = questions
	return  embed_text_detail



#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])
compartmentId = scfg["oci"]["compartment"]
tablename_prefix = scfg["db"]["tablePrefix"]
wallet = os.path.expanduser(scfg["db"]["walletPath"])



# create a llm client 
llm_client = GenerativeAiInferenceClient(
				config=config, 
				service_endpoint=llm_service_endpoint, 
				retry_strategy=oci.retry.NoneRetryStrategy(),
				timeout=(10,240))	


print("creating embeddings")
response = llm_client.embed_text(get_embed_payload([pair["question"] for pair in qa_pairs], EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT))
embeddings = response.data.embeddings

# insert & query  vectors
with oracledb.connect(  config_dir=scfg["db"]["walletPath"],user= scfg["db"]["username"], password=scfg["db"]["password"], dsn=scfg["db"]["dsn"],wallet_location=scfg["db"]["walletPath"],wallet_password=scfg["db"]["walletPass"]) as db:
	cursor = db.cursor()

	print("creating table")
	create_table(cursor)
	for i in range(len(embeddings)):
		insert_data(cursor, i, qa_pairs[i]['question'],qa_pairs[i]['answer'], array.array("f",embeddings[i]))
		print(f"inserted {i}-{qa_pairs[i]}")

	print("commiting")
	db.commit()

	print("reading")
	read_data(cursor)

	while True:
		query = input("Ask a question: ").strip().lower()
		q=[]
		q.append(query)
		prompt_embed = llm_client.embed_text (get_embed_payload(q, EmbedTextDetails.INPUT_TYPE_SEARCH_QUERY))
		vec = array.array("f",prompt_embed.data.embeddings[0])
		
		# R of RAG : retrieving appicable text 
		print(f"searching for query:{query}")
		chunks = search_data(cursor,vec)

		print("**************************Chat Result**************************")
		print (f"Answer is {chunks[0][2]}")
		print ("\n other answers:\n")
		for chunk in chunks[0:3]: 
			print(f"{chunk[3]}:{chunk[1]}")