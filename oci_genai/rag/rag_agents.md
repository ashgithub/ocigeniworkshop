# OCI Gen AI Agent Service

OCI RAG agents have a hard usage limit. We can only have one agent in the tenancy. As this tenancy is shared, we all use the same agent by adding our documents to the knowledge base associated with the agent and rerunning the ingestion job.

## Steps in OCI Console

1. **Find the knowledge base for your agent**:
   - Change tenancy to Chicago.
   - Go to Generative AI Agents. If no active agent exists, follow console steps to create one.
   - Select one of the existing active agents.
   - Select one of the active knowledge bases for that agent.
   - Select the data source for the knowledge.
   - Note the bucket used by the datasource.

2. **Upload the document to datasource**:
   - Change tenancy to Phoenix.
   - Go to Object Storage and to the bucket found in step 1.
   - Find the folder for the knowledge base.
   - Upload your file.

3. **Restart the pipeline**:
   - Change tenancy to Chicago.
   - Navigate to agent, knowledge base.
   - Click on the datasource.
   - Create a new ingestion job.
   - Wait for ingestion to complete (track % in Work Requests for ingestion job).
   - Small files are faster; large files may take >5 mins.

4. **Go to chat console for the agent**:
   - Go to the agent.
   - Click on the endpoint.
   - Click on Launch Chat.
   - Ask questions related to the uploaded file.

5. **Go to code**:
   - Verify endpoint in sandbox.yaml matches your agent.
   - Run the Python script.
   - Ask questions related to the uploaded file.

## Errors Running Sample Code?

Reach out for help in #igiu-ai-learning.

## Experimentation Ideas

- Upload PDFs with images/charts and query about visuals.
- Ingest multiple docs and see how the agent handles cross-doc questions.
- Compare responses before/after ingestion.
- Try different file types (text, docs).
