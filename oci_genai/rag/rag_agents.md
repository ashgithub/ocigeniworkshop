# OCI GenAI Agent Service

OCI RAG agents have a practical shared-usage constraint in this sandbox environment. Because the tenancy is shared, users typically work with the same agent by adding documents to the associated knowledge base and rerunning ingestion.

## Steps in OCI Console

1. **Find the knowledge base for your agent**:
   - Change tenancy to Chicago.
   - Go to Generative AI Agents. If no active agent exists, follow console steps to create one.
   - Select one of the existing active agents.
   - Select one of the active knowledge bases for that agent.
   - Select the data source for the knowledge.
   - Note the bucket used by the datasource.

2. **Upload the document to the data source**:
   - Change tenancy to Phoenix.
   - Go to Object Storage and to the bucket found in step 1.
   - Find the folder for the knowledge base.
   - Upload your file.

3. **Restart the ingestion pipeline**:
   - Change tenancy to Chicago.
   - Navigate to agent, knowledge base.
   - Click on the datasource.
   - Create a new ingestion job.
   - Wait for ingestion to complete (track % in Work Requests for ingestion job).
   - Small files are faster; large files may take >5 mins.

4. **Go to the chat console for the agent**:
   - Go to the agent.
   - Click on the endpoint.
   - Click on Launch Chat.
   - Ask questions related to the uploaded file.

5. **Run the code example**:
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
