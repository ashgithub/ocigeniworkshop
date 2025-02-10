## Welcome to the AI Developer learning path. 

You can use this learning path with the our AI sandbox. See instructions in #igiu-ai-learning slack channel

Other resources of helpp: 
1. [Training Video](https://oracle-my.sharepoint.com/:v:/p/ashish_ag_agarwal/EUIBQblxmdlGtxFPg6C6Vv4Byx9KZRCQWaoELwUvLMYyXw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=BC9qVl)
2. [Powerpoint](https://oracle-my.sharepoint.com/:p:/p/ashish_ag_agarwal/EW8530J_QrpTi8XIe3FMmZABjOfVlJQQkfoUqCNDxpUDQQ?e=HcViLd)


## Setup for running code locally
The examples are based on python. Both python code & nobebook sampels are availble. 


1. Request access to sandbox `#igiu-ai-learning`
   - Set up api keys & db access based on document [here](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW)
   - Update the  `sanbox.json` file per your environment   
  
2. Note the AI sandbox gives you acess to two regions
   1. Chicago:  AI services, AI Playground & Gen AI Agents are in this reagion
   2. Phx : 23 AI Databse, Object buckets and compute (If  available) will be in this region
   3. Object bucket in CHI is a read only replica, so any files you drop in PHX will show up in chicago automatically
   4. Same bucket is shared by all users of AI sandbox, thus best to use your Oracle Userid  as `prefix` for your objects. (configure it in `sandbox.json`)
   5. Same schema in 23ai will be shared by all users, thus best to use your tables with your Oracle userid as `prefix` for table names. i(configure in `sandbox.json`)

3. Setup vscode &  python 3.11.5
    - pip install oci
    - pip install oracledb
    - run `AISandboxEnvCheck.py`  

5. We recommend following learning path 
    - **llm** : gets you started with OCI Generative APIs 
    - **Rag** : Looks at few different ways in which we can get LLM to interact with non public data
    - **function_calling** : Quick introduction to Cohere's agentic framework using single & multi-step tools
    - **speech**: Looks at OCI speech api's text to speech & Speech to text ability
    - **vision**: a quick look at OCI's object & text detection ability and multiodal llama model 


1. oci commands to clean your files from object buckets 
   - oci os object bulk-delete -ns axaemuxiyife -bn workshopbucket --prefix AAGARWA/ --include ocid1\*
   - oci os object list --all --fields name,timeCreated --bucket-name=workshopbucket | grep AAGARWA
   - oci os object put -bn workshopbucket --prefix AAGARWA/ --file test.txt
