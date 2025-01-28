## Welcome to the AI Developer learning path. 

You can use this learning path with the our AI sandbox. See instructions in #igiu-ai-learning slack channel

Other resources of helpp: 
1. [Training Video](https://oracle-my.sharepoint.com/:v:/p/ashish_ag_agarwal/EUIBQblxmdlGtxFPg6C6Vv4Byx9KZRCQWaoELwUvLMYyXw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=BC9qVl)
2. [Powerpoint](https://oracle-my.sharepoint.com/:p:/p/ashish_ag_agarwal/EW8530J_QrpTi8XIe3FMmZABjOfVlJQQkfoUqCNDxpUDQQ?e=HcViLd)


## Setup for running code locally
The examples are based on python. Both python code & nobebook sampels are availble. 


1. Request access to sandbox `#igiu-ai-learning`
    - set up your api key see task1 at https://oracle-livelabs.github.io/apex/ai-vision-lab/workshops/tenancy/index.html?lab=1-configure-oci#Task1:GenerateAPIKeysusingOCIConsole
    - set up `~/.oci/config` in your home directory using the api keys above
    - download wallet and setup sql developer (click on database connection here : https://cloud.oracle.com/db/adbs/ocid1.autonomousdatabase.oc1.phx.anyhqljsghwivzaajq6pzddmo4xbv5dtaytd2ctybjathmhcymf4vumagioa?region=null)
    - request the db userid/password in the #igiu-ai-learning channel

1. Note the AU sanbox gives you acess to two regions
   1. Chicago:  AI services& AI Playground, Gen AI Agents are in this reagion
   2. Phx : 23 AI Databse, Object buckets and compute (If  available) will be in this region
   3. Object bucket in CHI is a read only replica, so any files you drop in PHX will show up in chicago automatically
   4. Same bucket is shared by all users of AI sandbox, thus best to use your Oracle Userid  as `prefix` for your objects. (configure it in `sandbox.json`)
   5. Same schema in 23ai will be shared by all users, thus best to use your tables with your Oracle userid as `prefix` for table names. i(configure in `sandbox.json`)

2. Setup vscode &  python 3.11.5
    - pip install oci
    - pip install oracledb
    - run `AISandboxEnvCheck.py` 

3. Update the  `sanbox.json` file per your environment  

4. We recommend following learning path 
    - **llm** : gets you started with OCI Generative APIs 
    - **Rag** : Looks at few different ways in which we can get LLM to interact with non public data
    - **function_calling** : Quick introduction to Cohere's agentic framework using single & multi-step tools
    - **speech**: Looks at OCI speech api's text to speech & Speech to text ability
    - **vision**: a quick look at OCI's object & text detection ability and multiodal llama model 


1. oci commands to clean your files from object buckets 
   - oci os object bulk-delete -ns axaemuxiyife -bn workshopbucket --prefix AAGARWA/ --include ocid1\*
   - oci os object list --all --fields name,timeCreated --bucket-name=workshopbucket | grep AAGARWA
   - oci os object put -bn workshopbucket --prefix AAGARWA/ --file test.txt
