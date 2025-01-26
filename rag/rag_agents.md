OCI RAG agents have a hard limit. We can only habve one agent in the tenancy. As this tenancy is shared, the same agent have to be shared by all users of the lab tenancy

Follow these steps 

1. find the knowledge base for your agent
   1. change the tenancy to chicao 
   2. go to genrative ai agents
   3. select the knowledge base
   4.    
2. upload the document to knowlede base
   1. change the tenancy to phx
   2. go to object storage and to your bucket
   3. find the folder for knowledgebase
   4. upload your file 
3. restart the pipeline 
   1. change tenancy to chicago
   2. go to agent
   3. re=run the pipeline
   4. wait ofr ingest to complete 
4. go to console 
   1. ask questions 
5. go to code 
   1. verify that the endpoint is correct ofr your agent 
   2. run the python program 

# if you have errors running sample code reach out for help in #igiu-ai-learning