from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

# sample document base
documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"},
    ),
]

# Loading pdf files
file_path = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/langChain/rag/Sample1.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

# print(len(docs))
# print(f"{docs[0].page_content[:200]}\n")
# print(docs[0].metadata)

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

print(all_splits)

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
# # import oracledb
import array
import oci
import os,json 

SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/ocigeniworkshop/sandbox.json"

EMBED_MODEL = "cohere.embed-multilingual-v3.0"
LLM_MODEL = "cohere.command-r-08-2024"
# # cohere.command-a-03-2025
# # cohere.command-r-08-2024
# # cohere.command-r-plus-08-2024
# # meta.llama-3.1-405b-instruct
# # meta.llama-3.3-70b-instruct
# # meta.llama-3.2-90b-vision-instruct
# # meta.llama-4-maverick-17b-128e-instruct-fp8
# # meta.llama-4-scout-17b-16e-instruct

 
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# # here we are starting with samll chunks. Idelaly you will have to parse teh file and chunk it using a library
# # there are quite a few strategies on parsing and chunking. do you wn ownresearch and enahcne this code. 
# chunks = [
#     			"Baseball is a great game ",
# 				"baseball games typically last 9 innings",
# 				"Baseball game can finish in about 2 hours",
# 				"Indias favroite passtime is cricket",
# 				"England's favorite passtime is football",
# 				"Football is called soccer in America",
# 				"baseball is americas favroite pass time sport"]

# # we are mocking the cource of chunks. this will be used in citations. This helps build confidence, avoid hallucination. 
# chunk_source = [ 
#                 {"chapter":"Baseball", "question":"1"},
#                 {"chapter":"Baseball", "question":"2"},
#                 {"chapter":"Baseball", "question":"3"},
#                 {"chapter":"Cricket", "question":"1"},
#                 {"chapter":"Football", "question":"1"},
#                 {"chapter":"Football", "question":"2"},
#                 {"chapter":"Baseball", "question":"4"},
	
# ]
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
		f"""drop table if exists {tablename_prefix}_embedding purge"""	,
  
		f"""
 		create table {tablename_prefix}_embedding (
   			id number,
			text varchar2(4000),
			vec vector,
			chapter varchar2(100),
			section integer,
			primary key (id)
		)"""
	]
 
	for s in sql : 
		cursor.execute(s)


def insert_data(cursor, id, chunk, vec,chapter, section):
	cursor.execute(f"insert into {tablename_prefix}_embedding values (:1, :2, :3, :4, :5)", [
				   id, chunk, vec,chapter,section])


# def read_data(cursor):
# 	cursor.execute(f"select id,text from {tablename_prefix}_embedding")
# 	for row in cursor:
# 		print(f"{row[0]}:{row[1]}")


# def search_data(cursor, vec,):

#  # COSINE, DOT, EUCLIDEAN
#  # try adding an constraint on the distance eg < 0.5 is something we will need to finetune based on data 
# 	cursor.execute(f"""
# 		select id,text, vector_distance(vec, :1, COSINE) d, chapter,section 
# 		from {tablename_prefix}_embedding
# 		order by d
# 		fetch first 3 rows only
# 	""", [vec])

# 	rows =[]
# 	for row in cursor:
# 		r = [row[0], row[1], row[2], f"chapter:[{row[3]}]_section:[{row[4]}]"]
# 		print(r)
# 		rows.append(r)

# 	return rows

# #boilerplate text for embeddings
def get_embed_payload(chunks, embed_type):
	embed_text_detail = EmbedTextDetails()
	embed_text_detail.serving_mode = OnDemandServingMode(model_id=EMBED_MODEL)
	embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
	embed_text_detail.input_type = embed_type 
	embed_text_detail.compartment_id = compartmentId
	embed_text_detail.inputs = chunks
	return  embed_text_detail

# def get_chat_request():
#         cohere_chat_request = CohereChatRequest()
#         cohere_chat_request.preamble_override = " answer only from selected docs, ignore any other information you may know"
#         cohere_chat_request.is_stream = False 
#         cohere_chat_request.max_tokens = 500
#         cohere_chat_request.temperature = 0.75
#         cohere_chat_request.top_p = 0.7
#         cohere_chat_request.frequency_penalty = 1.0
#         #cohere_chat_request.documents = get_documents()

#         return cohere_chat_request

# def get_chat_detail (llm_request):
#         chat_detail = ChatDetails()
#         chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
#         chat_detail.compartment_id = compartmentId
#         chat_detail.chat_request = llm_request

#         return chat_detail


# # here are omitting the reranking step.
# # reranking is an optional step which can order the set of documents retrived and take a the top few to LLM  
# # as eg, we get top 5 rows from db similarity search, reanak and send top 3 to LLM 
def get_documents(chunks):
    docs =[]
    for chunk in chunks:
        doc = {
            "id" : chunk[3],
            "snippet" : chunk[1]
        } 
        docs.append(doc)
        
    return docs 

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
response = llm_client.embed_text(get_embed_payload(all_splits,EmbedTextDetails.INPUT_TYPE_SEARCH_DOCUMENT))
embeddings = response.data.embeddings

# # insert & query  vectors
# with oracledb.connect(  config_dir=scfg["db"]["walletPath"],user= scfg["db"]["username"], password=scfg["db"]["password"], dsn=scfg["db"]["dsn"],wallet_location=scfg["db"]["walletPath"],wallet_password=scfg["db"]["walletPass"]) as db:
# 	cursor = db.cursor()

# 	print("creating table")
# 	create_table(cursor)
# 	for i in range(len(embeddings)):
# 		insert_data(cursor, i, chunks[i], array.array("f",embeddings[i]),chunk_source[i]["chapter"], chunk_source[i]["question"] )
# 		print(f"inserted {i}-{chunks[i]}")

# 	print("commiting")
# 	db.commit()

# 	print("reading")
# 	read_data(cursor)

# 	while True:
# 		query = input("Ask a question: ").strip().lower()
# 		q=[]
# 		q.append(query)
# 		prompt_embed = llm_client.embed_text (get_embed_payload(q,EmbedTextDetails.INPUT_TYPE_SEARCH_QUERY))
# 		vec = array.array("f",prompt_embed.data.embeddings[0])
		
# 		# R of RAG : retrieving appicable text 
# 		print(f"searching for query:{query}")
# 		chunks = search_data(cursor,vec)

# 		# A of RAG : Augmenting the selected text

# 		# RERANK
  
# 		llm_request = get_chat_request()
# 		llm_request.documents = get_documents(chunks)
# 		llm_payload =get_chat_detail(llm_request)
		
# 		# G of RAG generate a respomse usimg llm  
# 		llm_payload.chat_request.message = query
# 		llm_response = llm_client.chat(llm_payload)

  
# 		# Print result
# 		print("**************************Chat Result**************************")
# 		#llm_text = llm_response.data.chat_response.text
# 		print(llm_response.data.chat_response.text)
# 		print("************************** Citations**************************")
# 		print(llm_response.data.chat_response.citations)
