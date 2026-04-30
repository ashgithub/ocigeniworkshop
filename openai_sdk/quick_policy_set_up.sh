############################################
# 0. PREREQUISITES (MANDATORY)
############################################
# - Create ONE compartment for the workshop (recommended)
# - Create IAM group (e.g., genai-users)
# - ADD USERS TO GROUP (CRITICAL — often missed)

oci iam group add-user --group-id <group_ocid> --user-id <user_ocid>
# Without this → policies exist but users still get denied

# - Ensure users have OCI config (~/.oci/config) for IAM auth

############################################
# 1. BASE ACCESS (REQUIRED FOR EVERYTHING)
############################################

# 🔥 RECOMMENDED FOR WORKSHOP (simple, avoids errors)
allow group <group> to manage generative-ai-family in compartment <compartment>
# Gives full access to:
# - Projects, Vector Stores, Files, NL2SQL, Containers, Connectors
# Best for learning / sandbox

# 🔐 PRODUCTION (least privilege alternative)
allow group <group> to manage generative-ai-project in compartment <compartment>
# REQUIRED → Project is mandatory in GA (API won’t work without it)

allow group <group> to manage generative-ai-response in tenancy
# REQUIRED → enables Responses API (LLM calls, tools)

allow group <group> to use generative-ai-family in compartment <compartment>
# REQUIRED → inference (models, file_search, code interpreter, etc.)


############################################
# 2. AUTHENTICATION SETUP (MANDATORY)
############################################

# OPTION A — IAM AUTH (RECOMMENDED)
# Use OciSessionAuth / OciResourcePrincipalAuth

# OPTION B — API KEY (DEV ONLY)
allow group <group> to manage generative-ai-response in tenancy
where ALL {request.principal.type='generativeaiapikey', request.principal.id='<api-key-ocid>'}

# NOTE:
# - Vector Store control plane DOES NOT support API key → IAM required
# - API key only works for inference endpoints


############################################
# 3. GENERATIVE AI PROJECT (MANDATORY)
############################################

# MUST create project in OCI Console before using SDK

# SDK usage:
# client = OpenAI(project="ocid1.generativeaiproject...")

# Doc confirms:
# “Project is required before using API” :contentReference[oaicite:0]{index=0}


############################################
# 4. VECTOR STORE (RAG / FILE SEARCH)
############################################

allow group <group> to manage generative-ai-vectorstore in compartment <compartment>
# Create/delete vector stores

allow group <group> to manage generative-ai-vectorstore-file in compartment <compartment>
# Add/remove/search indexed chunks

allow group <group> to manage generative-ai-file in compartment <compartment>
# Upload documents

# REQUIRED WORKFLOW (IMPORTANT):
# 1. Upload file
# 2. Create vector store
# 3. Attach file to vector store
# 4. Use file_search tool

# File Search depends on vector store (doc confirms) :contentReference[oaicite:1]{index=1}


############################################
# 5. VECTOR STORE CONNECTORS (OBJECT STORAGE)
############################################

# REQUIRED:
# - Create Object Storage bucket
# - Upload files

# Dynamic group:
ALL {resource.type='generativeaivectorconnector'}

# Policy:
allow dynamic-group <vector-connector-dg> to read object-family in compartment <compartment>
# Enables ingestion from bucket

# Without bucket setup → connector will fail silently


############################################
# 6. SEMANTIC STORE / NL2SQL (STRUCTURED DATA)
############################################

# REQUIRED INFRA (NOT JUST POLICIES):
# - Create Autonomous DB (ADB) or Oracle DB
# - Create DB Tools connections:
#   - Enrichment connection (high privilege)
#   - Query connection (low privilege)

allow group <group> to manage generative-ai-semantic-store in compartment <compartment>
# Create/manage semantic store

allow group <group> to manage generative-ai-nl2sql in compartment <compartment>
# Execute NL2SQL

# Dynamic group:
ALL {resource.type='generativeaisemanticstore'}

# REQUIRED PERMISSIONS:
allow dynamic-group <semantic-dg> to use database-tools-family in compartment <compartment>
# Access DB connections

allow dynamic-group <semantic-dg> to read database-family in compartment <compartment>
# Read schema metadata

allow dynamic-group <semantic-dg> to read autonomous-database-family in compartment <compartment>
# ADB metadata

allow dynamic-group <semantic-dg> to read secret-family in compartment <compartment>
# DB credentials

allow dynamic-group <semantic-dg> to use generative-ai-family in compartment <compartment>
# LLM inference

# Doc confirms DB + connections required :contentReference[oaicite:2]{index=2}


############################################
# 7. CONTAINERS / CODE INTERPRETER TOOL
############################################

allow group <group> to manage generative-ai-container in compartment <compartment>
# Required for code interpreter

# Notes:
# - Containers expire after ~20 minutes
# - No persistence unless files are re-uploaded


############################################
# 8. FILE SEARCH TOOL (RAG runtime)
############################################

# No extra policy needed beyond:
# - vectorstore-file
# - generative-ai-family (inference)

# File search uses vector store internally


############################################
# 9. HOSTED AGENTS / APPLICATIONS (OPTIONAL)
############################################

# Dynamic group:
ALL {resource.type='generativeaihosteddeployment'}

# Policies:
allow dynamic-group <deployment-dg> to read repos in compartment <compartment>
allow dynamic-group <deployment-dg> to read container-scan-results in compartment <compartment>
allow dynamic-group <deployment-dg> to read vss-family in compartment <compartment>

allow group <group> to manage generative-ai-hosted-application in compartment <compartment>
allow group <group> to manage generative-ai-hosted-deployment in compartment <compartment>

# Needed only if deploying agents


############################################
# 10. QUICK WORKSHOP FLOW (END-TO-END)
############################################

# STEP 1: Setup IAM
# - create group
# - add users
# - attach policies

# STEP 2: Create Project
# (MANDATORY for API)

# STEP 3: Test API
# - call responses API

# STEP 4: RAG
# - upload file
# - create vector store
# - attach file
# - run file_search

# STEP 5: NL2SQL
# - create DB
# - create DB tools connections
# - create semantic store
# - run NL2SQL query

# STEP 6: Connectors
# - create bucket
# - create connector
# - sync data

# STEP 7: Tools
# - code interpreter
# - MCP tools (optional)


############################################
# 11. COMMON ERRORS (DEBUG)
############################################

# "couldn't create vector store"
# → missing generative-ai-vectorstore

# "API works but tools fail"
# → missing generative-ai-family (use)

# "file upload fails"
# → missing generative-ai-file

# "NL2SQL fails"
# → missing DB + DB tools + secrets

# "connector fails"
# → missing dynamic group + object storage setup

# "API fails with auth"
# → missing project OR generative-ai-response policy