

-- What this file does:
-- Demonstrates Oracle 23ai Select AI capabilities for natural language database queries.
-- Shows different AI query modes (narrate, showsql, explainsql, chat) and how they work with the SH schema.

-- Documentation to reference:
-- - Oracle 23ai Select AI: https://docs.oracle.com/en/cloud/paas/autonomous-database/select-ai/
-- - Select AI Examples: https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/select-ai-examples.html
-- - DBMS_CLOUD_AI Package: https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/DBMS_CLOUD_AI.html

-- Relevant slack channels:
-- - #adb-select-ai-users: questions about Oracle 23ai Select AI
-- - #igiu-innovation-lab: general discussions on your project
-- - #igiu-ai-learning: help with sandbox environment or help with running this code

-- Prerequisites:
-- 1. Oracle 23ai Autonomous Database with Select AI enabled
-- 2. Access to the SH (Sales History) sample schema
-- 3. OCI credentials configured for GenAI access

-- How to run the file:
-- 1. Update the credential details below with your OCI information
-- 2. Execute this script in SQL*Plus or SQL Developer connected to your 23ai database
-- 3. Test the various AI query examples

-- Step 1: Verify database connection
SELECT USER FROM DUAL;

-- Step 2: Create OCI credential for GenAI access
-- IMPORTANT: Replace the placeholder values below with your actual OCI credentials
-- You can find these details in your ~/.oci/config file and private key file
-- NOTE: This is your PRIVATE key, not the public key referenced in the config
BEGIN

    DBMS_CLOUD.DROP_CREDENTIAL(
        credential_name => 'AISANDBOX_CRED'
    );
BEGIN
    DBMS_CLOUD.CREATE_CREDENTIAL(
        credential_name => 'your_oracle_id_CRED',
        user_ocid => 'your-user-ocid-here',
        tenancy_ocid => 'your-tenancy-ocid-here',
        private_key => '-----BEGIN PRIVATE KEY-----
your-private-key-content-here
-----END PRIVATE KEY-----',
        fingerprint => 'your-key-fingerprint-here'
    );
END;

-- Step 3: Clean up existing profile
BEGIN
    dbms_cloud_ai.drop_profile(
        profile_name => 'workshop_app_profile',
        force => true
    );
END;
/

-- Step 4: Create AI profile for SH schema
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'workshop_app_profile',
        attributes => '{
            "provider": "oci",
            "credential_name": "AISANDBOX_CRED",
            "model": "meta.llama-4-scout-17b-16e-instruct",
            "comments": "true",
            "object_list": [{"owner": "WORKSHOP_ADMIN"}]
        }'
    );
END;
/

-- Step 5: Set the active profile
BEGIN
    dbms_cloud_ai.set_profile(
        profile_name => 'workshop_app_profile'
    );
END;
/

-- Step 6: Configure output formatting
SET WRAP ON

-- Step 7: Sample Select AI queries demonstrating different modes

-- Basic AI query - returns natural language answer
SELECT AI 'how many students exist';

-- Show the SQL that would be executed
SELECT AI showsql 'how many students have completed omnboarding tasks, by number of tasks in descentimng order'
SELECT AI explainsql 'how many students have completed omnboarding tasks, by number of tasks in descentimng order'
SELECT AI runsql 'how many students have completed omnboarding tasks, group by number of tasks in descentimng order, show me number of tasks completed and how many students completed that many tasjk. '
SELECT AI narrate 'how many students have completed omnboarding tasks, by number of tasks in descentimng order'
SELECT AI 'how many students have completed omnboarding tasks, by number of tasks in descentimng order'

-- Explain the SQL that would be executed
SELECT AI explainsql 'how many customers exist';

-- Run the SQL and return results
SELECT AI runsql 'how many customers exist';

-- Narrative answer (same as basic AI query)
SELECT AI narrate 'how many customers exist';

-- Chat mode for conversational queries
SELECT AI chat 'how many customers exist';
SELECT AI chat 'why is the sky blue';

-- Complex queries with filtering
SELECT AI showsql 'how many customers in San Francisco are married';

-- Business intelligence style queries
SELECT AI 'find top 3 baby boomer big spenders';
SELECT AI showsql 'find top 3 baby boomer big spenders';

