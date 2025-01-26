#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oracledb
import array
import oci
import sys
import os 

#####
#Setup
#Change the compartmentid to yhe ocid of your compartment
#Change the profile if needed
#####

CONFIG_PROFILE = "AISANDBOX"
compartmentId= "ocid1.compartment.oc1..aaaaaaaaxj6fuodcmai6n6z5yyqif6a36ewfmmovn42red37ml3wxlehjmga" 
endpointId= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

print (" change the table names & DB detais per your setup & uncomment ")
#sys.exit(1)

# Change to your wallet
DB_CONFIG_DIR = os.path.expanduser("~/.workshop/inno_wallet")
DB_USER = "ONNOVATE"
DB_PASS = "Welcome_2025"
DB_DSN = "innovationlab_medium"
DB_WALLET_LOC=os.path.expanduser("~/.workshop/inno_wallet")
DB_WALLET_PASS="41_innovation" 

# The input text to vectorize
# https://pypi.org/project/pdfplumber/#extracting-text for pdf extractinga nd chnuinking 
sentences = [" Baseball is a great game ",
				"baseball games typically last 9 innings",
				"Baseball game can finish in about 2 hours",
				"Indias favroite passtime is cricket",
				"England's favorite passtime is football",
				"Football is called soccer in America",
				"baseball is americas favroite pass time sport"]

 
def create_table(cursor):
	sql = [
		"""drop table if exists asagarwa2_embedding purge"""	,
  
		"""
 		create table asagarwa2_embedding (
   			id number,
			text varchar2(4000),
			vec vector,
			primary key (id)
		)"""
	]
 
	for s in sql : 
		cursor.execute(s)


def insert_data(cursor, id, chunk, vec):
	cursor.execute("insert into asagarwa2_embedding values (:1, :2, :3)", [
				   id, chunk, vec])


def read_data(cursor):
	cursor.execute('select id,text from asagarwa2_embedding')
	for row in cursor:
		print(f"{row[0]}:{row[1]}")


def search_data(cursor, vec,):

 # COSINE, DOT, EUCLIDEAN
	cursor.execute("""
		select id,text, vector_distance(vec, :1, EUCLIDEAN) d 
		from asagarwa2_embedding
		order by d
		fetch first 10 rows only
	""", [vec])

	rows =[]
	for row in cursor:
		r = [row[0], row[1], row[2]]
		print(r)
		rows.append(r)

	return rows

#boilerplate text for embeddings
def get_embed_payload(chunks):
	embed_text_detail = EmbedTextDetails()
	embed_text_detail.serving_mode = OnDemandServingMode(model_id="cohere.embed-multilingual-v3.0")
	embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
	embed_text_detail.input_type = embed_text_detail.INPUT_TYPE_SEARCH_DOCUMENT
	embed_text_detail.compartment_id = compartmentId
	embed_text_detail.inputs = chunks
	return  embed_text_detail

def get_chat_request():
        cohere_chat_request = CohereChatRequest()
        cohere_chat_request.preamble_override = " answer only from selected docs, ignore any other information you may know"
        cohere_chat_request.is_stream = False 
        cohere_chat_request.max_tokens = 500
        cohere_chat_request.temperature = 0.75
        cohere_chat_request.top_p = 0.7
        cohere_chat_request.frequency_penalty = 1.0
        #cohere_chat_request.documents = get_documents()

        return cohere_chat_request

def get_chat_detail (llm_request):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id="cohere.command-r-plus-08-2024")
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail

 
def get_documents(chunks):
    docs =[]
    for chunk in chunks:
        doc = {
            "title" : f"document {chunk[0]}",
            "snippet" : chunk[1]
        } 
        docs.append(doc)
        
    return docs 

config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)


# create a llm client 
llm_client = GenerativeAiInferenceClient(
				config=config, 
				service_endpoint=endpointId, 
				retry_strategy=oci.retry.NoneRetryStrategy(),
				timeout=(10,240))	


print("creating embeddings")
response = llm_client.embed_text(get_embed_payload(sentences))
embeddings = response.data.embeddings

# insert & query  vectors
with oracledb.connect( config_dir= DB_CONFIG_DIR, user= DB_USER, password=DB_PASS, dsn=DB_DSN,wallet_location=DB_WALLET_LOC, wallet_password=DB_WALLET_PASS) as db:
	cursor = db.cursor()

	print("creating table")
	create_table(cursor)
	for i in range(len(embeddings)):
		insert_data(cursor, i, sentences[i], array.array("f",embeddings[i]))
		print(f"inserted {i}-{sentences[i]}")

	print("commiting")
	db.commit()

	print("reading")
	read_data(cursor)

	while True:
		query = input("Ask a question: ").strip().lower()
		q=[]
		q.append(query)
		prompt_embed = llm_client.embed_text (get_embed_payload(q))
		vec = array.array("f",prompt_embed.data.embeddings[0])
		
		# R of RAG : retrieving appicable text 
		print(f"searching for query:{query}")
		chunks = search_data(cursor,vec)

		# A of RAG : Augmenting the selected text
  
		llm_request = get_chat_request()
		llm_request.documents = get_documents(chunks)
		llm_payload =get_chat_detail(llm_request)
		
		# G of RAG generate a respomse usimg llm  
		llm_payload.chat_request.message = query
		llm_response = llm_client.chat(llm_payload)

  
		# Print result
		print("**************************Chat Result**************************")
		#llm_text = llm_response.data.chat_response.text
		print(llm_response.data.chat_response.text)
		print("************************** Citations**************************")
		print(llm_response.data.chat_response.citations)
