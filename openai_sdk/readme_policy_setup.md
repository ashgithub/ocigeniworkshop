# OCI Generative AI Policy set up for GA + OpenIA SDK usage

*Policies + Procedures for SDK + Console*

---

> For condensed view consult [quick_policy_set_up](./quick_policy_set_up.sh)

## 0. Prerequisites (Mandatory)

* Create **one compartment** for the workshop (recommended)
* Create IAM **group** (e.g., `genai-users`)
* **Add users to group** (CRITICAL)

```bash
oci iam group add-user --group-id <group_ocid> --user-id <user_ocid>
```

> Without this, policies exist but users still get permission errors.

* Ensure users have OCI config (`~/.oci/config`) for IAM authentication

---

## 1. Base Access (Required for Everything)

### ✅ Recommended (Workshop / Sandbox)

```bash
allow group <group> to manage generative-ai-family in compartment <compartment>
```

* Grants full access to:

  * Projects, Vector Stores, Files
  * NL2SQL, Containers, Connectors
* Simplest option for learning

---

### Production (Least Privilege)

```bash
allow group <group> to manage generative-ai-project in compartment <compartment>
allow group <group> to manage generative-ai-response in tenancy
allow group <group> to use generative-ai-family in compartment <compartment>
```

* `project` → required for GA API usage
* `response` → enables Responses API
* `use generative-ai-family` → allows inference (models, tools)

---

## 2. Authentication Setup

### Option A — IAM Auth (Recommended)

* Use:

  * `OciSessionAuth`
  * `OciResourcePrincipalAuth`

---

### Option B — API Key (Dev Only)

```bash
allow group <group> to manage generative-ai-response in tenancy
where ALL {request.principal.type='generativeaiapikey', request.principal.id='<api-key-ocid>'}
```

> ⚠️ Vector Store control plane **requires IAM**, not API keys

---

## 3. Generative AI Project (Mandatory)

* Create a **Generative AI Project** in OCI Console

Example SDK usage:

```python
client = OpenAI(
  project="ocid1.generativeaiproject..."
)
```

> Required for all API calls in GA (replaces compartment usage)

---

## 4. Vector Store (RAG / File Search)

```bash
allow group <group> to manage generative-ai-vectorstore in compartment <compartment>
allow group <group> to manage generative-ai-vectorstore-file in compartment <compartment>
allow group <group> to manage generative-ai-file in compartment <compartment>
```

### Required Workflow

1. Upload file
2. Create vector store
3. Attach file to vector store
4. Use `file_search` tool

---

## 5. Vector Store Connectors (Object Storage)

### Required Setup

* Create Object Storage **bucket**
* Upload files

### Dynamic Group

```text
ALL {resource.type='generativeaivectorconnector'}
```

### Policy

```bash
allow dynamic-group <vector-connector-dg> to read object-family in compartment <compartment>
```

> Enables ingestion from bucket

---

## 6. Semantic Store / NL2SQL

### Required Infrastructure

* Create **Autonomous DB (ADB)** or Oracle DB
* Create **DB Tools connections**:

  * Enrichment connection (high privilege)
  * Query connection (low privilege)

---

### Policies

```bash
allow group <group> to manage generative-ai-semantic-store in compartment <compartment>
allow group <group> to manage generative-ai-nl2sql in compartment <compartment>
```

---

### Dynamic Group

```text
ALL {resource.type='generativeaisemanticstore'}
```

---

### Required Permissions

```bash
allow dynamic-group <semantic-dg> to use database-tools-family in compartment <compartment>
allow dynamic-group <semantic-dg> to read database-family in compartment <compartment>
allow dynamic-group <semantic-dg> to read autonomous-database-family in compartment <compartment>
allow dynamic-group <semantic-dg> to read secret-family in compartment <compartment>
allow dynamic-group <semantic-dg> to use generative-ai-family in compartment <compartment>
```

---

## 7. Containers / Code Interpreter

```bash
allow group <group> to manage generative-ai-container in compartment <compartment>
```

### Notes

* Containers expire after ~20 minutes
* No persistent state unless files are re-uploaded

---

## 8. File Search Tool

