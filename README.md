## Welcome to the AI Developer learning path.

You can use this learning path with our AI sandbox. See instructions in #igiu-ai-learning slack channel.

Other resources of help:
1. [Training Video](https://oracle-my.sharepoint.com/:v:/p/ashish_ag_agarwal/EUIBQblxmdlGtxFPg6C6Vv4Byx9KZRCQWaoELwUvLMYyXw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=BC9qVl)
2. [Powerpoint](https://oracle-my.sharepoint.com/:p:/p/ashish_ag_agarwal/EW8530J_QrpTi8XIe3FMmZABjOfVlJQQkfoUqCNDxpUDQQ?e=HcViLd)


## Setup for running code locally
The examples are based on Python. Both Python code and notebook samples are available.


1. Request access to sandbox `#igiu-ai-learning`.
   - Set up API keys and DB access based on the document [here](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW).
   - Update the `sandbox.yaml` file per your environment.
  
2. Note the AI sandbox gives you access to two regions:
   1. Chicago: AI services, AI Playground, and Gen AI Agents are in this region.
   2. PHX: 23 AI Database, object buckets, and compute (if available) will be in this region.
   3. Object bucket in CHI is a read-only replica, so any files you drop in PHX will show up in Chicago automatically.
   4. Same bucket is shared by all users of AI sandbox; thus, best to use your Oracle User ID as `prefix` for your objects (configure it in `sandbox.yaml`).
   5. Same schema in 23ai will be shared by all users; thus, best to use your tables with your Oracle User ID as `prefix` for table names (configure in `sandbox.yaml`).

3. Setup VSCode and Python 3.11.5:
    - `pip install oci`
    - `pip install oracledb`
    - Run `AISandboxEnvCheck.py`.

4. We recommend following the learning path:
    - **llm**: Gets you started with OCI Generative APIs.
    - **RAG**: Looks at a few different ways in which we can get LLM to interact with non-public data.
    - **function_calling**: Quick introduction to Cohere's agentic framework using single and multi-step tools.
    - **speech**: Looks at OCI Speech APIs' text-to-speech and speech-to-text ability.
    - **vision**: A quick look at OCI's object and text detection ability and multimodal Llama model.
    - *database**: A quick look at  AI support in orcle databases 


5. OCI commands to clean your files from object buckets:
   - `oci os object bulk-delete -ns axaemuxiyife -bn workshopbucket --prefix AAGARWA/ --include ocid1\*`
   - `oci os object list --all --fields name,timeCreated --bucket-name=workshopbucket | grep AAGARWA`
   - `oci os object put -bn workshopbucket --prefix AAGARWA/ --file test.txt`

## Environment Variables
Create a `.env` file at the project root for sensitive values referenced in `sandbox.yaml`.

Example `.env`:
```
MY_PREFIX=your_oracle_id
DB_PASSWORD=your_db_password
```
Load with `python-dotenv` if needed: `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`.
