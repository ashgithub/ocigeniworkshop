
Welcome to the agents Module. In this module, we will experiment with the llms ability to call functions.  
Funtion calling ability is synonymous to using a tool. Agent can be given a set of tools and Agent can decomprose the problem and se the set of tools to solve it


In this module we will look at following ability
1. Single Step tool:  LLM invoking a single function/ using a single tool  
2. multi step tool : LLM orcestrating a sequence of function 

Following two are not directly reated to the tools/function but can help in your LLM/RAG pipeline: 
3. Clssification: using llm to classify a given text. This can be used to find the right set of tools to give the llm 
4. Semantic Cache: Ability to cache answers and retrieve it using semantic serach insted of key lookup

Note: 
1. OCI Gen AI only supports function calling for cohere models and not llama 
2. There are streaming and non streaming versions of code. Streaming version is fragile. 


As always, make sure your OCI client config & the compartment you are assigned to are correct:
    - Config file is assumed to be in ~/.oci/config. Change it if needed.
    - CONFIG_PROFILE: for the section on your local OCI config file that you configured for use with the sandbox
    - COMPARTMENT_ID: OCID of the compartment assigned to you

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:

1. single_step_demo.py, single_step_demo_streaming.py, singlestep_tool.ipynb : llm calling a function 
2. multi_step_demo.py, multi_step_demo_streaming.py, multistep_tool.ipynb : llm orcestration across multiple tools
3. llm_classification.py, classifiction.ipynb : classifying the given sentence
4. llm_semntic_cache.py, semantic_cache.ipynb : ability to cache answers and retrieve them basdd on a smilair questions


Here are some ideas of projects you can do (See notebook files for details):
    - Upload your video recoding from a zoom call, transcribe (Ai speech) & summarize it (Gen-AI)
    - try ranscription on different langaues, mixed langauges etc. Compafre oracle vs whisper models. 
    - Create a audio conversation between two people
        - Ask ai to generate the transcript (Gen AI)
        - use oci speech to convert reach dialog into audio, use different voice for each person
        - combine them into a single audio file

Here are few links to help you: 

#igiu-innovation-lab
#igiu-ai-learning
#generative-ai-users
