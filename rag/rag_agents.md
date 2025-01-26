OCI RAG agents have a hard limit. We can only habve one agent in the tenancy. As this tenancy is shared, the same agent have to be shared by all users of the lab tenancy

Follow these steps 

1. find the knowledge base for your agent
   1. change the tenancy to Chicago 
   2. go to genrative ai agents
   2. select one of the existing agent 
   3. select one of the active knowledge bases
   4. select the knowledge base
   5. check teh bucket used by the datasource
2. upload the document to datasource found above
   1. change the tenancy to phx
   2. go to object storage and to the bucket seen earlier
   3. find the folder for knowledgebase
   4. upload your file 
3. restart the pipeline 
   1. change tenancy to Cicago
   2. navigate  agent, knowledgebase & data source
   3. click in the datasource
   4. wait for ingest to complete 
   5. click to create teh injestion job and wait for it to finish 
4. go to chat console ofr teh agent 
   1. go the agent 
   2. click on teh endpoint 
   3. click on launch chat 
   4. ask questions related to teh file uploaded
5. go to code 
   1. verify that the endpoint is correct for your agent 
   2. run the python program 
   3. ask questions related to teh file uploaded

# if you have errors running sample code reach out for help in #igiu-ai-learning