-- What this file does:
-- Demonstrates full RAG (Retrieval-Augmented Generation) implementation in Oracle 23ai using vector embeddings and AI profiles.
-- Shows how to create vector indexes from documents stored in Object Storage and perform natural language queries with citations.

-- Documentation to reference:
-- - Oracle 23ai Select AI: https://docs.oracle.com/en/cloud/paas/autonomous-database/select-ai/
-- - DBMS_CLOUD_AI Package: https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/DBMS_CLOUD_AI.html
-- - Vector Operations: https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/

-- Relevant slack channels:
-- - #adb-select-ai-users: questions about Oracle 23ai Select AI
-- - #igiu-innovation-lab: general discussions on your project
-- - #igiu-ai-learning: help with sandbox environment or help with running this code

-- Prerequisites:
-- 1. Oracle 23ai Autonomous Database with Select AI enabled
-- 2. OCI credentials configured with proper permissions
-- 3. Object Storage bucket with documents for indexing
-- 4. OCI_GENAI_CRED credential created in the database

-- How to run the file:
-- 1. Update the bucket location URL below to point to your Object Storage bucket
-- 2. Execute this script in SQL*Plus or SQL Developer connected to your 23ai database
-- 3. Run the sample queries at the end to test the RAG functionality

-- Step 1: Clean up existing profile and vector index
BEGIN
    dbms_cloud_ai.drop_profile(
        profile_name => 'ocirag',
        force => true
    );
END;
/

BEGIN
    DBMS_CLOUD_AI.DROP_VECTOR_INDEX(
        index_name => 'RAG_INDEX'
    );
END;
/

-- Step 2: Create AI profile for RAG operations
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'ocirag',
        attributes => '{
            "provider": "oci",
            "credential_name": "OCI_GENAI_CRED",
            "model": "meta.llama-4-scout-17b-16e-instruct",
            "vector_index_name": "RAG_INDEX"
        }'
    );
END;
/

-- Step 3: Set the active profile
BEGIN
    dbms_cloud_ai.set_profile(
        profile_name => 'ocirag'
    );
END;
/

-- Step 4: Create vector index from documents in Object Storage
-- NOTE: Update the location URL below to point to your Object Storage bucket containing documents
BEGIN
    DBMS_CLOUD_AI.CREATE_VECTOR_INDEX(
        index_name => 'RAG_INDEX',
        attributes => '{
            "vector_db_provider": "oracle",
            "location": "https://objectstorage.us-phoenix-1.oraclecloud.com/n/axaemuxiyife/b/workshopbucket/o/AAGARWA/kb-test/",
            "object_storage_credential_name": "OCI_GENAI_CRED",
            "profile_name": "ocirag",
            "vector_dimension": 1024,
            "vector_distance_metric": "cosine",
            "chunk_overlap": 128,
            "chunk_size": 1024
        }'
    );
END;
/

-- Step 5: Sample RAG queries
-- Set formatting for better output display
SET PAGES 100
SET LINESIZE 150

-- Basic narration query
SELECT AI narrate 'tell me about France';

-- Query with specific information request
SELECT AI narrate 'tell me three things about Pope Pius XII';

-- Troubleshooting queries (run these if you encounter issues)
-- Check pipeline history
SELECT * FROM user_cloud_pipeline_history;

-- Check active pipelines
SELECT * FROM USER_CLOUD_PIPELINES;

-- Check load operations
SELECT * FROM USER_LOAD_OPERATIONS;

-- Check for running jobs
SELECT job_name, error#, errors
FROM DBA_SCHEDULER_RUNNING_JOBS
WHERE job_name LIKE 'PIPELINE%';

-- Check vector table contents
SELECT * FROM RAG_INDEX$VECTAB;
