
## Welcome to the Vision Module.
In this module, we will experiment with the rich set of OCI AI Services that work with images.

Specifically, we will try the following capabilities:
1. Using OCI Vision for analyzing images: object (including text) detection & classification
2. Using OCI Document Understanding for OCR capability: classification of documents, and extraction of text, tables & key/value pairs
3. Using OCI Vision for analyzing video: object (including text) detection & classification
4. Using multimodel LLM (Llama 3.2) for working with images using LLM

Remember to set up your `sandbox.json` file per your environment. This module  uses the "oci" & "bucket" section

Example code in this module is available both as Jupyter notebook & Python code. They are very similar:
1. **oci_vision.py / vision.ipynb**: Upload image to object bucket & analyze it (classification, object/text/face detection)
2. **oci_vision_video.py / video.ipynb**: Upload video to object bucket & analyze it (object/text/face detection)
3. **oci_document_understanding.py / document_understanding.ipynb**: Upload a document to object bucket & analyze it (document/language classification, text, table, key/value extraction)


Here are some ideas of projects you can do (See notebook files for details):
- Create an api with a few parameters (eg: city & days ahead). try askig question and see if llm calls the api using right values 
    - Sample question: next week in seattle
    - Sample question:  weather tomm for capital of colorado
- Have a set of tools and provide Agents with subsut of those tools based on the classification 
    - eg: categories: billing, outage, rebates
    - tools: get biils, get account number for name,  outage for zipcode, zipcode of city, rebates for applicate, is appliance efficent


Here are few links to help you: 
- **#igiu-innovation-lab** for project ideas
- **#igiu-ai-learning**for issues with the code or environment 
- **#oci_ai_vis_service_users** for oci vision api questions 
- **#video-analysis-beta** for oci video  api questions 
- **#oci_ai_document_service_users** for oci document service  api questions 

https://docs.oracle.com/en-us/iaas/Content/vision/using/home.htm

