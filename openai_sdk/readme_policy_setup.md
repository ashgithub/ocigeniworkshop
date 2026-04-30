---

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
