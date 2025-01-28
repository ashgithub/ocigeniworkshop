## OCI Gen AI Agent service 

OCI RAG agents have a hard usagelimit. We can only have one agent in the tenancy. As this tenancy is shared, We all us ethe same agent by adding our documents to the knowledge base associated with the agent. and rerunning the ingestion job.  


Follow these steps in your OCI console.

1. find the knowledge base for your agent
   1. change the tenancy to Chicago 
   2. Go to genrative ai agents. If no active agent exists, ignore the the rest of the document and follow the step on console
   2. Select one of the existing active agent 
   3. Select one of the active knowledge bases for that agent 
   4. select the data source for the knowledge
   5. check teh bucket used by the datasource
2. Upload the document to datasource found above
   1. Change the tenancy to phx
   2. Go to object storage and to the bucket we found in the steps above
   3. Find the folder for knowledgebase
   4. Upload your file 
3. Restart the pipeline 
   1. Change tenancy to Chicago
   2. Navigate  agent, knowledgebase & data source
   3. Click in the datasource and select the new file
   4. Check teh auto restart the ingestuin job
   5. Wait for ingest to complete 
   6. Click to create teh injestion job and wait for it to finish 
4. go to chat console for the agent 
   1. Go the agent 
   2. Click on the endpoint 
   3. Click on launch chat 
   4. Ask questions related to teh file uploaded
5. Go to code 
   1. Verify that the endpoint is correct for your agent 
   2. Run the python program 
   3. Ask questions related to teh file uploaded

# if you have errors running sample code reach out for help in #igiu-ai-learning