No extra policy required beyond:

* `generative-ai-vectorstore-file`
* `generative-ai-family (use)`

> Uses vector store internally

---

## 9. Hosted Agents / Applications (Optional)

### Dynamic Group

```text
ALL {resource.type='generativeaihosteddeployment'}
```

### Policies

```bash
allow dynamic-group <deployment-dg> to read repos in compartment <compartment>
allow dynamic-group <deployment-dg> to read container-scan-results in compartment <compartment>
allow dynamic-group <deployment-dg> to read vss-family in compartment <compartment>

allow group <group> to manage generative-ai-hosted-application in compartment <compartment>
allow group <group> to manage generative-ai-hosted-deployment in compartment <compartment>
```

---

## 10. Summary Flow (End-to-End)

1. Setup IAM

   * create group
   * add users
   * attach policies

2. Create Project

3. Test API

   * call Responses API

4. RAG

   * upload file
   * create vector store
   * attach file
   * run file search

5. NL2SQL

   * create DB
   * create DB tools connections
   * create semantic store
   * run query

6. Connectors

   * create bucket
   * create connector
   * sync data

7. Tools

   * code interpreter
   * MCP tools (optional)

---

## 11. Common Errors (Debug)

| Error                        | Cause                                       |
| ---------------------------- | ------------------------------------------- |
| couldn't create vector store | Missing `generative-ai-vectorstore`         |
| permission denied inference  | Missing `generative-ai-family (use)`        |
| file upload fails            | Missing `generative-ai-file`                |
| NL2SQL fails                 | Missing DB / DB Tools / secrets             |
| connector fails              | Missing dynamic group or object storage     |
| API auth fails               | Missing project or `generative-ai-response` |

---

## Final Notes

* Use **`generative-ai-family`** for workshops to avoid friction
* Use **granular policies** for production
* Always:

  * add users to group
  * create project
  * configure DB for NL2SQL

---

## References (OCI Generative AI + SDK)

#### Core Generative AI Platform

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
  → Main entry point for OCI Generative AI

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/overview.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/overview.htm)
  → Service overview and concepts

#### Agentic API (Responses API)

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-responses-api.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-responses-api.htm)
  → How to use OCI Responses API (OpenAI-compatible)

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started.htm)
  → Getting started guide

#### IAM & Policies

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/iam-policies.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/iam-policies.htm)
  → All IAM policies for Generative AI

* [https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm)
  → General OCI IAM policy syntax

#### Vector Stores (RAG)

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-vector-store.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-vector-store.htm)
  → Vector store concepts and usage

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/vector-store-permissions.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/vector-store-permissions.htm)
  → Required permissions for vector stores

#### Files API

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-files.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-files.htm)
  → Upload and manage files

#### File Search (RAG Tool)

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-file-search.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-file-search.htm)
  → Using file search with vector stores

#### Vector Store Connectors

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-vector-store-connectors.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-vector-store-connectors.htm)
  → Sync data from Object Storage

#### NL2SQL / Semantic Store

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started-agents.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started-agents.htm)
  → Semantic store + NL2SQL setup

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-semantic-store.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-semantic-store.htm)
  → Manage semantic stores

#### Database Tools (Required for NL2SQL)

* [https://docs.oracle.com/en-us/iaas/database-tools/doc/database-tools-overview.html](https://docs.oracle.com/en-us/iaas/database-tools/doc/database-tools-overview.html)
  → Database Tools service overview

#### Containers / Code Interpreter

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-containers.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-containers.htm)
  → Containers API (code interpreter backend)

#### Hosted Applications (Deploy Agents)

* [https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-hosted-applications.htm](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-hosted-applications.htm)
  → Deploy agents as services

#### Authentication (IAM + SDK)

* [https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm)
  → OCI authentication methods

* [https://github.com/oracle-samples/oci-genai-auth-python](https://github.com/oracle-samples/oci-genai-auth-python)
  → OCI GenAI IAM auth helper (Python)

#### OpenAI SDK (Used with OCI)

* [https://developers.openai.com/api/docs](https://developers.openai.com/api/docs)
  → OpenAI Responses API spec (compatible with OCI)
