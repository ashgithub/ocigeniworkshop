
## Welcome to the agents Module.
In this module, we will experiment with the llms ability to call functions.  
Funtion calling ability is synonymous to using a tool. Agent can be given a set of tools and Agent can decomprose the problem and se the set of tools to solve it


In this module we will look at following abilities: 
1. Single Step tool:  LLM invoking a single function/ using a single tool  
2. Multi Step tool : LLM orcestrating a sequence of function 

Following two are not directly reated to the tools/function but can help in your LLM/RAG pipeline: 
3. Clssification: using llm to classify a given text. This can be used to find the right set of tools to give the llm 
4. Semantic Cache: Ability to cache answers and retrieve it using semantic serach insted of key lookup

Note: 
1. OCI Gen AI only supports function calling for cohere models and not llama 
2. There are streaming and non streaming versions of code. Streaming version is fragile. 

Oracle 23 ai databased is used in this module:refer to [this page](https://confluence.oraclecorp.com/confluence/display/D2OPS/AISandbox#AISandbox-ToAccessADW)
    - The database requires the wallet to be downlaoded. 
    - Remember to update the database section per your setup in `sandbox.json` 
    - As the database schmea is shared, set a unique `prefix` in teh datbase section of `sanbox.json`. Your Oralce user id is a good choice

Remember to set up your `sandbox.json` file per your environment. This module only uses the "oci" section 

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:
1. **single_step_demo.py, single_step_demo_streaming.py, singlestep_tool.ipynb**: llm calling a function 
2. **multi_step_demo.py, multi_step_demo_streaming.py, multistep_tool.ipynb** : llm orcestration across multiple tools
3. **llm_classification.py, classifiction.ipynb** : classifying the given sentence
4. **llm_semntic_cache.py, semantic_cache.ipynb** : ability to cache answers and retrieve them basdd on a smilair questions


Here are some ideas of projects you can do (See notebook files for details):
- Upload your video recoding from a zoom call, transcribe (Ai speech) & summarize it (Gen-AI)
- Try transcription on different languages, mixed languages etc. Compare Oracle vs whisper models. 
- Create a audio conversation between two people
   - Ask ai to generate the transcript (Gen AI)
   - Use oci speech to convert reach dialog into audio, use different voice for each person
   - Combine them into a single audio file

Here are few slack channels to help you: 

- **#igiu-ai-learning**  : if you have issues with environment or cant get this code working 
- **#igiu-innovation-lab** : discuss project ideas
- **#generative-ai-users** :  if you have questions about OCI GenAI  API  